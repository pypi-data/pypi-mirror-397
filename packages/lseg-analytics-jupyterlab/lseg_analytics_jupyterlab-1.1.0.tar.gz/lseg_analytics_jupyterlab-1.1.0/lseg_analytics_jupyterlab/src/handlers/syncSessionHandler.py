import json
import uuid
from typing import cast


from tornado.web import RequestHandler

from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
from lseg_analytics_jupyterlab.src.utils.serverUtils import create_response
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
from lseg_analytics_jupyterlab.src.classes.baseUserSession import BaseUserSession
from lseg_analytics_jupyterlab.src.classes.proxyServer import ProxyServer


class SyncSessionHandler(RequestHandler):
    """
    Handler for synchronizing client and server session state after server restart.

    This handler is called during application initialization to make sure the server
    is initialized:
    1. it ensures the proxy server is running, and
    2. overwrites the server session with the data supplied from the client

    """

    def initialize(
        self,
        session_service: SessionService,
        proxy_server: ProxyServer,
    ):
        """
        Store session_service passed from main.py for use in handler methods.

        Args:
            session_service: The session service instance
        """
        self.session_service = session_service
        self.proxy_server = proxy_server

    def post(self):
        """
        Handle POST request to synchronize client and server session.

        Expected request body:

            "id": "session-id",
            "customerId": "user-id",
            "userDisplayName": "User Name",
            "accessToken": "...",
            "refreshToken": "...",
            "expiryDatetimeMs": "1234567890"
        }

        Returns:
            200: Session synchronized successfully
            400: Invalid request body
            500: Internal server error
        """
        try:
            # Extract client session from request
            client_session = self._extract_session_from_request()
            if not client_session:
                return

            self._log_sync_diagnostics(client_session)

            if not self._ensure_proxy_server_running():
                return

            self._restore_session_from_client(client_session)

            self.finish(
                create_response(
                    "success", "Session restored to server from client storage"
                )
            )

        except Exception as e:
            logger_main.error(
                f"[SyncSessionHandler] Exception during session sync: {str(e)}"
            )
            self.set_status(500)
            self.finish(
                create_response("error", "Internal server error during session sync")
            )

    def _extract_session_from_request(self):
        """
        Extract and validate session data from request body.

        Returns:
            BaseUserSession if valid, None otherwise (with error response sent)
        """
        try:
            body = (
                json.loads(self.request.body.decode("utf-8"))
                if self.request.body
                else {}
            )
            # Extract required fields
            session_id = body.get("id")
            user_id = body.get("customerId")
            user_display_name = body.get("userDisplayName")
            access_token = body.get("accessToken")
            refresh_token = body.get("refreshToken")
            expiry_datetime_ms = body.get("expiryDatetimeMs")
            diagnostics = body.get("diagnostics")

            # Validate required fields

            if not (
                session_id
                and user_id
                and user_display_name
                and access_token
                and refresh_token
            ):
                logger_main.warn(
                    "[SyncSessionHandler] Missing required fields in request"
                )
                self.set_status(400)
                self.finish(
                    create_response(
                        "error",
                        "Missing required session fields (id, customerId, userDisplayName, accessToken, refreshToken, expiryDatetimeMs)",
                    )
                )
                return None

            # Create BaseUserSession object
            client_session = BaseUserSession(
                session_id,
                user_id,
                user_display_name,
                access_token,
                refresh_token,
                str(expiry_datetime_ms),
                diagnostics,
            )

            return client_session

        except json.JSONDecodeError as e:
            logger_main.warn(
                f"[SyncSessionHandler] Invalid JSON in request body: {str(e)}"
            )
            self.set_status(400)
            self.finish(create_response("error", "Invalid JSON in request body"))
            return None
        except Exception as e:
            logger_main.error(
                f"[SyncSessionHandler] Error extracting session from request: {str(e)}"
            )
            self.set_status(400)
            self.finish(create_response("error", f"Invalid request: {str(e)}"))
            return None

    def _restore_session_from_client(self, client_session: BaseUserSession):
        """
        Restore server session from client-provided session data.
        This will overwrite the current server session, if there is one.

        Args:
            client_session: The session object from the client
        """
        self.session_service.set_session(client_session)
        logger_main.info(
            f"[SyncSessionHandler] Session restored: user={client_session.user_display_name}, id={client_session.id}"
        )

    def _ensure_proxy_server_running(self) -> bool:
        """Ensure the proxy server is running after session synchronization."""

        state = uuid.uuid4()
        host = cast(str, self.request.host)  # type: ignore
        lab_host = host.split(":")[0]
        lab_port = host.split(":")[1]

        if not self.proxy_server.is_started:
            try:
                port_range = [
                    self.settings["port_range"]["start"],
                    self.settings["port_range"]["end"],
                ]
                self.proxy_server.start(port_range, lab_host, lab_port, state=state)

            except Exception as e:
                error_message = str(e)
                logger_main.error("Error starting proxy server")

                # Check if this is a port availability error for specific error type
                from lseg_analytics_jupyterlab.src.classes.proxyServer import (
                    PORT_UNAVAILABLE_ERROR_MSG_TEMPLATE,
                )

                if PORT_UNAVAILABLE_ERROR_MSG_TEMPLATE.split("{")[0] in error_message:
                    self.finish(
                        create_response("error", "port_unavailable", error_message)
                    )
                else:
                    self.finish(
                        create_response("error", "proxy_server_error", error_message)
                    )
                return False
        else:
            self.proxy_server.update_proxy_server_data(lab_host, lab_port, state)
        return True

    def _log_sync_diagnostics(self, client_session: BaseUserSession):
        # Get current server session (if any)
        server_session = self.session_service._current_session

        if not server_session:
            # this should only happen when the server has restarted
            logger_main.debug("[SyncSessionHandler] No server session found")
        else:
            # This will happen if the browser was refreshed while the server was running.
            # We expect the server and client sessions to be in sync. Log if they match or not
            # to help detect logic issues.
            if self._sessions_match(server_session, client_session):
                logger_main.debug(
                    "[SyncSessionHandler] Server and client sessions match"
                )
            else:
                logger_main.warn(
                    "[SyncSessionHandler] Session mismatch detected! "
                    f"Server session: {server_session.id}, Client session: {client_session.id}"
                )

    def _sessions_match(
        self, server_session: BaseUserSession, client_session: BaseUserSession
    ) -> bool:
        """
        Check if server and client sessions match.

        We consider sessions to match if they have the same:
        - Session ID
        - Refresh token

        Args:
            server_session: The session stored on the server
            client_session: The session from the client

        Returns:
            True if sessions match, False otherwise
        """
        return (
            server_session.id == client_session.id
            and server_session.refresh_token == client_session.refresh_token
        )
