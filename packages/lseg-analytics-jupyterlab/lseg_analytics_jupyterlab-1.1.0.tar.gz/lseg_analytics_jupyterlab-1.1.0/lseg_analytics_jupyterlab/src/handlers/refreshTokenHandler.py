import json
from tornado.web import RequestHandler
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
from lseg_analytics_jupyterlab.src.utils.serverUtils import create_response
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main


class RefreshTokenHandler(RequestHandler):
    """
    Handler for refreshing OAuth tokens.
    Now uses SessionService.get_session() which handles token refresh automatically.
    This maintains API compatibility while leveraging centralized token refresh logic.
    """

    def initialize(self, session_service: SessionService):
        """
        Store session_service passed from main.py for use in handler methods.
        """
        self.session_service = session_service

    def post(self):
        """
        Handle POST request to refresh tokens.

        This endpoint can be called by clients to trigger token refresh.
        The actual refresh logic is now centralized in SessionService.get_session().
        """
        try:
            # Extract refresh token from request (for API compatibility)
            refresh_token = self._extract_refresh_token_from_request()
            if not refresh_token:
                return

            # Security check: Validate that supplied refresh token matches stored token
            # This prevents unauthorized access to the refresh endpoint from any local caller
            current_session = self.session_service._current_session
            if not current_session or current_session.refresh_token != refresh_token:
                logger_main.warn("[RefreshTokenHandler] Invalid refresh token provided")
                self.set_status(401)
                self.finish(create_response("error", "Invalid refresh token"))
                return

            # Get session which will automatically refresh if needed
            session = self.session_service.get_session()

            if session is None:
                logger_main.warn(
                    "[RefreshTokenHandler] No session available or token refresh failed"
                )

                # Check if this is a configuration error (400) or server error (500)
                # Try to get more specific error details from the token refresh service
                if hasattr(self.session_service, "_token_refresh_service"):
                    # Check configuration first
                    valid, msg, _, _ = (
                        self.session_service._token_refresh_service._validate_configuration()
                    )
                    if not valid:
                        # 400 for client/configuration errors
                        self.set_status(400)
                        self.finish(
                            create_response("error", f"Configuration error: {msg}")
                        )
                        return

                # 500 for server errors (network issues, token server problems, etc.)
                self.set_status(500)
                self.finish(
                    create_response(
                        "error", "Internal server error during token refresh"
                    )
                )
                return

            # Return the refreshed token information
            # Note: format must match the RefreshTokenResponse interface defined in client/src/core/networkServices/interface.ts
            response_data = {
                "accessToken": session.access_token,
                "refreshToken": session.refresh_token,
                "expiresAt": session.expiry_date_time_ms,
            }

            logger_main.info(
                "[RefreshTokenHandler] Token refresh completed successfully"
            )
            self.finish(
                create_response(
                    "success", "Token refreshed successfully", response_data
                )
            )

        except Exception as e:
            logger_main.warn(
                f"[RefreshTokenHandler] Exception during token refresh: {str(e)}"
            )
            self.set_status(500)
            self.finish(
                create_response("error", "Internal server error during token refresh")
            )

    def _extract_refresh_token_from_request(self):
        """Extract and validate refresh token from request body."""
        body = (
            json.loads(self.request.body.decode("utf-8")) if self.request.body else {}
        )
        refresh_token = body.get("refresh_token")

        if not refresh_token:
            logger_main.debug("[RefreshTokenHandler] No refresh_token provided")
            self.set_status(400)
            self.finish(create_response("error", "Missing refresh_token"))
            return None

        return refresh_token
