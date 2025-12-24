# type: ignore
import pytest
from unittest.mock import MagicMock, Mock, patch
from tornado.web import Application

from tornado.httputil import HTTPServerRequest, HTTPHeaders
from lseg_analytics_jupyterlab.src.classes.baseUserSession import BaseUserSession
from lseg_analytics_jupyterlab.src.handlers.callBackHandler import CallBackHandler
import json
import time


@pytest.fixture
@patch("lseg_analytics_jupyterlab.src.classes.sessionService.SessionService")
def callback_handler(mock_session_service):
    application = Application()

    mock_session_service.set_session = Mock()
    request = create_request(method="GET", uri="/callback", host="127.0.0.1")
    handler = CallBackHandler(
        application, request, session_service=mock_session_service
    )
    return handler


@pytest.fixture
def mock_get_signing_key():
    with patch("jwt.PyJWKClient.get_signing_key_from_jwt") as mock_get_signing_key:
        # Create a mock signing key
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test_sign_key"

        mock_get_signing_key.return_value = mock_signing_key
        yield mock_get_signing_key


@pytest.fixture
def mock_jwt_decode():
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test_user_id", "name": "test_name"}
        yield mock_decode


def test_assert_if_session_service_is_populated(callback_handler):
    assert callback_handler._session_service is not None


@patch("lseg_analytics_jupyterlab.src.handlers.callBackHandler.logger_main.info")
@patch(
    "lseg_analytics_jupyterlab.src.handlers.callBackHandler.BaseUserSession",
    autospec=True,
)
@patch("uuid.uuid4")
@patch("time.time")
def test_get_success(
    mock_time,
    mock_uuid,
    mock_base_user_session,
    mock_logger_info,
    mock_jwt_decode,
    mock_get_signing_key,
    callback_handler,
):
    with patch("requests.post") as mock_post, patch(
        "lseg_analytics_jupyterlab.src.handlers.callBackHandler.WebSocket.send_message_to_client"
    ) as mock_send_message:
        # Set up time mock
        current_time_s = 1000
        expires_in_s = 3600
        expected_expiry_ms = (current_time_s + expires_in_s) * 1000
        mock_time.return_value = current_time_s

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "id_token": "id_token",
            "refresh_token": "test_refresh",
            "expires_in": expires_in_s,
        }
        mock_uuid.return_value = "test-uuid"
        instance = mock_base_user_session.return_value

        # Set up session instance properties
        instance.id = "test-uuid"
        instance.user_id = "test_user_id"
        instance.user_display_name = "test_name"
        instance.access_token = "test_token"
        instance.refresh_token = "test_refresh"
        instance.expiry_date_time_ms = expected_expiry_ms
        instance.diagnostics = {
            "sessionStartTimestampMs": current_time_s,
            "lastTokenRefreshTimestampMs": current_time_s,
            "refreshCount": 0,
        }
        mock_post.return_value = mock_response
        callback_handler.get_argument = Mock(return_value="test_code")
        callback_handler.settings["TOKEN_URL"] = "https://test.com/token"
        callback_handler.settings["code_verifier"] = "test_verifier"
        callback_handler.settings["redirect_uri"] = "https://test.com/callback"
        callback_handler.settings["CLIENT_ID"] = "test_client_id"
        callback_handler.settings["BASE_URL"] = "https://login.stage.ciam.refinitiv.com"
        callback_handler.finish = Mock()
        callback_handler.get()

        mock_post.assert_called_once_with(
            callback_handler.settings["TOKEN_URL"],
            data={
                "grant_type": "authorization_code",
                "code": "test_code",
                "redirect_uri": callback_handler.settings["redirect_uri"],
                "client_id": callback_handler.settings["CLIENT_ID"],
                "code_verifier": callback_handler.settings["code_verifier"],
            },
        )

        callback_handler.finish.assert_called_once()
        mock_get_signing_key.assert_called_once_with("id_token")
        mock_jwt_decode.assert_called_once_with(
            "id_token",
            key="test_sign_key",
            issuer="https://login.stage.ciam.refinitiv.com",
            algorithms=["ES256", "RS256"],
            options={"require": ["exp", "iss", "sub"]},
            audience="test_client_id",
        )
        mock_base_user_session.assert_called_once_with(
            "test-uuid",
            "test_user_id",
            "test_name",
            "test_token",
            "test_refresh",
            expected_expiry_ms,
        )
        callback_handler._session_service.set_session.assert_called_once_with(instance)
        mock_logger_info.assert_called_once_with("Tokens retrieved successfully")


@patch(
    "lseg_analytics_jupyterlab.src.classes.sessionService.SessionService.set_session"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
def test_get_unexpected_error(mock_logger_error, mock_set_session, callback_handler):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("Unexpected error")

        callback_handler.finish = Mock()
        callback_handler.get_argument = Mock(return_value="test_code")
        callback_handler.set_status = Mock()

        callback_handler.get()

        callback_handler.set_status.assert_called_once_with(500)
        callback_handler.finish.assert_called_once()
        mock_set_session.assert_not_called()
        mock_logger_error.assert_called_once_with(
            "An unexpected error occurred: 'code_verifier'"
        )


@patch(
    "lseg_analytics_jupyterlab.src.classes.sessionService.SessionService.set_session"
)
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
@patch(
    "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket.send_message_to_client"
)
def test_get_authentication_failure(
    mock_send_message_to_client, mock_logger_error, mock_set_session, callback_handler
):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "invalid_grant"}
        mock_post.return_value = mock_response

        callback_handler.get_argument = Mock(return_value="test_code")
        callback_handler.settings["TOKEN_URL"] = "https://test.com/token"
        callback_handler.settings["code_verifier"] = "test_verifier"
        callback_handler.settings["redirect_uri"] = "https://test.com/callback"
        callback_handler.settings["CLIENT_ID"] = "test_client_id"
        callback_handler.finish = Mock()
        callback_handler.set_status = Mock()

        callback_handler.get()

        callback_handler.set_status.assert_called_once_with(400)
        callback_handler.finish.assert_called_once()
        mock_set_session.assert_not_called()
        mock_logger_error.assert_called_once_with(
            "Authentication failed, please try again."
        )
        mock_send_message_to_client.assert_called_once_with(
            json.dumps(
                {
                    "message_type": "AUTHENTICATION",
                    "message": {"content": "auth_fail", "log_level": "ERROR"},
                }
            )
        )


def create_request(method="GET", uri="/callback", host="127.0.0.1", headers=None):
    mock_iostream = Mock()
    if headers is None:
        headers = {}

    http_headers = HTTPHeaders(headers)
    if "Host" not in http_headers:
        http_headers["Host"] = host

    request = HTTPServerRequest(
        method=method,
        uri=uri,
        connection=mock_iostream,
        headers=http_headers,
    )

    return request
