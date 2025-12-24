# type: ignore
from lseg_analytics_jupyterlab.src.classes.baseUserSession import BaseUserSession
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
import pytest
import time
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture()
def mock_settings():
    return {"TOKEN_URL": "https://test.token.url", "CLIENT_ID": "test_client_id"}


@pytest.fixture()
def session_service(mock_settings):
    return SessionService(settings=mock_settings)


@pytest.fixture()
def user_session():
    # Create a session with a token that expires far in the future (no refresh needed)
    future_expiry = str(
        int(time.time() * 1000) + 24 * 3600 * 1000
    )  # Expires in 24 hours (milliseconds)
    return BaseUserSession(
        "test_id",
        "test_user_id",
        "test_user_name",
        "test_access_token",
        "test_refresh_token",
        future_expiry,  # This goes to expiry_date_time_ms
    )


@pytest.fixture()
def expiring_user_session():
    # Create a session with a token that expires soon (needs refresh)
    soon_expiry = str(
        int(time.time() * 1000) + 60000
    )  # Expires in 1 minute (within 2-minute buffer) - in milliseconds
    return BaseUserSession(
        "test_id",
        "test_user_id",
        "test_user_name",
        "test_access_token",
        "test_refresh_token",
        soon_expiry,
    )


@pytest.fixture()
def invalid_expiry_session():
    # Create a session with invalid expiry format
    return BaseUserSession(
        "test_id",
        "test_user_id",
        "test_user_name",
        "test_access_token",
        "test_refresh_token",
        "invalid_expiry_format",
    )


@pytest.fixture()
def no_expiry_session():
    # Create a session with no expiry information
    session = BaseUserSession(
        "test_id",
        "test_user_id",
        "test_user_name",
        "test_access_token",
        "test_refresh_token",
        None,
    )
    # Remove expiry_date_time_ms to simulate missing expiry
    session.expiry_date_time_ms = None
    return session


def test_set_session(user_session, session_service):
    session_service.set_session(user_session)
    assert session_service._current_session is not None


def test_get_session(user_session, session_service):
    session_service.set_session(user_session)
    expected_session = session_service.get_session()
    assert expected_session is not None
    assert expected_session.id == user_session.id
    assert expected_session.user_id == user_session.user_id
    assert expected_session.user_display_name == user_session.user_display_name
    assert expected_session.access_token == user_session.access_token
    assert expected_session.refresh_token == user_session.refresh_token


def test_get_session_with_successful_token_refresh(
    expiring_user_session, session_service
):
    """Test successful token refresh when token is expiring."""
    session_service.set_session(expiring_user_session)

    # Mock the token refresh service to return success
    mock_token_service = MagicMock()
    mock_token_service.proactive_token_refresh.return_value = (True, "Success", None)
    session_service._token_refresh_service = mock_token_service

    # Patch the logger before calling get_session
    with patch(
        "lseg_analytics_jupyterlab.src.classes.sessionService.logger_main"
    ) as mock_logger:
        result = session_service.get_session()

        # Should return the session after successful refresh
        assert result is not None
        assert result == expiring_user_session

        # Verify logging calls - updated to match current implementation
        mock_logger.debug.assert_any_call(
            "[SessionService] Token expiring, attempting automatic refresh"
        )
        mock_logger.debug.assert_any_call(
            "[SessionService] Token refreshed successfully"
        )

        # Verify token refresh was called
        mock_token_service.proactive_token_refresh.assert_called_once()


def test_get_session_with_failed_token_refresh(expiring_user_session, session_service):
    """Test failed token refresh when token is expiring."""
    session_service.set_session(expiring_user_session)

    # Mock the token refresh service to return failure
    mock_token_service = MagicMock()
    mock_token_service.proactive_token_refresh.return_value = (
        False,
        "Refresh failed",
        None,
    )
    session_service._token_refresh_service = mock_token_service

    # Patch the logger before calling get_session
    with patch(
        "lseg_analytics_jupyterlab.src.classes.sessionService.logger_main"
    ) as mock_logger:
        result = session_service.get_session()

        # Should return None after failed refresh and clear session
        assert result is None
        assert session_service._current_session is None

        # Verify logging calls - updated to match current implementation
        mock_logger.debug.assert_any_call(
            "[SessionService] Token expiring, attempting automatic refresh"
        )
        mock_logger.warn.assert_called_with(
            "[SessionService] Token refresh failed: Refresh failed"
        )

        # Verify token refresh was called
        mock_token_service.proactive_token_refresh.assert_called_once()


def test_is_token_expired_or_expiring_with_no_session(session_service):
    """Test _is_token_expired_or_expiring when no session exists."""
    # Should return False when no session is stored
    assert session_service._is_token_expired_or_expiring() is False


def test_is_token_expired_or_expiring_with_no_expiry(
    no_expiry_session, session_service
):
    """Test _is_token_expired_or_expiring when session has no expiry information."""
    session_service.set_session(no_expiry_session)

    # Should return True when no expiry information is available
    assert session_service._is_token_expired_or_expiring() is True


def test_is_token_expired_or_expiring_with_invalid_expiry(
    invalid_expiry_session, session_service
):
    """Test _is_token_expired_or_expiring with invalid expiry format."""
    session_service.set_session(invalid_expiry_session)

    with patch(
        "lseg_analytics_jupyterlab.src.classes.sessionService.logger_main"
    ) as mock_logger:
        result = session_service._is_token_expired_or_expiring()

        # Should return True for invalid expiry format
        assert result is True

        # Should log warning about invalid format
        mock_logger.warn.assert_called()
        # Check that warn was called with a message containing the expected text
        warn_call_args = mock_logger.warn.call_args[0][0]
        assert "[SessionService] Invalid token expiry format:" in warn_call_args


def test_is_token_expired_or_expiring_with_attribute_error(session_service):
    """Test _is_token_expired_or_expiring when AttributeError occurs."""
    # Create a session with problematic access to expiry attributes
    session_service.set_session(MagicMock())

    # Mock the sessionService module's logger instead
    with patch(
        "lseg_analytics_jupyterlab.src.classes.sessionService.logger_main"
    ) as mock_logger:
        # Force an AttributeError by making the session have no expiry_date_time_ms
        session_service._current_session.expiry_date_time_ms = None
        # Patch getattr to raise AttributeError when called on expires_at
        with patch(
            "lseg_analytics_jupyterlab.src.classes.sessionService.getattr",
            side_effect=AttributeError("Test error"),
        ):
            result = session_service._is_token_expired_or_expiring()

            # Should return True when AttributeError occurs
            assert result is True

            # Should log warning about invalid format
            mock_logger.warn.assert_called()
            # Check that warn was called with a message containing the expected text
            warn_call_args = mock_logger.warn.call_args[0][0]
            assert "[SessionService] Invalid token expiry format:" in warn_call_args


def test_create_without_settings():
    """Test get_session when no token refresh service is available."""
    # Create session service without token refresh service
    with pytest.raises(
        AssertionError, match="Settings are required for SessionService"
    ):
        session_service = SessionService(
            settings=None,
        )


def test_remove_session(user_session, session_service):
    session_service.set_session(user_session)
    session_service.delete_session()
    assert session_service._current_session is None


def test_get_session_with_new_session_and_notification(
    expiring_user_session, session_service
):
    """Test that token refresh triggers client notification with full WebSocket message verification."""
    session_service.set_session(expiring_user_session)

    # Create new session returned by refresh
    new_session = BaseUserSession(
        "test_id",
        "test_user_id",
        "test_user_name",
        "new_access_token",
        "new_refresh_token",
        str(int(time.time() * 1000) + 24 * 3600 * 1000),
    )

    # Mock successful token refresh returning new session
    mock_token_service = MagicMock()
    mock_token_service.proactive_token_refresh.return_value = (
        True,
        "Success",
        new_session,
    )
    session_service._token_refresh_service = mock_token_service

    # Mock WebSocket.send_message_to_client for full verification
    with patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket"
    ) as mock_websocket:
        mock_websocket.send_message_to_client = Mock()

        with patch(
            "lseg_analytics_jupyterlab.src.classes.sessionService.logger_main"
        ) as mock_logger:
            result = session_service.get_session()

            # Should return new session
            assert result == new_session
            assert session_service._current_session == new_session

            # Verify WebSocket was called with correct message
            mock_websocket.send_message_to_client.assert_called_once()

            # Verify the message structure
            call_args = mock_websocket.send_message_to_client.call_args[0][0]
            import json

            message = json.loads(call_args)

            assert message["message_type"] == "TOKEN_UPDATED"
            # Verify id is set to session.id (not user_id) - this is the fix for IDE-2571
            assert message["message"]["session"]["id"] == "test_id"
            assert message["message"]["session"]["customerId"] == "test_user_id"
            assert message["message"]["session"]["userDisplayName"] == "test_user_name"
            assert message["message"]["session"]["accessToken"] == "new_access_token"
            assert message["message"]["session"]["refreshToken"] == "new_refresh_token"
            assert (
                message["message"]["session"]["expiryDatetimeMs"]
                == new_session.expiry_date_time_ms
            )

            # Verify the notification debug message was called (among other debug calls)
            debug_calls = [call.args[0] for call in mock_logger.debug.call_args_list]
            assert (
                "[SessionService] Sent token update notification to client"
                in debug_calls
            )


def test_notify_client_of_token_update_failure(session_service):
    """Test client notification failure handling."""
    test_session = BaseUserSession(
        "test_id", "test_user_id", "test_user_name", "token", "refresh", "123"
    )

    # Mock WebSocket to raise an exception
    with patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket"
    ) as mock_websocket:
        mock_websocket.send_message_to_client.side_effect = Exception("WebSocket error")

        with patch(
            "lseg_analytics_jupyterlab.src.classes.sessionService.logger_main"
        ) as mock_logger:
            # Should not raise exception
            session_service._notify_client_of_token_update(test_session)

            # Verify error was logged
            mock_logger.warn.assert_called_with(
                "[SessionService] Failed to notify client of token update: WebSocket error"
            )
