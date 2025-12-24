import http.server
import os
import socket
from threading import Thread
from typing import Optional, Any, List
from lseg_analytics_jupyterlab.src.classes.loggers import logger_proxy
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
from lseg_analytics_jupyterlab.src.handlers.proxyHandler import ProxyHandler
from lseg_analytics_jupyterlab.src.classes.enablementStatusService import (
    EnablementStatusService,
)
from pathlib import Path
import uuid

PROXY_SERVER_HOST = "127.0.0.1"
PORT_FILE = ".portInUse"
LSEG_DIRECTORY = ".lseg/VSCode"

# Constant for port unavailable error message
PORT_UNAVAILABLE_ERROR_MSG_TEMPLATE = "Unable to log on - no available ports in the range {start_port}-{end_port}. Please free a port and try again."


class ProxyServer:
    http_server: Optional[http.server.HTTPServer] = None
    server_thread: Optional[Thread] = None
    proxy_port: Optional[int] = None

    is_started: bool = False

    def __init__(
        self,
        session_service: SessionService,
        settings: Any,
        enablement_status_service: EnablementStatusService,
    ) -> None:
        assert session_service is not None
        assert enablement_status_service is not None
        self._session_service = session_service
        self.settings = settings
        self._enablement_status_service = enablement_status_service
        logger_proxy.info("Proxy Server initialised")

    def update_proxy_server_data(
        self, lab_host: str, lab_port: str, state: uuid.UUID
    ) -> None:
        ProxyHandler.set_lab_info(lab_host, lab_port, state)

    def start(
        self, port_range: List[int], lab_host: str, lab_port: str, state: uuid.UUID
    ) -> None:

        if self.is_started:
            logger_proxy.debug("[Proxy] proxy is already started")
            return

        try:
            self.proxy_port = self._find_available_port(port_range[0], port_range[1])
            thread = Thread(
                target=self._start_http_server,
                args=[self.proxy_port, lab_host, lab_port, state],
                daemon=True,
            )
            thread.start()
            self.server_thread = thread

            logger_proxy.info(
                "Proxy Server started on port {port}".format(port=self.proxy_port)
            )

        except OSError as e:
            logger_proxy.error(f"Socket error occurred: {e}")
            raise
        except RuntimeError as e:
            logger_proxy.error(f"Runtime error occurred: {e}")
            raise
        except Exception as e:
            logger_proxy.error(f"An unexpected error occurred: {e}")
            raise

        # create port file after the server is started
        self._create_port_file(self.proxy_port)

        self.is_started = True

    def stop(self) -> None:

        if self.server_thread is not None:
            if self.http_server is not None:
                self.http_server.shutdown()
            self.server_thread.join()
            # clear all server variables
            self.server_thread = None
            self.http_server = None
            self.proxy_port = None
            ##Delete port file
            self._delete_port_file()

            logger_proxy.info("Proxy Server stopped")
        else:
            logger_proxy.warn("Proxy Server is not running")

        self.is_started = False

    def _start_http_server(
        self, port: int, lab_host: str, lab_port: str, state: Any
    ) -> None:
        """
        Starts an HTTP server on the specified port.

        This function initializes and starts an HTTP server using the specified port,
        lab host, and lab port. The server uses the ProxyHandler to handle incoming requests.

        Parameters:
        port (int): The port number on which the server will listen.
        lab_host (str): The host address of the lab server.
        lab_port (int): The port number of the lab server.
        """
        hostname = PROXY_SERVER_HOST
        ProxyHandler.set_lab_info(lab_host, lab_port, state)
        session_service = self._session_service
        settings = self.settings
        enablement_status_service = self._enablement_status_service

        class CustomProxyHandler(ProxyHandler):
            def __init__(self, *args: Any, **kwargs: Any):
                super().__init__(
                    session_service,
                    settings,
                    enablement_status_service,
                    *args,
                    **kwargs,
                )

        httpd = http.server.HTTPServer(
            (hostname, port),
            CustomProxyHandler,
        )
        self.http_server = httpd
        httpd.serve_forever()

    def _find_available_port(self, start_port: int, end_port: int) -> int:
        """
         Finds an available port within a specified range.

        This function iterates over a range of ports from `start_port` to `end_port`
        and returns the first port that is available for use. If no ports are available within
        the specified range, it raises a RuntimeError.

        Parameters:
        start_port (int): The starting port number of the range to check.
        end_port (int): The ending port number of the range to check.

        Returns:
         int: The first available port number within the specified range.

        Raises:
         RuntimeError: If no available ports are found within the specified range.
        """
        for port in range(start_port, end_port + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex((PROXY_SERVER_HOST, port)) != 0:
                    return port
        raise RuntimeError(
            PORT_UNAVAILABLE_ERROR_MSG_TEMPLATE.format(
                start_port=start_port, end_port=end_port
            )
        )

    def _get_lseg_directory_path(self) -> Path:
        user_directory = Path.home()
        return user_directory / LSEG_DIRECTORY

    def _get_port_file_path(self) -> Path:
        return self._get_lseg_directory_path() / PORT_FILE

    def _create_port_file(self, port: int) -> None:
        try:
            self._get_lseg_directory_path().mkdir(parents=True, exist_ok=True)
            self._get_port_file_path().write_text(str(port))
            logger_proxy.info(
                "Created .portInUse file with port: {port}".format(port=port)
            )
        except OSError as e:
            logger_proxy.error(f"File system error occurred: {e}")
            raise
        except Exception as e:
            logger_proxy.error(
                f"An unexpected error occurred while creating port file: {e}"
            )
            raise

    def _delete_port_file(self) -> None:
        port_file_path = self._get_port_file_path()
        try:
            os.remove(port_file_path)
            logger_proxy.info(f"File '{port_file_path}' deleted successfully.")
        except FileNotFoundError:
            logger_proxy.error(f"File '{port_file_path}' not found.")
        except PermissionError:
            logger_proxy.error(f"Permission denied: '{port_file_path}'")
        except Exception as e:
            logger_proxy.error(f"Error: {e}")
