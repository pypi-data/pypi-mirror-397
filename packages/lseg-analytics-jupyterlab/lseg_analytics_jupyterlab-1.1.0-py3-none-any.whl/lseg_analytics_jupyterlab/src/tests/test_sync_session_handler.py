# type: ignore
"""
Tests for SyncSessionHandler.

This module contains unit tests for the SyncSessionHandler, which manages
session synchronization between client and server after a server restart.
"""

import json
import pytest
from unittest.mock import ANY, MagicMock, Mock
from tornado.web import Application

from lseg_analytics_jupyterlab.src.handlers.syncSessionHandler import (
    SyncSessionHandler,
)
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
from lseg_analytics_jupyterlab.src.classes.baseUserSession import BaseUserSession
from lseg_analytics_jupyterlab.src.classes.proxyServer import (
    ProxyServer,
    PORT_UNAVAILABLE_ERROR_MSG_TEMPLATE,
)


@pytest.fixture
def session_service():
    """Create a mock SessionService for testing."""
    service = Mock(spec=SessionService)
    service._current_session = None
    service.settings = {
        "BASE_URL": "https://test.example.com",
        "CLIENT_ID": "test-client-id",
    }
    return service


@pytest.fixture
def sample_session_data():
    """Create sample session data for testing."""
    return {
        "id": "session-123",
        "customerId": "user-456",
        "userDisplayName": "Test User",
        "accessToken": "access-token-xyz",
        "refreshToken": "refresh-token-abc",
        "expiryDatetimeMs": "1234567890000",
        "diagnostics": {
            "sessionStartTimestampMs": 1111111111111,
            "lastTokenRefreshTimestampMs": 2222222222222,
            "refreshCount": 3,
        },
    }


@pytest.fixture
def sample_session_object():
    """Create a sample BaseUserSession object."""
    return BaseUserSession(
        id="session-123",
        user_id="user-456",
        user_display_name="Test User",
        access_token="access-token-xyz",
        refresh_token="refresh-token-abc",
        expiry_date_time_ms="1234567890000",
    )


@pytest.fixture
def proxy_server():
    mock_proxy = Mock(spec=ProxyServer)
    mock_proxy.is_started = False
    return mock_proxy


@pytest.fixture
def sync_handler(session_service, proxy_server):
    """Fixture for SyncSessionHandler with mock session service."""
    application = MagicMock()
    application.settings = {"port_range": {"start": 3000, "end": 3010}}
    mock_request = Mock()
    mock_request.host = "localhost:8888"
    handler = SyncSessionHandler(
        application,
        mock_request,
        session_service=session_service,
        proxy_server=proxy_server,
    )
    handler.set_status = Mock()
    handler.finish = Mock()
    return handler


@pytest.fixture
def sync_handler_with_server_session(
    session_service, sample_session_object, proxy_server
):
    """Fixture for SyncSessionHandler with existing server session."""
    session_service._current_session = sample_session_object
    application = MagicMock()
    application.settings = {"port_range": {"start": 3000, "end": 3010}}
    mock_request = Mock()
    mock_request.host = "localhost:8888"
    proxy_server.is_started = True
    handler = SyncSessionHandler(
        application,
        mock_request,
        session_service=session_service,
        proxy_server=proxy_server,
    )
    handler.set_status = Mock()
    handler.finish = Mock()
    return handler


@pytest.fixture
def sync_handler_with_mismatched_session(session_service, proxy_server):
    """Fixture for SyncSessionHandler with mismatched server session."""
    different_session = BaseUserSession(
        id="different-session-id",
        user_id="different-user",
        user_display_name="Different User",
        access_token="different-access-token",
        refresh_token="different-refresh-token",
        expiry_date_time_ms="9876543210000",
    )
    session_service._current_session = different_session
    application = MagicMock()
    application.settings = {"port_range": {"start": 3000, "end": 3010}}
    mock_request = Mock()
    mock_request.host = "localhost:8888"
    handler = SyncSessionHandler(
        application,
        mock_request,
        session_service=session_service,
        proxy_server=proxy_server,
    )
    handler.set_status = Mock()
    handler.finish = Mock()
    return handler


class TestSyncSessionHandler:
    """Test suite for SyncSessionHandler."""

    def test_initialize(self, session_service, proxy_server):
        """Test handler initialization with session service."""
        application = Application()
        application.settings = {"port_range": {"start": 3000, "end": 3010}}
        mock_request = Mock()
        mock_request.host = "localhost:8888"
        handler = SyncSessionHandler(
            application,
            mock_request,
            session_service=session_service,
            proxy_server=proxy_server,
        )

        assert handler.session_service == session_service
        assert handler.proxy_server == proxy_server

    def test_sync_session_port_unavailable_error(
        self, sync_handler, sample_session_data, session_service
    ):
        """Test port-unavailable error short-circuits session restoration."""

        # Setup request body and proxy failure
        sync_handler.request.body = json.dumps(sample_session_data).encode("utf-8")
        port_error_message = PORT_UNAVAILABLE_ERROR_MSG_TEMPLATE.format(
            start_port=3000, end_port=3010
        )
        sync_handler.proxy_server.start.side_effect = RuntimeError(port_error_message)

        # Execute
        sync_handler.post()

        # Ensure we did not proceed with session restoration
        session_service.set_session.assert_not_called()

        # Verify response details
        sync_handler.finish.assert_called_once()
        response_arg = sync_handler.finish.call_args[0][0]
        response = json.loads(response_arg)
        assert response["status"] == "error"
        assert response["message"] == "port_unavailable"
        assert response["error"] == port_error_message

        # Ensure status untouched and proxy start attempted once
        sync_handler.set_status.assert_not_called()
        sync_handler.proxy_server.start.assert_called_once()

    def test_sync_session_proxy_start_generic_error(
        self, sync_handler, sample_session_data, session_service
    ):
        """Test generic proxy start failure returns proxy_server_error."""

        sync_handler.request.body = json.dumps(sample_session_data).encode("utf-8")
        sync_handler.proxy_server.start.side_effect = RuntimeError("generic failure")

        sync_handler.post()

        session_service.set_session.assert_not_called()

        sync_handler.finish.assert_called_once()
        response_arg = sync_handler.finish.call_args[0][0]
        response = json.loads(response_arg)
        assert response["status"] == "error"
        assert response["message"] == "proxy_server_error"
        assert response["error"] == "generic failure"

        sync_handler.set_status.assert_not_called()
        sync_handler.proxy_server.start.assert_called_once()

    def test_proxy_is_started_if_not_running(self, sample_session_data, sync_handler):
        # Setup request body - data does not matter
        sync_handler.request.body = json.dumps(sample_session_data).encode("utf-8")

        # Setup proxy - not already running
        proxy = sync_handler.proxy_server
        sync_handler.proxy_server.is_started = False

        sync_handler.post()

        # Verify proxy server started with restored session details
        proxy.start.assert_called_once_with(
            [3000, 3010], "localhost", "8888", state=ANY
        )
        proxy.update_proxy_server_data.assert_not_called()

    def test_proxy_is_updated_if_already_running(
        self, sample_session_data, sync_handler
    ):
        # Setup request body - data does not matter
        sync_handler.request.body = json.dumps(sample_session_data).encode("utf-8")

        # Setup proxy - already running
        proxy = sync_handler.proxy_server
        sync_handler.proxy_server.is_started = True

        sync_handler.post()

        # Verify proxy server started with restored session details
        proxy.start.assert_not_called()
        proxy.update_proxy_server_data.assert_called_once_with("localhost", "8888", ANY)

    def test_sync_session_missing_required_fields(self, sync_handler):
        """Test sync with missing required fields returns 400."""
        # Setup: Request with missing fields
        incomplete_data = {
            "id": "session-123",
            # Missing customerId, userDisplayName, accessToken, refreshToken
        }
        sync_handler.request.body = json.dumps(incomplete_data).encode("utf-8")

        # Execute
        sync_handler.post()

        # Verify 400 status was set
        sync_handler.set_status.assert_called_once_with(400)

        # Verify response
        sync_handler.finish.assert_called_once()
        response_arg = sync_handler.finish.call_args[0][0]
        response = json.loads(response_arg)
        assert response["status"] == "error"

        proxy = sync_handler.proxy_server
        proxy.start.assert_not_called()
        proxy.update_proxy_server_data.assert_not_called()

    def test_sync_session_invalid_json(self, sync_handler):
        """Test sync with invalid JSON returns 400."""
        sync_handler.request.body = b"invalid json {{{{"

        # Execute
        sync_handler.post()

        # Verify 400 status was set
        sync_handler.set_status.assert_called_once_with(400)

        # Verify response
        sync_handler.finish.assert_called_once()
        response_arg = sync_handler.finish.call_args[0][0]
        response = json.loads(response_arg)
        assert response["status"] == "error"

    def test_sync_session_empty_body(self, sync_handler):
        """Test sync with empty request body returns 400."""
        sync_handler.request.body = b""

        # Execute
        sync_handler.post()

        # Verify 400 status was set
        sync_handler.set_status.assert_called_once_with(400)

    matching_server_session_object = BaseUserSession(
        id="session-111",
        user_id="user-1",
        user_display_name="Test User 1",
        access_token="access-token-111",
        refresh_token="refresh-token-111",
        expiry_date_time_ms="111",
    )

    non_matching_server_session_object = BaseUserSession(
        id="session-222",
        user_id="user-2",
        user_display_name="Test User 2",
        access_token="access-token-222",
        refresh_token="refresh-token-222",
        expiry_date_time_ms="222",
    )

    @pytest.mark.parametrize(
        "server_session_data",
        [
            None,  # no data on server
            matching_server_session_object,  # server session matches the session suppied by the client
            non_matching_server_session_object,  # server session does not match the session supplied by the client
        ],
    )
    def test_server_session_is_always_overwritten(
        self, sync_handler, session_service, server_session_data
    ):
        """Test session restoration scenarios: should always update the server session, regardless of prior state."""

        session_from_client = {
            "id": "session-111",
            "customerId": "user-1",
            "userDisplayName": "Test User 1",
            "accessToken": "access-token-111",
            "refreshToken": "refresh-token-111",
            "expiryDatetimeMs": "111",
        }

        # Setup:
        sync_handler.request.body = json.dumps(session_from_client).encode("utf-8")
        session_service._current_session = server_session_data

        # Execute
        sync_handler.post()

        # Verify session was restored
        session_service.set_session.assert_called_once()
        restored_session = session_service.set_session.call_args[0][0]
        assert restored_session.id == session_from_client["id"]
        assert restored_session.user_id == session_from_client["customerId"]
        assert (
            restored_session.user_display_name == session_from_client["userDisplayName"]
        )
        assert restored_session.access_token == session_from_client["accessToken"]
        assert restored_session.refresh_token == session_from_client["refreshToken"]

        # Verify response
        sync_handler.finish.assert_called_once()
        response_arg = sync_handler.finish.call_args[0][0]
        response = json.loads(response_arg)
        assert response["status"] == "success"
        assert "restored" in response["message"].lower()

    def test_sessions_match_with_same_id_and_refresh_token(self, sync_handler):
        """Test _sessions_match returns True when sessions have matching ID and refresh token."""
        session1 = BaseUserSession(
            id="session-123",
            user_id="user-456",
            user_display_name="Test User",
            access_token="access-token-1",
            refresh_token="refresh-token-match",
            expiry_date_time_ms="1234567890000",
        )

        session2 = BaseUserSession(
            id="session-123",
            user_id="user-456",
            user_display_name="Test User",
            access_token="access-token-2",  # Different access token is OK
            refresh_token="refresh-token-match",
            expiry_date_time_ms="9876543210000",  # Different expiry is OK
        )

        assert sync_handler._sessions_match(session1, session2) is True

    def test_sessions_match_with_different_id(self, sync_handler):
        """Test _sessions_match returns False when session IDs differ."""
        session1 = BaseUserSession(
            id="session-123",
            user_id="user-456",
            user_display_name="Test User",
            access_token="access-token",
            refresh_token="refresh-token",
            expiry_date_time_ms="1234567890000",
        )

        session2 = BaseUserSession(
            id="different-session-id",
            user_id="user-456",
            user_display_name="Test User",
            access_token="access-token",
            refresh_token="refresh-token",
            expiry_date_time_ms="1234567890000",
        )

        assert sync_handler._sessions_match(session1, session2) is False

    def test_sessions_match_with_different_refresh_token(self, sync_handler):
        """Test _sessions_match returns False when refresh tokens differ."""
        session1 = BaseUserSession(
            id="session-123",
            user_id="user-456",
            user_display_name="Test User",
            access_token="access-token",
            refresh_token="refresh-token-1",
            expiry_date_time_ms="1234567890000",
        )

        session2 = BaseUserSession(
            id="session-123",
            user_id="user-456",
            user_display_name="Test User",
            access_token="access-token",
            refresh_token="refresh-token-2",
            expiry_date_time_ms="1234567890000",
        )

        assert sync_handler._sessions_match(session1, session2) is False

    def test_sync_session_preserves_diagnostics(self, sync_handler, session_service):
        """Test that diagnostics are preserved when syncing session from client."""
        session_with_diagnostics = {
            "id": "session-789",
            "customerId": "user-999",
            "userDisplayName": "Diagnostic User",
            "accessToken": "access-token-diag",
            "refreshToken": "refresh-token-diag",
            "expiryDatetimeMs": "1234567890000",
            "diagnostics": {
                "sessionStartTimestampMs": 5555555555555,
                "lastTokenRefreshTimestampMs": 6666666666666,
                "refreshCount": 5,
            },
        }

        sync_handler.request.body = json.dumps(session_with_diagnostics).encode(
            "utf-8"
        )
        sync_handler.post()

        # Verify session was restored with diagnostics
        session_service.set_session.assert_called_once()
        restored_session = session_service.set_session.call_args[0][0]
        assert restored_session.diagnostics is not None
        assert (
            restored_session.diagnostics["sessionStartTimestampMs"] == 5555555555555
        )
        assert (
            restored_session.diagnostics["lastTokenRefreshTimestampMs"]
            == 6666666666666
        )
        assert restored_session.diagnostics["refreshCount"] == 5
