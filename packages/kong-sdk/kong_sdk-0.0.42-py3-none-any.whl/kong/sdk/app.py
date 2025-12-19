import asyncio
import importlib.metadata
import json
import multiprocessing
import platform
import signal
import socket
from concurrent import futures
from contextlib import contextmanager

import grpc
from grpc_health.v1 import health_pb2
from grpc_reflection.v1alpha import reflection
from kong.common.app_logger import app_logger
from kong.proto import service_pb2
from kong.proto.service_pb2_grpc import add_GrpcBindingServicer_to_server
from kong.sdk.container import Container
from kong.sdk.grpc_binding import GrpcBinding
from kong.sdk.health_check import setup_health_check
from kong.sdk.kong_function import KongFunction
from pydantic import BaseModel

logger = app_logger(__name__)


def _create_and_run_server(address: str, threads: int):
    """Helper function to create and run server in a process"""

    async def _async_server():
        server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=threads),
            options=(("grpc.so_reuseport", 1),),
        )
        add_GrpcBindingServicer_to_server(GrpcBinding(), server)
        setup_health_check(server)

        service_names = (
            service_pb2.DESCRIPTOR.services_by_name["GrpcBinding"].full_name,
            health_pb2.DESCRIPTOR.services_by_name["Health"].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(service_names, server)

        server.add_insecure_port(address)

        logger.info(
            "start server",
            lambda: dict(
                address=address,
                pid=multiprocessing.current_process().pid,
                services=service_names,
                threads=threads,
            ),
        )

        await server.start()

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig, lambda x=server: asyncio.create_task(x.stop(5))
            )

        await server.wait_for_termination()

        logger.info(
            "server terminated",
            lambda: dict(
                address=address,
                pid=multiprocessing.current_process().pid,
                services=service_names,
                threads=threads,
            ),
        )

    asyncio.run(_async_server())


class App:
    def __init__(
        self,
        input_data_class: type[BaseModel],
        output_data_class: type[BaseModel],
        kong_function_class: type[KongFunction],
    ):
        logger.info(
            "init function",
            lambda: dict(sdkVersion=importlib.metadata.version("kong_sdk")),
        )

        self.__input_type = input_data_class
        self.__output_type = output_data_class
        self.__di = Container()
        self.__di.fn().set(
            kong_function_class(
                class_of_input_data=input_data_class,
            )
        )

    @contextmanager
    def _bind_port(self, port: int):
        """Context manager to bind port with SO_REUSEPORT"""

        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Check if SO_REUSEPORT is supported
        if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
            raise IOError(f"SO_REUSEPORT not supported on this system on port {port}")

        sock.bind(("", port))

        # Set backlog to enable port binding
        sock.listen(1)

        try:
            yield sock.getsockname()[1]
        finally:
            sock.close()

    def run(self, argv):
        if "--schema" in argv:
            self.print_model()
            return

        settings = self.__di.sdk_config()
        address = f"{settings.app.host}:{settings.app.port}"

        logger.info(
            "create workers",
            lambda: dict(
                address=address,
                workers=settings.app.workers,
                platform=platform.system(),
            ),
        )

        # Windows doesn't support SO_REUSEPORT properly, use different approach
        if platform.system() == "Windows" or settings.app.workers == 1:
            _create_and_run_server(address, settings.app.threads)
        else:
            # Unix-like systems with multiple workers
            workers: list[multiprocessing.Process] = []

            try:
                # Bind port first to ensure it's available
                with self._bind_port(settings.app.port):
                    for i in range(settings.app.workers):
                        worker = multiprocessing.Process(
                            target=_create_and_run_server,
                            args=(address, settings.app.threads),
                            name=f"app-worker-{i}",
                            daemon=True,
                        )
                        worker.start()
                        workers.append(worker)

                    # Wait for all workers to complete
                    for worker in workers:
                        worker.join()

            except Exception as ex:
                logger.error("unexpected problem", ex)
                for worker in workers:
                    if worker.is_alive():
                        worker.terminate()
                        worker.join(timeout=30)
                raise

    def print_model(self):
        schema = dict(
            input=self.__input_type.model_json_schema(),
            output=self.__output_type.model_json_schema(),
        )
        print(json.dumps(schema, indent=2))
