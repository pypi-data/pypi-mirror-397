from typing import Optional
import time
import json
from lseg_analytics_jupyterlab.src.classes.baseUserSession import BaseUserSession
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
from lseg_analytics_jupyterlab.src.services.tokenRefreshService import (
    TokenRefreshService,
)
from lseg_analytics_jupyterlab.src.constants.message_types import MessageType


class SessionService:
    """
    Enhanced session service that handles both session management and automatic token refresh.
    This centralizes all authentication concerns as suggested in code review.
    Uses the existing TokenRefreshService internally to avoid code duplication.
    """

    def __init__(self, settings: dict) -> None:
        """
        Initialize the session service.

        Args:
            settings: Application settings containing OAuth configuration (required)
        """
        # Current session in memory
        self._current_session: Optional[BaseUserSession] = None
        assert settings is not None, "Settings are required for SessionService"
        self.settings = settings
        self._token_refresh_service = TokenRefreshService(settings=settings)

    def set_session(self, session: BaseUserSession) -> None:
        """Set the current user session."""
        self._current_session = session

    def get_session(self) -> Optional[BaseUserSession]:
        """
        Get the current session with automatic token refresh if needed.

        Returns either a valid session with fresh token or None if refresh fails.
        """
        logger_main.debug("[SessionService] get_session() called")

        # Return None if no session exists
        if self._current_session is None:
            logger_main.debug("[SessionService] No session in store, returning None")
            return None

        logger_main.debug(
            f"[SessionService] Session found - user_id: {getattr(self._current_session, 'user_id', 'N/A')}"
        )
        logger_main.debug(
            f"[SessionService] Session expiry: {getattr(self._current_session, 'expiry_date_time_ms', 'N/A')}"
        )

        # Check if token needs refresh directly to avoid circular dependency
        token_expiring = self._is_token_expired_or_expiring()
        logger_main.debug(
            f"[SessionService] Token expiring check result: {token_expiring}"
        )

        if self._token_refresh_service and token_expiring:
            logger_main.debug(
                "[SessionService] Token expiring, attempting automatic refresh"
            )

            # Attempt token refresh using existing TokenRefreshService
            logger_main.debug(
                "[SessionService] Calling TokenRefreshService.proactive_token_refresh()"
            )
            success, message, new_session = (
                self._token_refresh_service.proactive_token_refresh(
                    session=self._current_session
                )
            )
            logger_main.debug(
                f"[SessionService] Token refresh result - success: {success}, message: {message}"
            )

            if not success:
                logger_main.warn(f"[SessionService] Token refresh failed: {message}")
                logger_main.debug(
                    "[SessionService] Clearing current session due to refresh failure"
                )
                self._current_session = None
                return None
            else:
                logger_main.debug("[SessionService] Token refreshed successfully")
                if new_session:
                    logger_main.debug(
                        "[SessionService] Updating current session with new session"
                    )
                    self._current_session = new_session
                    logger_main.debug(
                        f"[SessionService] New session expiry: {getattr(new_session, 'expiry_date_time_ms', 'N/A')}"
                    )

                    # Notify client of token update via WebSocket
                    self._notify_client_of_token_update(new_session)
                else:
                    logger_main.debug(
                        "[SessionService] No new session returned, keeping existing session"
                    )

        logger_main.debug("[SessionService] Returning session to caller")
        return self._current_session

    def _notify_client_of_token_update(self, session: BaseUserSession) -> None:
        """
        Send updated token information to the client via WebSocket.

        This ensures client and server stay in sync when server-side token refresh occurs
        (e.g., during API proxy calls). Prevents client from using stale refresh tokens.

        Args:
            session: The updated session with new tokens
        """
        try:
            # Import here to avoid circular dependency issues
            from lseg_analytics_jupyterlab.src.handlers.webSocketHandler import (
                WebSocket,
            )

            # Create message with updated token info
            token_update_message = {
                "message_type": MessageType.TOKEN_UPDATED,
                "message": {
                    "session": {
                        "id": session.id,
                        "accessToken": session.access_token,
                        "refreshToken": session.refresh_token,
                        "customerId": session.user_id,
                        "userDisplayName": session.user_display_name,
                        "expiryDatetimeMs": session.expiry_date_time_ms,
                        "diagnostics": session.diagnostics,
                    }
                },
            }

            message_json = json.dumps(token_update_message)
            WebSocket.send_message_to_client(message_json)

            logger_main.debug(
                "[SessionService] Sent token update notification to client"
            )

        except Exception as e:
            # Don't fail the token refresh if client notification fails
            logger_main.warn(
                f"[SessionService] Failed to notify client of token update: {e}"
            )

    def _is_token_expired_or_expiring(self) -> bool:
        """Check if the current token is expired or expiring soon."""
        logger_main.debug("[SessionService] Checking if token is expired or expiring")

        if not self._current_session:
            logger_main.debug(
                "[SessionService] No current session, considering token expired"
            )
            return False

        try:
            # BaseUserSession uses expiry_date_time_ms for token expiry
            expires_at_str = (
                getattr(self._current_session, "expires_at", None)
                or self._current_session.expiry_date_time_ms
            )
            logger_main.debug(
                f"[SessionService] Token expires_at_str: {expires_at_str}"
            )

            if not expires_at_str:
                logger_main.debug(
                    "[SessionService] No expiry time found, considering token expired"
                )
                return True

            # Convert from milliseconds to seconds for comparison
            expires_at_ms = int(expires_at_str)
            expires_at = expires_at_ms // 1000  # Convert milliseconds to seconds
            current_time = int(time.time())

            logger_main.debug(
                f"[SessionService] Current time: {current_time}, Token expires at: {expires_at} (converted from {expires_at_ms}ms)"
            )

            # Check if token expires within buffer time (2 minutes)
            buffer_seconds = 120
            time_until_expiry = expires_at - current_time
            is_expiring = time_until_expiry <= buffer_seconds

            logger_main.debug(
                f"[SessionService] Time until expiry: {time_until_expiry}s, Buffer: {buffer_seconds}s, Is expiring: {is_expiring}"
            )

            return is_expiring

        except (ValueError, AttributeError) as e:
            logger_main.warn(f"[SessionService] Invalid token expiry format: {e}")
            return True

    def delete_session(self) -> None:
        """Delete the current session."""
        if self._current_session is not None:
            self._current_session = None
