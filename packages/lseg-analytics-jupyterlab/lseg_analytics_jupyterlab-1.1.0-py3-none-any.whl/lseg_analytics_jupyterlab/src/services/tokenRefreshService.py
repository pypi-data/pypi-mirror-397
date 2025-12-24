import json
import time
import requests
from typing import Tuple, Optional, Dict, Any, TYPE_CHECKING, cast
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
from lseg_analytics_jupyterlab.src.utils.serverUtils import ensure_auth_settings

if TYPE_CHECKING:
    from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
    from lseg_analytics_jupyterlab.src.classes.baseUserSession import BaseUserSession


class TokenRefreshService:
    """
    Service class for handling OAuth token refresh operations.
    This class contains the core token refresh logic without depending on Tornado RequestHandler.
    """

    def __init__(self, settings: Optional[Dict[str, Any]]):
        """
        Initialize the token refresh service.

        Args:
            settings: Application settings containing OAuth configuration (can be None for testing)
        """
        self.settings = settings

    def perform_token_refresh(
        self, refresh_token: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Public method to perform token refresh using the provided refresh token.

        Args:
            refresh_token: The refresh token to use for getting new tokens

        Returns:
            tuple: (success: bool, message: str, new_tokens: dict or None)
        """
        try:
            # Validate configuration - will only continue if valid
            valid, msg, token_url, client_id = self._validate_configuration()
            if not valid:
                # 400 for missing config (client error)
                return False, f"Configuration error: {msg}", None

            # At this point, token_url and client_id are guaranteed to be valid strings
            # Prepare token request data
            data = self._prepare_token_request_data(refresh_token, client_id)

            # Make token request
            response = self._make_token_request(token_url, data)

            # Validate response
            valid, msg, tokens = self._validate_token_response(response)
            if not valid or tokens is None:
                return False, msg, None

            # Return tokens data for caller to handle session update
            response_data = {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "expires_in": tokens["expires_in"],
            }

            logger_main.debug(
                "[TokenRefreshService] Token refresh completed successfully"
            )
            return True, "Tokens refreshed successfully", response_data

        except requests.RequestException as e:
            # 500 for server/network errors
            logger_main.error(
                f"[TokenRefreshService] Network error during token refresh: {str(e)}"
            )
            return False, f"Network error: {str(e)}", None
        except Exception as e:
            # 500 for other server errors
            logger_main.error(
                f"[TokenRefreshService] Unexpected error during token refresh: {str(e)}"
            )
            return False, f"Server error: {str(e)}", None

    def proactive_token_refresh(
        self, session: Optional["BaseUserSession"] = None
    ) -> Tuple[bool, str, Optional["BaseUserSession"]]:
        """
        Public method to proactively refresh token if needed.

        Args:
            session: The session to check and refresh (required)

        Returns:
            tuple: (success: bool, message: str, updated_session: BaseUserSession or None)
        """
        try:
            logger_main.info("[TokenRefreshService] proactive_token_refresh() called")

            # Check if session is provided
            if session is None:
                logger_main.error(
                    "[TokenRefreshService] No session provided to proactive_token_refresh"
                )
                return False, "No session provided", None

            logger_main.debug(
                f"[TokenRefreshService] Session provided - user_id: {getattr(session, 'user_id', 'N/A')}"
            )
            logger_main.debug(
                f"[TokenRefreshService] Session expiry: {getattr(session, 'expiry_date_time_ms', 'N/A')}"
            )

            # Check if token refresh is needed
            token_expiring = self._is_token_expired_or_expiring(session)
            logger_main.debug(
                f"[TokenRefreshService] Token expiring check result: {token_expiring}"
            )

            if not token_expiring:
                logger_main.info(
                    "[TokenRefreshService] Token is still valid, no refresh needed"
                )
                return True, "Token is still valid", session

            logger_main.info(
                "[TokenRefreshService] Token needs refresh, attempting proactive refresh"
            )

            # Check if session has refresh_token attribute
            has_refresh_token = (
                hasattr(session, "refresh_token") and session.refresh_token
            )
            logger_main.debug(
                f"[TokenRefreshService] Session has refresh_token: {has_refresh_token}"
            )

            if not has_refresh_token:
                logger_main.error(
                    "[TokenRefreshService] No refresh token available in session"
                )
                return False, "No refresh token available in session", None

            logger_main.debug(
                f"[TokenRefreshService] Refresh token length: {len(session.refresh_token) if session.refresh_token else 0}"
            )

            # Use the current session's refresh token
            logger_main.info(
                "[TokenRefreshService] Calling perform_token_refresh() with session refresh token"
            )
            success, message, token_data = self.perform_token_refresh(
                session.refresh_token
            )
            logger_main.info(
                f"[TokenRefreshService] perform_token_refresh() result - success: {success}, message: {message}"
            )

            if success and token_data:
                logger_main.info(
                    "[TokenRefreshService] Token refresh successful, updating session with new tokens"
                )
                # Update session with new tokens
                new_session = self._update_session_with_tokens(session, token_data)
                logger_main.debug(
                    f"[TokenRefreshService] New session expiry: {getattr(new_session, 'expiry_date_time_ms', 'N/A') if new_session else 'None'}"
                )
                return True, message, new_session
            else:
                logger_main.error(
                    f"[TokenRefreshService] Token refresh failed: {message}"
                )
                return False, message, None

        except Exception as e:
            logger_main.error(
                f"[TokenRefreshService] Exception during proactive refresh: {str(e)}"
            )
            return False, f"Server error: {str(e)}", None

    # PRIVATE METHODS

    def _validate_configuration(self) -> Tuple[bool, str, str, str]:
        """Validate required configuration settings."""
        if not self.settings:
            return False, "Missing configuration settings", "", ""

        try:
            ensure_auth_settings(self.settings)
        except Exception as e:
            return False, str(e), "", ""

        token_url = self.settings.get("TOKEN_URL")
        client_id = self.settings.get("CLIENT_ID")

        # ensure_auth_settings guarantees these are set if no exception
        return True, "Configuration valid", cast(str, token_url), cast(str, client_id)

    def _prepare_token_request_data(
        self, refresh_token: str, client_id: str
    ) -> Dict[str, str]:
        """Prepare the token request payload."""
        return {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
        }

    def _make_token_request(
        self, token_url: str, data: Dict[str, str]
    ) -> requests.Response:
        """Make HTTP request to token endpoint."""
        try:
            logger_main.debug("[TokenRefreshService] Making token refresh request")
            response = requests.post(token_url, data=data, timeout=(10, 30))
            return response
        except requests.RequestException as e:
            logger_main.warn(f"[TokenRefreshService] HTTP request failed: {str(e)}")
            raise

    def _validate_token_response(
        self, response: requests.Response
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Validate token response and extract tokens."""
        if response.status_code != 200:
            logger_main.warn(
                f"[TokenRefreshService] Token refresh failed: {response.status_code} - {response.text}"
            )
            return False, f"Refresh failed with status {response.status_code}", None

        try:
            tokens = response.json()
            access_token = tokens.get("access_token")
            new_refresh_token = tokens.get("refresh_token")
            expires_in = tokens.get("expires_in")

            if not access_token or not new_refresh_token or not expires_in:
                return False, "Invalid token response - missing required fields", None

            return (
                True,
                "Token response valid",
                {
                    "access_token": access_token,
                    "refresh_token": new_refresh_token,
                    "expires_in": expires_in,
                },
            )
        except (json.JSONDecodeError, AttributeError) as e:
            logger_main.warn(
                f"[TokenRefreshService] Failed to parse token response: {str(e)}"
            )
            return False, "Invalid token response format", None

    def _update_session_with_tokens(
        self, session: "BaseUserSession", tokens: Dict[str, Any]
    ) -> Optional["BaseUserSession"]:
        """Update the user session with new tokens."""
        return self._update_session(
            session,
            tokens["access_token"],
            tokens["refresh_token"],
            tokens["expires_in"],
        )

    def _update_session(
        self,
        session: Optional["BaseUserSession"],
        access_token: str,
        new_refresh_token: str,
        expires_in: int,
    ) -> Optional["BaseUserSession"]:
        """Update the user session with new tokens."""
        if session is None:
            logger_main.warn("[TokenRefreshService] No session provided")
            return None

        # Update the session with the new tokens
        session.refresh_token = new_refresh_token
        session.access_token = access_token
        session.expiry_date_time_ms = str(int(time.time() * 1000) + (expires_in * 1000))

        # Update diagnostics
        current_time_ms = int(time.time() * 1000)
        session.diagnostics["lastTokenRefreshTimestampMs"] = current_time_ms
        session.diagnostics["refreshCount"] = (
            session.diagnostics.get("refreshCount", 0) + 1
        )

        logger_main.debug(
            "[TokenRefreshService] Session updated with new refresh token"
        )
        return session

    def _is_token_expired_or_expiring(
        self, session: "BaseUserSession", buffer_seconds: int = 120
    ) -> bool:
        """
        Check if the access token is expired or will expire within buffer_seconds.

        Args:
            session: The session to check
            buffer_seconds (int): Number of seconds before expiry to consider as "expiring" (default: 5 minutes)

        Returns:
            bool: True if token is expired or expiring soon, False otherwise
        """
        logger_main.debug(
            f"[TokenRefreshService] Checking if token is expired or expiring (buffer: {buffer_seconds}s)"
        )

        if session is None:
            logger_main.warn("[TokenRefreshService] No session provided")
            return True  # Assume expired if we can't check

        logger_main.debug(
            f"[TokenRefreshService] Session expiry_date_time_ms: {getattr(session, 'expiry_date_time_ms', 'N/A')}"
        )

        if not session.expiry_date_time_ms:
            logger_main.warn(
                "[TokenRefreshService] No session or expiry time available"
            )
            return True  # Assume expired if we can't check

        try:
            # Convert expiry time from milliseconds to seconds
            expiry_time_seconds = int(session.expiry_date_time_ms) / 1000
            current_time_seconds = time.time()

            logger_main.debug(
                f"[TokenRefreshService] Current time: {current_time_seconds}, Token expires at: {expiry_time_seconds}"
            )

            # Check if token is expired or will expire within buffer_seconds
            time_until_expiry = expiry_time_seconds - current_time_seconds
            is_expiring = time_until_expiry <= buffer_seconds

            logger_main.debug(
                f"[TokenRefreshService] Time until expiry: {time_until_expiry:.1f}s, Is expiring: {is_expiring}"
            )

            if is_expiring:
                logger_main.info(
                    f"[TokenRefreshService] Token expiring in {time_until_expiry:.1f} seconds (buffer: {buffer_seconds}s)"
                )

            return is_expiring

        except (ValueError, TypeError) as e:
            logger_main.warn(
                f"[TokenRefreshService] Error checking token expiry: {str(e)}"
            )
            return True  # Assume expired if we can't parse the time
