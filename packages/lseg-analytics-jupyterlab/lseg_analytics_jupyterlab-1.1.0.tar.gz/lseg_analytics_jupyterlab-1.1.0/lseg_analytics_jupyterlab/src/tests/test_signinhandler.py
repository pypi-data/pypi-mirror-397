# type: ignore
import pytest
from unittest.mock import Mock, patch
from urllib.parse import urlencode
from tornado.web import Application
from lseg_analytics_jupyterlab.src.classes.proxyServer import ProxyServer
from lseg_analytics_jupyterlab.src.handlers.signinHandler import (
    SignInHandler,
    generate_code_challenge,
    generate_state,
)

mock_proxy_server = Mock()


@pytest.fixture
def sign_in_handler():
    mock_proxy_server.reset_mock()  # module-level so needs to be reset for each test

    application = Application()
    mock_http_request = Mock()
    mock_http_request.host = "127.0.0.1:1111"

    # Any customer parameters passed to the "initialize" method must be passed
    # as named arguments here
    handler = SignInHandler(
        application, mock_http_request, proxy_server=mock_proxy_server
    )
    handler.settings["port_range"] = {"start": 60100, "end": 60110}
    handler.settings["proxy_server_host"] = "http://127.0.0.1"
    handler.settings["CLIENT_ID"] = "afd238de-256f-4956-9e39-b31bab87b837"
    handler.settings["BASE_URL"] = "https://login.stage.ciam.refinitiv.com"
    return handler


@patch("tornado.web.RequestHandler.finish")
@patch("lseg_analytics_jupyterlab.src.handlers.signinHandler.generate_state")
@patch("lseg_analytics_jupyterlab.src.handlers.signinHandler.generate_code_challenge")
@patch(
    "lseg_analytics_jupyterlab.src.handlers.signinHandler.fetch_openid_configuration"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.info")
async def test_sign_in_handler(
    mock_logger_info,
    mock_fetch_openid_configuration,
    mock_generate_code_challenge,
    mock_generate_state,
    mock_finish,
    sign_in_handler,
):
    mock_fetch_openid_configuration.return_value = {
        "authorization_endpoint": "sample_auth_endpoint",
        "token_endpoint": "sample_token_endpoint",
    }
    mock_generate_code_challenge.return_value = "xxyy"
    mock_generate_state.return_value = "aabb"

    # Begin with the proxy server in the "stopped" state
    mock_proxy_server.is_started = False

    def start_side_effect(*args, **kwargs):
        mock_proxy_server.proxy_port = 60100

    mock_proxy_server.start.side_effect = start_side_effect

    sign_in_handler.get()
    # assert
    mock_proxy_server.start.assert_called_once_with(
        [60100, 60110], "127.0.0.1", "1111", "aabb"
    )

    mock_proxy_server.update_proxy_server_data.assert_not_called()

    params = {
        "response_type": "code",
        "client_id": sign_in_handler.settings["CLIENT_ID"],
        "redirect_uri": f'{sign_in_handler.settings["proxy_server_host"]}:{60100}/auth',
        "code_challenge": mock_generate_code_challenge(),
        "code_challenge_method": "S256",
        "state": mock_generate_state(),
        "scope": "openid profile trapi lfa trapi.platform.iam.acl_service trapi.data.quantitative-analytics.read",
        "response_mode": "query",
    }
    expected_auth_url = f"{mock_fetch_openid_configuration()['authorization_endpoint']}?{urlencode(params)}"
    # Verify JSON response is returned instead of redirect
    expected_response = {
        "status": "success",
        "message": "auth_url",
        "data": {"url": expected_auth_url, "port": 60100},
        "error": None,
    }
    import json

    mock_finish.assert_called_once_with(json.dumps(expected_response))

    assert sign_in_handler.settings["redirect_uri"].endswith("/auth")
    mock_logger_info.assert_called_once_with("Returning authentication URL to client")

    mock_proxy_server.stop.assert_not_called()


@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
@patch("tornado.web.RequestHandler.finish")
async def test_error_proxy_server_start(
    mock_finish, mock_logger_error, sign_in_handler
):
    # Begin with the proxy server in the "stopped" state
    mock_proxy_server.is_started = False
    mock_proxy_server.start.side_effect = Exception("error")

    sign_in_handler.get()

    error_msg = '{"status": "error", "message": "proxy_server_error", "data": null, "error": "error"}'
    mock_finish.assert_called_once_with(error_msg)
    mock_logger_error.assert_called_once_with("Error starting proxy server")
    mock_proxy_server.stop.assert_not_called()


@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
@patch("tornado.web.RequestHandler.finish")
async def test_port_unavailable_error(mock_finish, mock_logger_error, sign_in_handler):
    # Begin with the proxy server in the "stopped" state
    mock_proxy_server.is_started = False
    # Simulate the specific port unavailable error message
    port_error_msg = "Unable to log on - no available ports in the range 60100-60110. Please free a port and try again."
    mock_proxy_server.start.side_effect = Exception(port_error_msg)

    sign_in_handler.get()

    expected_error_response = (
        '{"status": "error", "message": "port_unavailable", "data": null, "error": "'
        + port_error_msg
        + '"}'
    )
    mock_finish.assert_called_once_with(expected_error_response)
    mock_logger_error.assert_called_once_with("Error starting proxy server")
    mock_proxy_server.stop.assert_not_called()


@patch("tornado.web.RequestHandler.finish")
async def test_proxy_server_started_if_not_running(mock_finish, sign_in_handler):
    # Begin with the proxy server in the "stopped" state
    mock_proxy_server.is_started = False
    mock_finish.return_value = ""

    sign_in_handler.get()

    mock_proxy_server.start.assert_called_once()


@patch("tornado.web.RequestHandler.finish")
async def test_proxy_server_not_started_if_already_running(
    mock_finish, sign_in_handler
):
    # Begin with the proxy server in the "started" state
    mock_proxy_server.is_started = True
    mock_finish.return_value = ""

    sign_in_handler.get()

    mock_proxy_server.start.assert_not_called()


@patch(
    "lseg_analytics_jupyterlab.src.handlers.signinHandler.fetch_openid_configuration"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
@patch("tornado.web.RequestHandler.finish")
async def test_error_fetch_open_id_configuration(
    mock_finish, mock_logger_error, mock_fetch_open_id_configuration, sign_in_handler
):
    error_msg = '{"status": "error", "message": "Error fetching OpenID configuration", "data": null, "error": "error"}'
    mock_fetch_open_id_configuration.side_effect = Exception("error")
    sign_in_handler.get()

    mock_finish.assert_called_once_with(error_msg)
    mock_logger_error.assert_called_once_with("Error fetching OpenID configuration")


@patch("uuid.uuid4")
async def test_generate_state(mock_uuid):
    mock_uuid.return_value = "id"
    result = generate_state()
    # assert
    assert result == mock_uuid()


@patch("pkce.generate_code_verifier")
async def generate_code_verifier(mock_generate_code_verifier):
    mock_generate_code_verifier.return_value = "***"
    result = generate_code_verifier()
    # assert
    assert result == mock_generate_code_verifier()


@patch("pkce.get_code_challenge")
async def mock_generate_code_challenge(mock_get_code_challenge):
    mock_get_code_challenge.return_value = "***"
    result = generate_code_challenge("code")
    # assert
    assert result == mock_get_code_challenge()


@patch("tornado.web.RequestHandler.finish")
@patch("lseg_analytics_jupyterlab.src.handlers.signinHandler.generate_state")
@patch("lseg_analytics_jupyterlab.src.handlers.signinHandler.generate_code_challenge")
@patch(
    "lseg_analytics_jupyterlab.src.handlers.signinHandler.fetch_openid_configuration"
)
async def test_update_proxy_server_data_when_already_running(
    mock_fetch_openid_configuration,
    mock_generate_code_challenge,
    mock_generate_state,
    mock_finish,
    sign_in_handler,
):
    # Setup
    mock_fetch_openid_configuration.return_value = {
        "authorization_endpoint": "sample_auth_endpoint",
        "token_endpoint": "sample_token_endpoint",
    }
    mock_generate_state.return_value = "test-state"
    mock_proxy_server.is_started = True
    mock_proxy_server.proxy_port = 60100

    # Execute
    sign_in_handler.get()

    # Assert
    mock_proxy_server.update_proxy_server_data.assert_called_once_with(
        "127.0.0.1", "1111", "test-state"
    )
    mock_proxy_server.start.assert_not_called()

    params = {
        "response_type": "code",
        "client_id": sign_in_handler.settings["CLIENT_ID"],
        "redirect_uri": f'{sign_in_handler.settings["proxy_server_host"]}:{60100}/auth',
        "code_challenge": mock_generate_code_challenge(),
        "code_challenge_method": "S256",
        "state": mock_generate_state(),
        "scope": "openid profile trapi lfa trapi.platform.iam.acl_service trapi.data.quantitative-analytics.read",
        "response_mode": "query",
    }
    expected_auth_url = f"{mock_fetch_openid_configuration()['authorization_endpoint']}?{urlencode(params)}"
    # Verify JSON response is returned
    expected_response = {
        "status": "success",
        "message": "auth_url",
        "data": {"url": expected_auth_url, "port": 60100},
        "error": None,
    }
    import json

    mock_finish.assert_called_once_with(json.dumps(expected_response))


@patch("tornado.web.RequestHandler.finish")
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.info")
@patch(
    "lseg_analytics_jupyterlab.src.handlers.signinHandler.fetch_openid_configuration"
)
async def test_runtime_error_exception_outer(
    mock_fetch_openid_configuration,
    mock_logger_info,
    mock_logger_error,
    mock_finish,
    sign_in_handler,
):
    mock_proxy_server.is_started = True
    mock_fetch_openid_configuration.return_value = {
        "authorization_endpoint": "sample_auth_endpoint",
        "token_endpoint": "sample_token_endpoint",
    }
    # Raise RuntimeError from logger_main.info, which is after all inner try/except blocks
    mock_logger_info.side_effect = RuntimeError("runtime error occurred")
    sign_in_handler.get()
    error_msg = '{"status": "error", "message": "runtime_error", "data": null, "error": "runtime error occurred"}'
    mock_finish.assert_called_once_with(error_msg)
    mock_logger_error.assert_called_with("runtime error occurred")
