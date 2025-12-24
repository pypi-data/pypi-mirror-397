# type: ignore
import threading
import pytest
import http.server

from unittest.mock import MagicMock, Mock, patch
from pathlib import Path
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
from lseg_analytics_jupyterlab.src.handlers.proxyHandler import ProxyHandler
from lseg_analytics_jupyterlab.src.classes.proxyServer import ProxyServer
from lseg_analytics_jupyterlab.src.classes.enablementStatusService import (
    EnablementStatusService,
)


PORT_FILE = ".portInUse"
LSEG_DIRECTORY = ".lseg/VSCode"


@pytest.fixture
def enablement_status_service() -> EnablementStatusService:
    return EnablementStatusService()


@pytest.fixture
def proxy_server(enablement_status_service: EnablementStatusService) -> ProxyServer:
    proxy = ProxyServer(
        session_service=SessionService(settings={}),
        settings={"extension_version": "1.0.0"},
        enablement_status_service=enablement_status_service,
    )
    proxy.http_server = None
    proxy.server_thread = None
    proxy.proxy_port = None

    return proxy


def test_proxy_is_created_in_stopped_state(proxy_server):
    assert proxy_server.is_started == False
    assert proxy_server._session_service is not None


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._create_port_file"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.info")
@patch("lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler.set_lab_info")
def test_start_proxy_starts_if_not_running(
    mock_set_lab_info,
    mock_logger_info,
    mock_create_port_file,
    proxy_server,
):
    proxy_server.start([30100, 30111], "0.0.0.0", "9999", "aabb")

    assert proxy_server.server_thread is not None
    assert proxy_server.proxy_port is not None
    mock_set_lab_info.assert_called_once_with("0.0.0.0", "9999", "aabb")

    mock_create_port_file.assert_called_once()
    mock_logger_info.assert_called_once_with("Proxy Server started on port 30100")
    assert proxy_server.is_started == True


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._create_port_file"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.info")
@patch("lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler.set_lab_info")
def test_start_proxy_no_op_if_already_running(
    mock_set_lab_info,
    mock_logger_info,
    mock_create_port_file,
    proxy_server,
):
    # Mark the proxy as started
    proxy_server.is_started = True

    proxy_server.start([30100, 30111], "0.0.0.0", "9999", "aabb")

    mock_set_lab_info.assert_not_called()

    mock_create_port_file.assert_not_called()
    mock_logger_info.assert_not_called()
    assert proxy_server.is_started == True


@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.info")
@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._delete_port_file"
)
def test_stop_proxy_server(mock_delete_port_file, mock_logger_info, proxy_server):
    proxy_server.http_server = Mock(
        return_value=http.server.HTTPServer(("localhost", 2222), ProxyHandler)
    )

    proxy_server.server_thread = Mock(return_value=threading.Thread())
    mock_delete_port_file.return_value = ""

    proxy_server.stop()
    # assert

    mock_logger_info.assert_called_once_with("Proxy Server stopped")
    assert proxy_server.is_started == False


@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.warn")
def test_error_stop_proxy_server(mock_logger_warn, proxy_server, mocker):

    mocker.patch(
        "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer.server_thread",
        new=None,
    )
    proxy_server.stop()
    # assert

    mock_logger_warn.assert_called_once_with("Proxy Server is not running")
    assert proxy_server.is_started == False


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_port_file_path"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.info")
@patch("os.remove")
def test_delete_port_file(
    mock_os_remove, mock_info, mock_get_port_file_path, proxy_server
):
    file_path = Path("/mock/home") / LSEG_DIRECTORY / PORT_FILE
    mock_get_port_file_path.return_value = file_path
    proxy_server._delete_port_file()

    # assert
    mock_get_port_file_path.assert_called_once()
    mock_os_remove.assert_called_once_with(file_path)
    mock_info.assert_called_once()


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_port_file_path"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
@patch("os.remove")
def test_file_not_found_error_delete_port_file(
    mock_os_remove, mock_error, mock_get_port_file_path, proxy_server
):
    file_path = Path("/mock/home") / LSEG_DIRECTORY / PORT_FILE
    mock_get_port_file_path.return_value = file_path
    mock_os_remove.side_effect = FileNotFoundError()

    proxy_server._delete_port_file()

    # assert
    mock_get_port_file_path.assert_called_once()
    mock_error.assert_called_once_with(f"File '{file_path}' not found.")


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_port_file_path"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
@patch("os.remove")
def test_permission_error_delete_port_file(
    mock_os_remove, mock_error, mock_get_port_file_path, proxy_server
):
    file_path = Path("/mock/home") / LSEG_DIRECTORY / PORT_FILE
    mock_get_port_file_path.return_value = file_path
    mock_os_remove.side_effect = PermissionError()

    proxy_server._delete_port_file()

    # assert
    mock_get_port_file_path.assert_called_once()
    mock_error.assert_called_once_with(f"Permission denied: '{file_path}'")


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_port_file_path"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
@patch("os.remove")
def test_exception_delete_port_file(
    mock_os_remove, mock_error, mock_get_port_file_path, proxy_server
):
    file_path = Path("/mock/home") / LSEG_DIRECTORY / PORT_FILE
    mock_get_port_file_path.return_value = file_path
    mock_os_remove.side_effect = Exception("error")

    proxy_server._delete_port_file()

    # assert
    mock_get_port_file_path.assert_called_once()
    mock_error.assert_called_once_with(f"Error: error")


@patch("lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler.set_lab_info")
@patch("http.server.HTTPServer.serve_forever")
async def test_start_http_server(mock_serve_forever, mock_set_lab_info, proxy_server):
    proxy_server._start_http_server(1111, "0.0.0.0", "9999", "aabb")
    # assert
    mock_set_lab_info.assert_called_once_with("0.0.0.0", "9999", "aabb")
    mock_serve_forever.assert_called_once()


async def test_find_available_port(proxy_server):
    port = proxy_server._find_available_port(1112, 1113)
    assert port == 1112


def make_side_effect(map):
    def side_effect_func(args):
        return map[args[1]]

    return side_effect_func


@patch("socket.socket.connect_ex")
async def test_find_available_port_with_second_available_port(
    mock_connect_ex, proxy_server
):

    mock_connect_ex.side_effect = make_side_effect({1111: 0, 1112: 1, 1113: 1})

    port = proxy_server._find_available_port(1111, 1113)
    # first port is available
    assert port == 1112


@patch("socket.socket.connect_ex")
async def test_find_available_port_with_last_available_port(
    mock_connect_ex, proxy_server
):

    mock_connect_ex.side_effect = make_side_effect({1111: 0, 1112: 0, 1113: 1})

    port = proxy_server._find_available_port(1111, 1113)
    # assert last port is available
    assert port == 1113


@patch("socket.socket.connect_ex")
async def test_find_available_port_with_no_available_ports(
    mock_connect_ex, proxy_server, mocker
):
    with pytest.raises(
        RuntimeError,
        match="Unable to log on - no available ports in the range 1111-1113. Please free a port and try again.",
    ):
        mock_connect_ex.return_value = 0
        proxy_server._find_available_port(1111, 1113)


@patch("lseg_analytics_jupyterlab.src.classes.proxyServer.Path.home")
def test_get_lseg_directory_path(mock_home, proxy_server):
    mock_home.return_value = Path("/mock/home")
    expected_path = Path("/mock/home") / LSEG_DIRECTORY
    assert proxy_server._get_lseg_directory_path() == expected_path


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_lseg_directory_path"
)
def test_get_port_file_path(mock_get_lseg_directory_path, proxy_server):
    mock_get_lseg_directory_path.return_value = Path("/mock/home") / LSEG_DIRECTORY
    expected_path = Path("/mock/home") / LSEG_DIRECTORY / PORT_FILE
    assert proxy_server._get_port_file_path() == expected_path


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_port_file_path"
)
@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_lseg_directory_path"
)
def test_create_port_file(
    mock_get_lseg_directory_path, mock_get_port_file_path, proxy_server
):
    mock_lseg_directory_path = MagicMock(spec=Path)
    mock_port_file_path = MagicMock(spec=Path)

    mock_get_lseg_directory_path.return_value = mock_lseg_directory_path
    mock_get_port_file_path.return_value = mock_port_file_path

    proxy_server._create_port_file(8080)

    mock_lseg_directory_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_port_file_path.write_text.assert_called_once_with("8080")


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._find_available_port"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
def test_start_proxy_oserror(mock_logger_error, mock_find_available_port, proxy_server):
    mock_find_available_port.side_effect = OSError("Mocked OSError")

    with pytest.raises(OSError, match="Mocked OSError"):
        proxy_server.start([30100, 30111], "0.0.0.0", "9999", "aabb")

    mock_logger_error.assert_called_once_with("Socket error occurred: Mocked OSError")


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._find_available_port"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
def test_start_proxy_runtimeerror(
    mock_logger_error, mock_find_available_port, proxy_server
):
    mock_find_available_port.side_effect = RuntimeError("Mocked RuntimeError")

    with pytest.raises(RuntimeError, match="Mocked RuntimeError"):
        proxy_server.start([30100, 30111], "0.0.0.0", "9999", "aabb")

    mock_logger_error.assert_called_once_with(
        "Runtime error occurred: Mocked RuntimeError"
    )


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._find_available_port"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
def test_start_proxy_unexpected_error(
    mock_logger_error, mock_find_available_port, proxy_server
):
    mock_find_available_port.side_effect = Exception("Mocked Exception")

    with pytest.raises(Exception, match="Mocked Exception"):
        proxy_server.start([30100, 30111], "0.0.0.0", "9999", "aabb")

    mock_logger_error.assert_called_once_with(
        "An unexpected error occurred: Mocked Exception"
    )


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_lseg_directory_path"
)
@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_port_file_path"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
def test_create_port_file_oserror(
    mock_logger_error,
    mock_get_port_file_path,
    mock_get_lseg_directory_path,
    proxy_server,
):
    mock_lseg_directory_path = MagicMock(spec=Path)
    mock_port_file_path = MagicMock(spec=Path)

    mock_get_lseg_directory_path.return_value = mock_lseg_directory_path
    mock_get_port_file_path.return_value = mock_port_file_path

    mock_lseg_directory_path.mkdir.side_effect = OSError("Mocked OSError")

    with pytest.raises(OSError, match="Mocked OSError"):
        proxy_server._create_port_file(8080)

    mock_logger_error.assert_called_once_with(
        "File system error occurred: Mocked OSError"
    )


@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_lseg_directory_path"
)
@patch(
    "lseg_analytics_jupyterlab.src.classes.proxyServer.ProxyServer._get_port_file_path"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
def test_create_port_file_unexpected_error(
    mock_logger_error,
    mock_get_port_file_path,
    mock_get_lseg_directory_path,
    proxy_server,
):
    mock_lseg_directory_path = MagicMock(spec=Path)
    mock_port_file_path = MagicMock(spec=Path)

    mock_get_lseg_directory_path.return_value = mock_lseg_directory_path
    mock_get_port_file_path.return_value = mock_port_file_path

    mock_port_file_path.write_text.side_effect = Exception("Mocked Exception")

    with pytest.raises(Exception, match="Mocked Exception"):
        proxy_server._create_port_file(8080)

    mock_logger_error.assert_called_once_with(
        "An unexpected error occurred while creating port file: Mocked Exception"
    )


@patch("lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler.set_lab_info")
def test_update_proxy_server_data(mock_set_lab_info, proxy_server):
    # Call the method with test values
    proxy_server.update_proxy_server_data("test-host", "8888", "test-state")

    # Assert that the mocked method was called with the correct parameters
    mock_set_lab_info.assert_called_once_with("test-host", "8888", "test-state")
