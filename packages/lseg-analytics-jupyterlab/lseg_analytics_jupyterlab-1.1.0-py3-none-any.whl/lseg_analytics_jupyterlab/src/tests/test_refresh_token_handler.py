import json
import pytest
import time
from unittest.mock import MagicMock, patch
from lseg_analytics_jupyterlab.src.handlers.refreshTokenHandler import (
    RefreshTokenHandler,
)


@pytest.fixture
def mock_session_with_fresh_token():
    """Fixture for a mock user session with fresh token."""
    session = MagicMock()
    session.access_token = "fresh-access-token"
    session.refresh_token = "fresh-refresh-token"
    session.expiry_date_time_ms = 987654321
    return session


@pytest.fixture
def mock_session_service_success(mock_session_with_fresh_token):
    """Session service that successfully returns a refreshed session."""
    service = MagicMock()
    service.get_session.return_value = mock_session_with_fresh_token
    # Mock the session store with matching refresh token
    service._current_session = MagicMock()
    service._current_session.refresh_token = "valid-refresh-token"
    return service


@pytest.fixture
def mock_session_service_failure():
    """Session service where get_session fails (returns None)."""
    service = MagicMock()
    service.get_session.return_value = None
    # Mock the session store with matching refresh token
    service._current_session = MagicMock()
    service._current_session.refresh_token = "valid-refresh-token"
    return service


@pytest.fixture
def mock_session_service_invalid_token():
    """Session service with mismatched refresh token."""
    service = MagicMock()
    service.get_session.return_value = None
    # Mock the session store with different refresh token
    service._current_session = MagicMock()
    service._current_session.refresh_token = "different-refresh-token"
    return service


@pytest.fixture
def handler_settings():
    """Fixture for handler settings."""
    return {
        "TOKEN_URL": "https://test-token-url.com/token",
        "CLIENT_ID": "test-client-id",
        "redirect_uri": "http://localhost:8888/callback",
    }


@pytest.fixture
def handler_with_session_success(handler_settings, mock_session_service_success):
    """Fixture for RefreshTokenHandler with successful session service."""
    mock_application = MagicMock()
    mock_application.settings = handler_settings
    handler = RefreshTokenHandler(
        mock_application, MagicMock(), session_service=mock_session_service_success
    )
    handler.set_status = MagicMock()
    handler.finish = MagicMock()
    return handler


@pytest.fixture
def handler_with_session_failure(handler_settings, mock_session_service_failure):
    """Fixture for RefreshTokenHandler with failed session service."""
    mock_application = MagicMock()
    mock_application.settings = handler_settings
    handler = RefreshTokenHandler(
        mock_application, MagicMock(), session_service=mock_session_service_failure
    )
    handler.set_status = MagicMock()
    handler.finish = MagicMock()
    return handler


@pytest.fixture
def handler_with_invalid_token(handler_settings, mock_session_service_invalid_token):
    """Fixture for RefreshTokenHandler with invalid token."""
    mock_application = MagicMock()
    mock_application.settings = handler_settings
    handler = RefreshTokenHandler(
        mock_application,
        MagicMock(),
        session_service=mock_session_service_invalid_token,
    )
    handler.set_status = MagicMock()
    handler.finish = MagicMock()
    return handler


@pytest.fixture
def mock_request_with_token():
    """Mock request with valid refresh token."""
    request = MagicMock()
    request.body = json.dumps({"refresh_token": "valid-refresh-token"}).encode("utf-8")
    return request


@pytest.fixture
def mock_request_without_token():
    """Mock request without refresh token."""
    request = MagicMock()
    request.body = json.dumps({}).encode("utf-8")
    return request


class TestRefreshTokenHandlerFixture:
    """Test cases for the updated RefreshTokenHandler using SessionService."""

    def test_successful_token_refresh(
        self, handler_with_session_success, mock_request_with_token
    ):
        """Test successful token refresh through SessionService."""
        handler_with_session_success.request = mock_request_with_token

        # Execute
        handler_with_session_success.post()

        # Verify successful response
        handler_with_session_success.finish.assert_called_once()
        response = handler_with_session_success.finish.call_args[0][0]
        response_dict = json.loads(response)

        assert response_dict["status"] == "success"
        assert response_dict["message"] == "Token refreshed successfully"
        assert "data" in response_dict
        assert response_dict["data"]["accessToken"] == "fresh-access-token"
        assert response_dict["data"]["refreshToken"] == "fresh-refresh-token"
        assert response_dict["data"]["expiresAt"] == 987654321

    def test_session_refresh_failed(
        self, handler_with_session_failure, mock_request_with_token
    ):
        """Test when SessionService.get_session() returns None (refresh failed)."""
        handler_with_session_failure.request = mock_request_with_token

        # Execute
        handler_with_session_failure.post()

        # Verify 500 response (server error when session refresh fails)
        handler_with_session_failure.set_status.assert_called_once_with(500)
        handler_with_session_failure.finish.assert_called_once()
        response = handler_with_session_failure.finish.call_args[0][0]
        response_dict = json.loads(response)

        assert response_dict["status"] == "error"
        assert "Internal server error during token refresh" in response_dict["message"]

    def test_missing_refresh_token(
        self, handler_with_session_success, mock_request_without_token
    ):
        """Test missing refresh token in request."""
        handler_with_session_success.request = mock_request_without_token

        # Execute
        handler_with_session_success.post()

        # Verify 400 response
        handler_with_session_success.set_status.assert_called_once_with(400)
        handler_with_session_success.finish.assert_called_once()
        response = handler_with_session_success.finish.call_args[0][0]
        response_dict = json.loads(response)

        assert response_dict["status"] == "error"
        assert response_dict["message"] == "Missing refresh_token"

    def test_exception_handling(
        self, handler_with_session_success, mock_request_with_token
    ):
        """Test exception handling in post method."""
        handler_with_session_success.request = mock_request_with_token
        # Make session service raise an exception after the token validation passes
        handler_with_session_success.session_service.get_session.side_effect = (
            Exception("Test exception")
        )

        # Execute
        handler_with_session_success.post()

        # Verify 500 response
        handler_with_session_success.set_status.assert_called_once_with(500)
        handler_with_session_success.finish.assert_called_once()
        response = handler_with_session_success.finish.call_args[0][0]
        response_dict = json.loads(response)

        assert response_dict["status"] == "error"
        assert "Internal server error during token refresh" in response_dict["message"]

    def test_invalid_refresh_token(
        self, handler_with_invalid_token, mock_request_with_token
    ):
        """Test invalid refresh token in request."""
        handler_with_invalid_token.request = mock_request_with_token

        # Execute
        handler_with_invalid_token.post()

        # Verify 401 response
        handler_with_invalid_token.set_status.assert_called_once_with(401)
        handler_with_invalid_token.finish.assert_called_once()
        response = handler_with_invalid_token.finish.call_args[0][0]
        response_dict = json.loads(response)

        assert response_dict["status"] == "error"
        assert response_dict["message"] == "Invalid refresh token"
