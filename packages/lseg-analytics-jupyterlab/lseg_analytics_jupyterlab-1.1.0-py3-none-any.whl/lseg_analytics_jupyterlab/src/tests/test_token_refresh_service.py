import json
import pytest
import time
from unittest.mock import MagicMock, Mock, patch
import requests
from lseg_analytics_jupyterlab.src.services.tokenRefreshService import (
    TokenRefreshService,
)


@pytest.fixture
def mock_session():
    """Fixture for a mock user session."""
    session = MagicMock()
    session.access_token = "old-access-token"
    session.refresh_token = "old-refresh-token"
    # Set expiry to far in the future (current time + 1 hour in milliseconds)
    session.expiry_date_time_ms = str(int((time.time() + 3600) * 1000))
    return session


@pytest.fixture
def mock_expired_session():
    """Fixture for a mock expired user session."""
    session = MagicMock()
    session.access_token = "expired-access-token"
    session.refresh_token = "expired-refresh-token"
    # Set expiry to past timestamp
    session.expiry_date_time_ms = str(int((time.time() - 3600) * 1000))  # 1 hour ago
    return session


@pytest.fixture
def mock_expiring_session():
    """Fixture for a mock expiring user session."""
    session = MagicMock()
    session.access_token = "expiring-access-token"
    session.refresh_token = "expiring-refresh-token"
    # Set expiry to 2 minutes from now (within 5 minute buffer)
    session.expiry_date_time_ms = str(
        int((time.time() + 120) * 1000)
    )  # 2 minutes from now
    return session


@pytest.fixture
def mock_session_service(mock_session):
    """Fixture for a mock session service."""
    service = MagicMock()
    service.get_session.return_value = mock_session
    return service


@pytest.fixture
def mock_expired_session_service(mock_expired_session):
    """Fixture for a mock session service with expired session."""
    service = MagicMock()
    service.get_session.return_value = mock_expired_session
    return service


@pytest.fixture
def mock_expiring_session_service(mock_expiring_session):
    """Fixture for a mock session service with expiring session."""
    service = MagicMock()
    service.get_session.return_value = mock_expiring_session
    return service


@pytest.fixture
def valid_settings():
    """Fixture for valid service settings."""
    return {
        "TOKEN_URL": "https://test-token-url.com/token",
        "CLIENT_ID": "test-client-id",
        "redirect_uri": "http://localhost:8888/callback",
    }


@pytest.fixture
def invalid_settings():
    """Fixture for invalid service settings."""
    return {
        "TOKEN_URL": None,
        "CLIENT_ID": None,
    }


@pytest.fixture
def token_service(valid_settings):
    """Fixture for the TokenRefreshService instance."""
    return TokenRefreshService(settings=valid_settings)


@pytest.fixture
def mock_successful_token_response():
    """Fixture for a successful token response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
        "expires_in": 3600,
    }
    return response


@pytest.fixture
def mock_failed_token_response():
    """Fixture for a failed token response."""
    response = MagicMock()
    response.status_code = 401
    response.text = "Invalid refresh token"
    return response


class TestTokenRefreshService:
    """Test cases for TokenRefreshService."""

    def test_initialization(self, valid_settings):
        """Test TokenRefreshService initialization."""
        service = TokenRefreshService(settings=valid_settings)
        assert service.settings == valid_settings

    def test_initialization_with_required_params(self, valid_settings):
        """Test TokenRefreshService initialization with required parameters."""
        service = TokenRefreshService(settings=valid_settings)
        assert service.settings == valid_settings

    def test_validate_configuration_success(self, token_service):
        """Test successful configuration validation."""

        # Note: we're patching the import of ensure_auth_settings in the tokenRefreshService module
        with patch(
            "lseg_analytics_jupyterlab.src.services.tokenRefreshService.ensure_auth_settings"
        ) as mock_ensure:

            def update_settings(settings):
                settings["TOKEN_URL"] = "token_url value"
                settings["CLIENT_ID"] = "client id value"
                return settings

            mock_ensure.side_effect = update_settings

            valid, message, token_url, client_id = (
                token_service._validate_configuration()
            )

        assert mock_ensure.called
        assert valid is True
        assert message == "Configuration valid"
        assert token_url == "token_url value"
        assert client_id == "client id value"

    def test_validate_configuration_no_settings(self):
        """Test configuration validation with no settings."""
        service = TokenRefreshService(settings=None)
        valid, message, token_url, client_id = service._validate_configuration()

        assert valid is False
        assert message == "Missing configuration settings"
        assert token_url == ""
        assert client_id == ""

    def test_validate_configuration_ensure_auth_settings_throws(self, token_service):
        """Test successful configuration validation."""

        # Note: we're patching the import of ensure_auth_settings in the tokenRefreshService module where
        with patch(
            "lseg_analytics_jupyterlab.src.services.tokenRefreshService.ensure_auth_settings"
        ) as mock_ensure:
            mock_ensure.side_effect = Exception(
                "Test exception from ensure_auth_settings"
            )

            valid, message, token_url, client_id = (
                token_service._validate_configuration()
            )

        assert mock_ensure.called
        assert valid is False
        assert message == "Test exception from ensure_auth_settings"
        assert token_url == ""
        assert client_id == ""

    def test_prepare_token_request_data(self, token_service):
        """Test token request data preparation."""
        data = token_service._prepare_token_request_data(
            "test-refresh-token", "test-client-id"
        )

        expected_data = {
            "grant_type": "refresh_token",
            "refresh_token": "test-refresh-token",
            "client_id": "test-client-id",
        }
        assert data == expected_data

    @patch("requests.post")
    def test_make_token_request_success(
        self, mock_post, token_service, mock_successful_token_response
    ):
        """Test successful token request."""
        mock_post.return_value = mock_successful_token_response
        data = {
            "grant_type": "refresh_token",
            "refresh_token": "test-token",
            "client_id": "test-client",
        }

        response = token_service._make_token_request("https://test-url.com/token", data)

        assert response == mock_successful_token_response
        mock_post.assert_called_once_with(
            "https://test-url.com/token", data=data, timeout=(10, 30)
        )

    @patch("requests.post")
    def test_make_token_request_failure(self, mock_post, token_service):
        """Test token request failure."""
        mock_post.side_effect = requests.RequestException("Network error")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": "test-token",
            "client_id": "test-client",
        }

        with pytest.raises(requests.RequestException):
            token_service._make_token_request("https://test-url.com/token", data)

    def test_validate_token_response_success(
        self, token_service, mock_successful_token_response
    ):
        """Test successful token response validation."""
        valid, message, tokens = token_service._validate_token_response(
            mock_successful_token_response
        )

        assert valid is True
        assert message == "Token response valid"
        assert tokens["access_token"] == "new-access-token"
        assert tokens["refresh_token"] == "new-refresh-token"
        assert tokens["expires_in"] == 3600

    def test_validate_token_response_http_error(
        self, token_service, mock_failed_token_response
    ):
        """Test token response validation with HTTP error."""
        valid, message, tokens = token_service._validate_token_response(
            mock_failed_token_response
        )

        assert valid is False
        assert "Refresh failed with status 401" in message
        assert tokens is None

    def test_validate_token_response_missing_fields(self, token_service):
        """Test token response validation with missing fields."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "access_token": "new-access-token",
            # Missing refresh_token and expires_in
        }

        valid, message, tokens = token_service._validate_token_response(response)

        assert valid is False
        assert message == "Invalid token response - missing required fields"
        assert tokens is None

    def test_validate_token_response_json_error(self, token_service):
        """Test token response validation with JSON decode error."""
        response = MagicMock()
        response.status_code = 200
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        valid, message, tokens = token_service._validate_token_response(response)

        assert valid is False
        assert message == "Invalid token response format"
        assert tokens is None

    def test_update_session_success(self, token_service, mock_session):
        """Test successful session update including diagnostics."""
        # Set up initial diagnostics
        mock_session.diagnostics = {
            "sessionStartTimestampMs": 111111,
            "lastTokenRefreshTimestampMs": 222222,
            "refreshCount": 2,
        }

        with patch("time.time", return_value=1000):
            result = token_service._update_session(
                mock_session, "new-access-token", "new-refresh-token", 3600
            )

        assert result == mock_session
        assert mock_session.access_token == "new-access-token"
        assert mock_session.refresh_token == "new-refresh-token"
        # Should be 1000 * 1000 + 3600 * 1000 = 4600000
        assert mock_session.expiry_date_time_ms == "4600000"
        # Verify diagnostics were updated
        assert mock_session.diagnostics["refreshCount"] == 3  # Incremented from 2 to 3
        assert mock_session.diagnostics["lastTokenRefreshTimestampMs"] == 1000000
        assert mock_session.diagnostics["sessionStartTimestampMs"] == 111111  # Unchanged

    def test_update_session_no_session(self):
        """Test session update with no session provided."""
        service = TokenRefreshService(settings={})
        result = service._update_session(
            None, "new-access-token", "new-refresh-token", 3600
        )

        assert result is None

    def test_is_token_expired_or_expiring_valid_token(
        self, token_service, mock_session
    ):
        """Test token expiry check with valid token."""
        # mock_session has expiry_date_time_ms = "1000000000000" which is far in the future
        result = token_service._is_token_expired_or_expiring(mock_session)

        assert result is False

    def test_is_token_expired_or_expiring_expired_token(
        self, token_service, mock_expired_session
    ):
        """Test token expiry check with expired token."""
        result = token_service._is_token_expired_or_expiring(mock_expired_session)

        assert result is True

    def test_is_token_expired_or_expiring_expiring_token(
        self, token_service, mock_expiring_session
    ):
        """Test token expiry check with expiring token."""
        result = token_service._is_token_expired_or_expiring(mock_expiring_session)

        assert result is True

    def test_is_token_expired_or_expiring_no_session_service(self):
        """Test token expiry check with no session service."""
        service = TokenRefreshService(settings=None)
        # Create a session with invalid expiry to test the logic
        invalid_session = MagicMock()
        invalid_session.expiry_date_time_ms = None

        result = service._is_token_expired_or_expiring(invalid_session)

        assert result is True  # Assume expired if we can't check

    def test_is_token_expired_or_expiring_invalid_expiry(self, valid_settings):
        """Test token expiry check with invalid expiry time."""
        session = MagicMock()
        session.expiry_date_time_ms = "invalid"
        service = TokenRefreshService(settings=valid_settings)

        result = service._is_token_expired_or_expiring(session)

        assert result is True  # Assume expired if we can't parse

    @patch("requests.post")
    @patch(
        "lseg_analytics_jupyterlab.src.services.tokenRefreshService.ensure_auth_settings"
    )
    def test_perform_token_refresh_success(
        self, mock_ensure, mock_post, token_service, mock_successful_token_response
    ):
        """Test successful token refresh."""
        mock_post.return_value = mock_successful_token_response

        success, message, response_data = token_service.perform_token_refresh(
            "test-refresh-token"
        )

        assert success is True
        assert message == "Tokens refreshed successfully"
        assert response_data["access_token"] == "new-access-token"
        assert response_data["refresh_token"] == "new-refresh-token"
        assert response_data["expires_in"] == 3600

    @patch("requests.post")
    def test_perform_token_refresh_invalid_config(self, mock_post):
        """Test token refresh with invalid configuration."""
        service = TokenRefreshService(None)

        success, message, response_data = service.perform_token_refresh(
            "test-refresh-token"
        )

        assert success is False
        assert message == "Configuration error: Missing configuration settings"
        assert response_data is None

    @patch("requests.post")
    @patch(
        "lseg_analytics_jupyterlab.src.services.tokenRefreshService.ensure_auth_settings"
    )
    def test_perform_token_refresh_network_error(
        self, mock_ensure, mock_post, token_service
    ):
        """Test token refresh with network error."""
        mock_post.side_effect = requests.RequestException("Network error")

        success, message, response_data = token_service.perform_token_refresh(
            "test-refresh-token"
        )

        assert success is False
        assert message == "Network error: Network error"
        assert response_data is None

    def test_proactive_token_refresh_not_needed(self, token_service, mock_session):
        """Test proactive refresh when token is still valid."""
        success, message, tokens = token_service.proactive_token_refresh(mock_session)

        assert success is True
        assert message == "Token is still valid"
        assert tokens == mock_session  # Should return the original session

    @patch("requests.post")
    @patch(
        "lseg_analytics_jupyterlab.src.services.tokenRefreshService.ensure_auth_settings"
    )
    def test_proactive_token_refresh_success(
        self,
        mock_ensure,
        mock_post,
        token_service,
        mock_expiring_session,
        mock_successful_token_response,
    ):
        """Test successful proactive token refresh."""
        mock_post.return_value = mock_successful_token_response

        success, message, tokens = token_service.proactive_token_refresh(
            mock_expiring_session
        )

        assert success is True
        assert message == "Tokens refreshed successfully"
        assert tokens is not None

    def test_proactive_token_refresh_no_refresh_token(self, token_service):
        """Test proactive refresh with no refresh token in session."""
        # Set up session without refresh token but with expiring time
        session = MagicMock()
        session.refresh_token = None
        session.expiry_date_time_ms = str(
            int((time.time() + 120) * 1000)
        )  # 2 minutes from now

        success, message, tokens = token_service.proactive_token_refresh(session)

        assert success is False
        assert message == "No refresh token available in session"
        assert tokens is None

    def test_proactive_token_refresh_exception(self, token_service):
        """Test proactive refresh with exception."""
        # Test what happens when no session is provided (None)
        success, message, tokens = token_service.proactive_token_refresh(None)

        assert success is False
        assert message == "No session provided"
        assert tokens is None

    def test_is_token_expired_or_expiring_no_session_available(self, valid_settings):
        """Test token expiry check when no session is available."""
        service = TokenRefreshService(settings=valid_settings)

        # Create a session with no expiry_date_time_ms to simulate "no session available"
        empty_session = MagicMock()
        empty_session.expiry_date_time_ms = None

        # Execute
        result = service._is_token_expired_or_expiring(empty_session)

        # Verify assumes expired when no expiry time
        assert result is True

    def test_is_token_expired_or_expiring_no_expiry_time(
        self, valid_settings, mock_session
    ):
        """Test token expiry check when session has no expiry time."""
        # Setup service with session that has no expiry_date_time_ms
        mock_session_service = Mock()
        mock_session = Mock()
        mock_session.expiry_date_time_ms = None
        mock_session_service.get_session.return_value = mock_session

        service = TokenRefreshService(valid_settings)

        # Execute
        result = service._is_token_expired_or_expiring(mock_session)

        # Verify assumes expired when no expiry time
        assert result is True

    def test_is_token_expired_or_expiring_empty_expiry_time(
        self, valid_settings, mock_session
    ):
        """Test token expiry check when session has empty expiry time."""
        # Setup service with session that has empty expiry_date_time_ms
        mock_session_service = Mock()
        mock_session = Mock()
        mock_session.expiry_date_time_ms = ""
        mock_session_service.get_session.return_value = mock_session

        service = TokenRefreshService(valid_settings)

        # Execute
        result = service._is_token_expired_or_expiring(mock_session)

        # Verify assumes expired when expiry time is empty
        assert result is True
