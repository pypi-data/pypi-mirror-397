# type: ignore
from types import SimpleNamespace
from unittest.mock import Mock, call, patch, MagicMock
from lseg_analytics_jupyterlab.src.handlers.proxyHandler import (
    ProxyHandler,
    AUTHORIZATION_ERROR_MESSAGE,
)
from lseg_analytics_jupyterlab.src.tests.utils import MockRequest
from lseg_analytics_jupyterlab.src.utils.serverUtils import (
    ERROR_INVALID_STATE,
    ERROR_UNEXPECTED,
)
import pytest
import http
import io
import json
import requests
import time
from io import BytesIO as IO

byte_query = b"GET /auth?code=l3QTBjRihopke2GNfCTvdJUcgn_fjxqq8ccShM56&state="
mock_settings = {
    "extension_version": "0.1.0",
}


@pytest.fixture
def enablement_status_service():
    service = Mock()
    service.user_has_lfa_access.return_value = True
    return service


@pytest.fixture
@patch("lseg_analytics_jupyterlab.src.classes.sessionService.SessionService")
def session_service(mock_session_service):

    mock_session_service._session_service = Mock()

    # Create a proper session object
    session = Mock()
    session.access_token = "test_access_token"
    session.refresh_token = "test_refresh_token"
    # Set token to expire in 10 minutes (far enough to not trigger refresh)
    session.expiry_date_time_ms = str(int((time.time() + 600) * 1000))

    mock_session_service.set_session = Mock()
    mock_session_service.get_session.return_value = session

    return mock_session_service


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.info")
async def test_proxy_valid_state(
    mock_logger_info,
    mock_send_response,
    mock_server,
    session_service,
    enablement_status_service,
):

    mock_send_response.return_value = ""
    state = "aabb"

    ProxyHandler.set_lab_info("0.0.0.0", 8888, state)

    mock_request = MockRequest(byte_query + b"aabb")
    handler = ProxyHandler(
        session_service,
        mock_settings,
        enablement_status_service,
        mock_request,
        ("0.0.0.0", 8888),
        mock_server,
    )
    # assert
    assert handler._session_service is not None
    mock_send_response.assert_called_once_with(302)
    mock_logger_info.assert_has_calls(
        [call("The path is: /auth"), call("Redirecting to callback")]
    )


@pytest.mark.parametrize(
    "expected_state, query", [("aabb", byte_query), ("invalid", byte_query + b"aabb")]
)
@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch(
    "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket.send_message_to_client"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
async def test_proxy_null_state(
    mock_logger_error,
    mock_send_message_to_client,
    mock_send_response,
    mock_server,
    expected_state,
    query,
    session_service,
    enablement_status_service,
):

    mock_send_response.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, expected_state)

    mock_request = MockRequest(query)
    handler = ProxyHandler(
        session_service,
        mock_settings,
        enablement_status_service,
        mock_request,
        ("0.0.0.0", 8888),
        mock_server,
    )
    # assert
    # Check for the presence of the authentication error message in JSON format
    expected_error_json = f'{{"message_type": "AUTHENTICATION", "message": {{"content": "{ERROR_UNEXPECTED}", "log_level": "ERROR"}}}}'
    mock_send_message_to_client.assert_any_call(expected_error_json)
    mock_send_response.assert_called_once_with(500, ERROR_INVALID_STATE)
    mock_logger_error.assert_called_once_with(ERROR_UNEXPECTED)


async def test_set_lab():
    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")
    assert ProxyHandler.expected_state == "aabb"
    assert ProxyHandler.lab_host == "0.0.0.0"
    assert ProxyHandler.lab_port == 8888


async def test_set_lab_host_null():
    with pytest.raises(ValueError, match="Host cannot be null."):
        ProxyHandler.set_lab_info(None, 8888, "aabb")


async def test_set_lab_port_null():
    with pytest.raises(ValueError, match="Port cannot be null."):
        ProxyHandler.set_lab_info("0.0.0.0", None, "aabb")


async def test_set_lab_state_null():
    with pytest.raises(ValueError, match="State cannot be null."):
        ProxyHandler.set_lab_info("0.0.0.0", 8888, None)


@patch("lseg_analytics_jupyterlab.src.handlers.proxyHandler.logger_proxy.debug")
def test_handle_backend_request_logs_when_client_disconnects(mock_debug):
    handler = object.__new__(ProxyHandler)
    handler._session_service = MagicMock()
    handler._session_service.get_session.return_value = SimpleNamespace(
        access_token="token"
    )
    handler._enablement_status_service = MagicMock()
    handler._enablement_status_service.user_has_lfa_access.return_value = False
    handler._is_proxy_enabled = MagicMock(return_value=True)
    handler.settings = {"SDK_API": "https://example.com", "extension_version": "1.0"}
    handler.command = "GET"
    handler.path = "/financials/test"
    handler.headers = {"User-Agent": "pytest"}
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    handler.wfile = MagicMock()
    handler.wfile.write.side_effect = ConnectionResetError("boom")

    handler._handle_backend_request("financials")

    mock_debug.assert_any_call(
        "[Proxy] Client disconnected while sending authorization error: boom"
    )


class TestableProxyHandler(ProxyHandler):
    def __init__(
        self,
        session_service,
        settings,
        request,
        client_address,
        server,
        enablement_status_service=None,
    ):
        if enablement_status_service is None:
            enablement_status_service = Mock()
            enablement_status_service.user_has_lfa_access.return_value = True
        super().__init__(
            session_service,
            settings,
            enablement_status_service,
            request,
            client_address,
            server,
        )

    def handle_one_request(self):
        pass  # Override to prevent automatic handling


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=True,
)
async def test_handle_status_get(
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""
    mock_write.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"GET /status")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/status"
    handler.wfile = io.BytesIO()
    handler.do_GET()

    mock_send_response.assert_called_once_with(200)
    mock_send_header.assert_called_once_with("Content-type", "application/json")
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = handler.wfile.read()
    assert response == b'{"lsegProxyEnabled": true}'


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=True,
)
async def test_handle_backend_request_denies_unauthorized_user(
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
    enablement_status_service,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""
    mock_write.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"GET /financials/test")
    handler = TestableProxyHandler(
        session_service,
        mock_settings,
        mock_request,
        ("0.0.0.0", 8888),
        mock_server,
        enablement_status_service=enablement_status_service,
    )
    enablement_status_service.user_has_lfa_access.return_value = False
    handler.command = "GET"
    handler.path = "/financials/test"
    handler.wfile = io.BytesIO()

    handler._handle_backend_request("financials")

    mock_send_response.assert_called_once_with(403)
    mock_send_header.assert_called_once_with("Content-type", "application/json")
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = json.loads(handler.wfile.read().decode("utf-8"))
    assert response == {"error": AUTHORIZATION_ERROR_MESSAGE}


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=True,
)
@patch("requests.get")
async def test_handle_financials_get_error(
    mock_requests_get,
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""
    mock_write.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"GET /financials/test")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/financials/test"
    handler.settings = {"extension_version": "0.1.0"}
    handler.headers = {"User-Agent": "mock"}
    handler.command = "GET"
    handler.wfile = io.BytesIO()

    mock_requests_get.side_effect = requests.RequestException("Test error")

    handler.do_GET()

    mock_send_response.assert_called_once_with(500)
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = handler.wfile.read()
    assert b"Test error" in response


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=True,
)
@patch("requests.post")
async def test_handle_financials_post_error(
    mock_requests_post,
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""
    mock_write.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    post_data = json.dumps({"key": "value"}).encode("utf-8")
    request_line = (
        b"POST /financials/test HTTP/1.1\r\nContent-Length: "
        + str(len(post_data)).encode()
        + b"\r\n\r\n"
    )
    mock_request = MockRequest(request_line + post_data)
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/financials/test"
    handler.settings = {"extension_version": "0.1.0"}
    handler.command = "POST"
    handler.headers = {"Content-Length": len(post_data)}
    handler.rfile = IO(post_data)
    handler.wfile = IO()

    mock_requests_post.side_effect = requests.RequestException("Test error")

    handler.do_POST()

    mock_send_response.assert_called_once_with(500)
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = handler.wfile.read()
    assert b"Test error" in response
    headers = mock_requests_post.call_args[1]["headers"]
    assert "User-Agent" in headers
    assert "x-lseg-client-requestid" in headers
    # no User-Agent in header
    assert headers["User-Agent"] == "lseg-ide-jupyter/v0.1.0 for unknown"
    assert headers["x-lseg-client-requestid"] is not None


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
async def test_do_get_invalid_path(
    mock_end_headers, mock_send_response, mock_server, session_service
):
    mock_send_response.return_value = ""
    mock_end_headers.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"GET /invalid_path")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/invalid_path"
    handler.command = "GET"
    handler.wfile = io.BytesIO()

    handler.do_GET()

    mock_send_response.assert_called_once_with(404)
    mock_end_headers.assert_called_once()


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
async def test_do_post_invalid_path(
    mock_end_headers, mock_send_response, mock_server, session_service
):
    mock_send_response.return_value = ""
    mock_end_headers.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    post_data = json.dumps({"key": "value"}).encode("utf-8")
    request_line = (
        b"POST /invalid_path HTTP/1.1\r\nContent-Length: "
        + str(len(post_data)).encode()
        + b"\r\n\r\n"
    )
    mock_request = MockRequest(request_line + post_data)
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/invalid_path"
    handler.command = "POST"
    handler.headers = {"Content-Length": len(post_data)}
    handler.rfile = IO(post_data)
    handler.wfile = IO()

    handler.do_POST()

    mock_send_response.assert_called_once_with(404)
    mock_end_headers.assert_called_once()


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(ProxyHandler, "handle_yieldbook")
async def test_do_get_yieldbook_routes_to_handler(
    mock_handle_yieldbook,
    mock_end_headers,
    mock_send_response,
    mock_server,
    session_service,
):
    """should call handle_yieldbook when path startswith /yieldbook from do_get"""
    mock_send_response.return_value = ""
    mock_end_headers.return_value = ""
    mock_handle_yieldbook.return_value = None

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"GET /yieldbook/test")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/yieldbook/test"
    handler.command = "GET"

    handler.do_GET()

    mock_handle_yieldbook.assert_called_once()


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(ProxyHandler, "handle_yieldbook")
async def test_handle_request_yieldbook_routes_to_handler(
    mock_handle_yieldbook,
    mock_end_headers,
    mock_send_response,
    mock_server,
    session_service,
):
    """should call handle_yieldbook from handle_request if path starts with yieldbook"""
    mock_send_response.return_value = ""
    mock_end_headers.return_value = ""
    mock_handle_yieldbook.return_value = None

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"POST /yieldbook/test")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/yieldbook/test"
    handler.command = "POST"

    handler.handle_request()

    mock_handle_yieldbook.assert_called_once()


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.warn")
async def test_handle_proxy_bad_request(
    mock_logger_warn, mock_end_headers, mock_send_response, mock_server, session_service
):
    mock_send_response.return_value = ""
    mock_end_headers.return_value = ""
    mock_logger_warn.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"GET /auth?state=aabb")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/auth?state=aabb"
    handler.command = "GET"
    handler.wfile = io.BytesIO()

    handler.handle_proxy()

    mock_logger_warn.assert_called_once_with("Bad request")
    mock_send_response.assert_called_once_with(400)
    mock_end_headers.assert_called_once()


@pytest.mark.parametrize("method", ["POST", "PUT", "GET"])
@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=True,
)
@patch("requests.put")
@patch("requests.post")
@patch("requests.get")
async def test_handle_financials(
    mock_requests_get,
    mock_requests_post,
    mock_requests_put,
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
    method,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""
    mock_write.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    data = json.dumps({"key": "value"}).encode("utf-8")
    request_line = (
        (
            f"{method} /financials/test HTTP/1.1\r\nContent-Length: "
            + str(len(data))
            + "\r\n\r\n"
        ).encode("utf-8")
        if method != "GET"
        else f"{method} /financials/test HTTP/1.1\r\n\r\n".encode("utf-8")
    )
    mock_request = MockRequest(request_line + data if method != "GET" else request_line)
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/financials/test"
    handler.settings = {"extension_version": "0.1.0"}
    handler.command = method
    handler.headers = (
        {"Content-Length": len(data), "User-Agent": "test-agent"}
        if method != "GET"
        else {"User-Agent": "test-agent"}
    )
    handler.rfile = IO(data) if method != "GET" else IO()
    handler.wfile = IO()

    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"data": "test"}'
    if method == "PUT":
        mock_requests_put.return_value = mock_response
        handler.do_PUT()
    elif method == "POST":
        mock_requests_post.return_value = mock_response
        handler.do_POST()
    elif method == "GET":
        mock_requests_get.return_value = mock_response
        handler.do_GET()

    mock_send_response.assert_called_once_with(200)
    mock_send_header.assert_called_once_with("Content-type", "application/json")
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = handler.wfile.read()
    assert response == b'{"data": "test"}'
    if method == "PUT":
        headers = mock_requests_put.call_args[1]["headers"]
    elif method == "POST":
        headers = mock_requests_post.call_args[1]["headers"]
    elif method == "GET":
        headers = mock_requests_get.call_args[1]["headers"]
    assert "User-Agent" in headers
    assert "x-lseg-client-requestid" in headers
    assert headers["User-Agent"] == "lseg-ide-jupyter/v0.1.0 for test-agent"
    assert headers["x-lseg-client-requestid"] is not None


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=True,
)
@patch("requests.delete")
async def test_handle_financials_delete(
    mock_requests_delete,
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""
    mock_write.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    data = json.dumps({"key": "value"}).encode("utf-8")
    request_line = (
        "DELETE /financials/test HTTP/1.1\r\nContent-Length: "
        + str(len(data))
        + "\r\n\r\n"
    ).encode("utf-8")
    mock_request = MockRequest(request_line + data)
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/financials/test"
    handler.settings = {"extension_version": "0.1.0"}
    handler.command = "DELETE"
    handler.headers = {"Content-Length": len(data), "User-Agent": "test-agent"}
    handler.rfile = IO(data)
    handler.wfile = IO()

    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"data": "test"}'
    mock_requests_delete.return_value = mock_response

    handler.do_DELETE()

    mock_send_response.assert_called_once_with(200)
    mock_send_header.assert_called_once_with("Content-type", "application/json")
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = handler.wfile.read()
    assert response == b'{"data": "test"}'
    headers = mock_requests_delete.call_args[1]["headers"]
    assert "User-Agent" in headers
    assert "x-lseg-client-requestid" in headers
    assert headers["User-Agent"] == "lseg-ide-jupyter/v0.1.0 for test-agent"
    assert headers["x-lseg-client-requestid"] is not None


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=True,
)
@patch("requests.put")
async def test_handle_financials_put_error(
    mock_requests_put,
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""
    mock_write.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    data = json.dumps({"key": "value"}).encode("utf-8")
    request_line = (
        "PUT /financials/test HTTP/1.1\r\nContent-Length: "
        + str(len(data))
        + "\r\n\r\n"
    ).encode("utf-8")
    mock_request = MockRequest(request_line + data)
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/financials/test"
    handler.settings = {"extension_version": "0.1.0"}
    handler.command = "PUT"
    handler.headers = {"Content-Length": len(data), "User-Agent": "test-agent"}
    handler.rfile = IO(data)
    handler.wfile = IO()

    mock_response = requests.Response()
    mock_response.status_code = 500
    mock_response._content = b'{"error": "test error"}'
    mock_requests_put.return_value = mock_response

    handler.do_PUT()

    mock_send_response.assert_called_once_with(500)
    mock_send_header.assert_called_once_with("Content-type", "application/json")
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = handler.wfile.read()
    assert response == b'{"error": "test error"}'
    headers = mock_requests_put.call_args[1]["headers"]
    assert "User-Agent" in headers
    assert "x-lseg-client-requestid" in headers
    assert headers["User-Agent"] == "lseg-ide-jupyter/v0.1.0 for test-agent"
    assert headers["x-lseg-client-requestid"] is not None


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=True,
)
@patch("requests.delete")
async def test_handle_financials_delete_error(
    mock_requests_delete,
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""
    mock_write.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    data = json.dumps({"key": "value"}).encode("utf-8")
    request_line = (
        "DELETE /financials/test HTTP/1.1\r\nContent-Length: "
        + str(len(data))
        + "\r\n\r\n"
    ).encode("utf-8")
    mock_request = MockRequest(request_line + data)
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/financials/test"
    handler.settings = {"extension_version": "0.1.0"}
    handler.command = "DELETE"
    handler.headers = {"Content-Length": len(data), "User-Agent": "test-agent"}
    handler.rfile = IO(data)
    handler.wfile = IO()

    mock_response = requests.Response()
    mock_response.status_code = 500
    mock_response._content = b'{"error": "test error"}'
    mock_requests_delete.return_value = mock_response

    handler.do_DELETE()

    mock_send_response.assert_called_once_with(500)
    mock_send_header.assert_called_once_with("Content-type", "application/json")
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = handler.wfile.read()
    assert response == b'{"error": "test error"}'
    headers = mock_requests_delete.call_args[1]["headers"]
    assert "User-Agent" in headers
    assert "x-lseg-client-requestid" in headers
    assert headers["User-Agent"] == "lseg-ide-jupyter/v0.1.0 for test-agent"
    assert headers["x-lseg-client-requestid"] is not None


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
async def test_callback_url_protocol_agnostic(
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
    enablement_status_service,
):
    ProxyHandler.set_lab_info("localhost", 8888, "test_state")

    mock_request = MockRequest(b"GET /auth?code=test_code&state=test_state")
    handler = ProxyHandler(
        session_service,
        mock_settings,
        enablement_status_service,
        mock_request,
        ("0.0.0.0", 8888),
        mock_server,
    )
    handler.path = "/auth?code=test_code&state=test_state"
    handler.command = "GET"
    handler.wfile = io.BytesIO()
    mock_send_response.assert_called_once_with(302)
    mock_send_header.assert_called_once_with(
        "Location",
        "//localhost:8888/api/lseg-analytics-jupyterlab/callback/?code=test_code",
    )
    mock_end_headers.assert_called_once()


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=True,
)
async def test_handle_financials_no_session(
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""
    session_service.get_session.return_value = None

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"GET /financials/test")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/financials/test"
    handler.command = "GET"
    handler.headers = {"User-Agent": "test-agent"}
    handler.wfile = io.BytesIO()

    handler.handle_financials()
    mock_send_response.assert_called_once_with(401)
    mock_send_header.assert_called_once_with("Content-type", "application/json")
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = handler.wfile.read()
    assert b'"error": "No active session found or token refresh failed"' in response


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=False,
)
async def test_handle_financials_disabled(
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"GET /financials/test")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/financials/test"
    handler.command = "GET"
    handler.headers = {"User-Agent": "test-agent"}
    handler.wfile = io.BytesIO()

    handler.handle_financials()
    mock_send_response.assert_called_once_with(400)
    mock_send_header.assert_called_once_with("Content-type", "application/json")
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = handler.wfile.read()
    assert b'"error": "Proxy is disabled in user settings"' in response


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.send_header")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
@patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
@patch(
    "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
    return_value=True,
)
async def test_handle_financials_method_not_allowed(
    mock_is_enabled,
    mock_write,
    mock_end_headers,
    mock_send_header,
    mock_send_response,
    mock_server,
    session_service,
):
    mock_send_response.return_value = ""
    mock_send_header.return_value = ""
    mock_end_headers.return_value = ""

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"PATCH /financials/test")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/financials/test"
    handler.settings = {"extension_version": "0.1.0"}
    handler.command = "PATCH"

    handler.headers = {"User-Agent": "test-agent"}
    handler.wfile = io.BytesIO()
    handler.handle_financials()
    # Verifing 405 response was sent
    mock_send_response.assert_called_once_with(405)
    mock_send_header.assert_called_once_with("Content-type", "application/json")
    mock_end_headers.assert_called_once()
    handler.wfile.seek(0)
    response = handler.wfile.read()
    assert b'"error": "Method not allowed"' in response


@pytest.mark.parametrize(
    "file_content, expected",
    [
        ('{"enableAutomaticAuthentication": true}', True),
        ('{"enableAutomaticAuthentication": false}', False),
        (None, False),  # missing file
        ("{", False),  # invalid JSON
    ],
)
@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch("http.server.BaseHTTPRequestHandler.end_headers")
def test_is_proxy_enabled_variants(
    mock_end_headers,
    mock_send_response,
    mock_server,
    session_service,
    tmp_path,
    file_content,
    expected,
):
    # Arrange: build settings dir structure
    user_settings_dir = tmp_path
    lseg_dir = user_settings_dir / "lseg-analytics-jupyterlab"
    lseg_dir.mkdir(parents=True, exist_ok=True)

    settings = {
        "extension_version": "0.1.0",
        "user_settings_dir": str(user_settings_dir),
    }

    # Only write file if content provided
    settings_file = lseg_dir / "plugin.jupyterlab-settings"
    if file_content is not None:
        settings_file.write_text(file_content, encoding="utf-8")

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "state")
    mock_request = MockRequest(b"GET /status")
    handler = TestableProxyHandler(
        session_service, settings, mock_request, ("0.0.0.0", 8888), mock_server
    )

    # Act
    result = handler._is_proxy_enabled()

    # Assert
    assert result is expected


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch.object(ProxyHandler, "_handle_backend_request")
async def test_handle_yieldbook_calls_backend(
    mock_backend_request, mock_send_response, mock_server, session_service
):
    """_handle_backend_request should be called with 'yieldbook' when handle_yieldbook is invoked"""
    mock_send_response.return_value = ""
    mock_backend_request.return_value = None

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"GET /yieldbook/test")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/yieldbook/test"
    handler.command = "GET"
    handler.settings = {"extension_version": "0.1.0", "SDK_API": "https://api"}

    handler.handle_yieldbook()

    mock_backend_request.assert_called_once_with("yieldbook")


@patch("socketserver.BaseServer")
@patch("http.server.BaseHTTPRequestHandler.send_response")
@patch.object(ProxyHandler, "_handle_backend_request")
async def test_handle_financials_calls_backend(
    mock_backend_request, mock_send_response, mock_server, session_service
):
    """_handle_backend_request should be called with 'financials' when handle_financials is invoked"""

    mock_send_response.return_value = ""
    mock_backend_request.return_value = None

    ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

    mock_request = MockRequest(b"GET /financials/test")
    handler = TestableProxyHandler(
        session_service, mock_settings, mock_request, ("0.0.0.0", 8888), mock_server
    )
    handler.path = "/financials/test"
    handler.command = "GET"
    handler.settings = {"extension_version": "0.1.0", "SDK_API": "https://api"}

    handler.handle_financials()

    mock_backend_request.assert_called_once_with("financials")


class TestProxyHandlerSessionService:
    """Test cases for ProxyHandler with SessionService-based token management."""

    @pytest.fixture
    def mock_session_with_valid_token(self):
        """Fixture for a mock user session with valid token."""
        session = Mock()
        session.access_token = "valid-access-token"
        session.refresh_token = "valid-refresh-token"
        session.expiry_date_time_ms = str(int(time.time() + 3600))  # Expires in 1 hour
        return session

    @pytest.fixture
    def mock_session_service_auto_refresh(self, mock_session_with_valid_token):
        """Session service that handles token refresh automatically."""
        service = Mock()
        service.get_session.return_value = mock_session_with_valid_token
        return service

    @pytest.fixture
    def mock_session_service_refresh_failed(self):
        """Session service where token refresh fails."""
        service = Mock()
        service.get_session.return_value = None
        return service

    @pytest.fixture
    def proxy_settings(self):
        """Fixture for proxy handler settings."""
        return {
            "extension_version": "0.1.0",
            "SDK_API": "https://api.example.com",
            "TOKEN_URL": "https://auth.example.com/token",
            "CLIENT_ID": "test-client-id",
            "user_settings_dir": "/tmp/test_settings",
        }

    @patch("socketserver.BaseServer")
    @patch("http.server.BaseHTTPRequestHandler.send_response")
    @patch("http.server.BaseHTTPRequestHandler.send_header")
    @patch("http.server.BaseHTTPRequestHandler.end_headers")
    @patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
    @patch(
        "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
        return_value=True,
    )
    @patch("requests.get")
    def test_handle_financials_with_session_auto_refresh(
        self,
        mock_requests_get,
        mock_is_enabled,
        mock_write,
        mock_end_headers,
        mock_send_header,
        mock_send_response,
        mock_server,
        mock_session_service_auto_refresh,
        proxy_settings,
    ):
        """Test handle_financials where SessionService handles token refresh automatically."""
        # Setup mocks
        mock_send_response.return_value = ""
        mock_send_header.return_value = ""
        mock_end_headers.return_value = ""

        # Mock successful API response
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.content = b'{"data": "test_data"}'
        mock_requests_get.return_value = mock_api_response

        ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

        # Create handler
        mock_request = MockRequest(b"GET /financials/test")
        handler = TestableProxyHandler(
            mock_session_service_auto_refresh,
            proxy_settings,
            mock_request,
            ("0.0.0.0", 8888),
            mock_server,
        )
        handler.path = "/financials/test"
        handler.command = "GET"
        handler.headers = {"User-Agent": "test-agent"}
        handler.wfile = io.BytesIO()

        # Execute
        handler.handle_financials()

        # Verify successful response (SessionService handled refresh automatically)
        mock_send_response.assert_called_once_with(200)
        mock_requests_get.assert_called_once()

        # Verify session was retrieved (automatic refresh handled by SessionService)
        mock_session_service_auto_refresh.get_session.assert_called()

    @patch("socketserver.BaseServer")
    @patch("http.server.BaseHTTPRequestHandler.send_response")
    @patch("http.server.BaseHTTPRequestHandler.send_header")
    @patch("http.server.BaseHTTPRequestHandler.end_headers")
    @patch.object(http.server.BaseHTTPRequestHandler, "wfile", create=True)
    @patch(
        "lseg_analytics_jupyterlab.src.handlers.proxyHandler.ProxyHandler._is_proxy_enabled",
        return_value=True,
    )
    def test_handle_financials_session_refresh_failed(
        self,
        mock_is_enabled,
        mock_write,
        mock_end_headers,
        mock_send_header,
        mock_send_response,
        mock_server,
        mock_session_service_refresh_failed,
        proxy_settings,
    ):
        """Test handle_financials when SessionService token refresh fails."""
        # Setup mocks
        mock_send_response.return_value = ""
        mock_send_header.return_value = ""
        mock_end_headers.return_value = ""

        ProxyHandler.set_lab_info("0.0.0.0", 8888, "aabb")

        # Create handler
        mock_request = MockRequest(b"GET /financials/test")
        handler = TestableProxyHandler(
            mock_session_service_refresh_failed,
            proxy_settings,
            mock_request,
            ("0.0.0.0", 8888),
            mock_server,
        )
        handler.path = "/financials/test"
        handler.command = "GET"
        handler.headers = {"User-Agent": "test-agent"}
        handler.wfile = io.BytesIO()

        # Execute
        handler.handle_financials()

        # Verify 401 response was sent (no session available after refresh attempt)
        mock_send_response.assert_called_once_with(401)
        mock_send_header.assert_called_once_with("Content-type", "application/json")
        mock_end_headers.assert_called_once()

        # Verify error message
        handler.wfile.seek(0)
        response = handler.wfile.read()
        assert b'"error": "No active session found or token refresh failed"' in response
