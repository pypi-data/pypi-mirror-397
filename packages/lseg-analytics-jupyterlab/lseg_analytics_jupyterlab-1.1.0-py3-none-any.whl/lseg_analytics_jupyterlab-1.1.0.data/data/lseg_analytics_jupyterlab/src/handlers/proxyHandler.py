from typing import Optional, Any, ClassVar
import http.server
import urllib.parse
import json
import requests
import os
from requests.exceptions import RequestException
from lseg_analytics_jupyterlab.src.classes.loggers import logger_proxy
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
from lseg_analytics_jupyterlab.src.classes.baseUserSession import BaseUserSession
from lseg_analytics_jupyterlab.src.handlers.webSocketHandler import WebSocket
from lseg_analytics_jupyterlab.src.utils.serverUtils import (
    ERROR_INVALID_STATE,
    ERROR_UNEXPECTED,
)
import uuid
from lseg_analytics_jupyterlab.src.classes.enablementStatusService import (
    EnablementStatusService,
)

json_type = "application/json"
AUTHORIZATION_ERROR_MESSAGE = (
    "Cannot connect to the LSEG Financial Analytics platform because you are not authorized to the extension. "
    "Please contact the LSEG support team."
)


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    """
    The ProxyHandler class is a request handler for proxy server requests. It redirects these requests to the Jupyter server callback URL.
    It sets the lab host and port information, handles GET and POST requests, and manages responses based on the path.
    """

    lab_host: ClassVar[Optional[str]] = None
    lab_port: ClassVar[Optional[str]] = None
    expected_state: ClassVar[Optional[uuid.UUID]] = None
    _session_service: SessionService
    _enablement_status_service: EnablementStatusService
    settings: Any

    def __init__(
        self,
        session_service: SessionService,
        settings: Any,
        enablement_status_service: EnablementStatusService,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        assert session_service is not None
        assert enablement_status_service is not None
        self._session_service = session_service
        self.settings = settings
        self._enablement_status_service = enablement_status_service
        super().__init__(*args, **kwargs)
        # Note: Do NOT call get_session() here - it can trigger unnecessary token refresh
        # during proxy server initialization, creating race conditions during OAuth flow

    def _is_proxy_enabled(self) -> bool:
        user_settings_dir = self.settings.get("user_settings_dir")
        if not user_settings_dir:
            logger_proxy.debug("[Proxy] No user_settings_dir configured")
            return False

        settings_file = os.path.join(
            user_settings_dir, "lseg-analytics-jupyterlab", "plugin.jupyterlab-settings"
        )
        logger_proxy.debug(f"[Proxy] Looking for settings file: {settings_file}")

        if not os.path.exists(settings_file):
            logger_proxy.debug(f"[Proxy] Settings file does not exist: {settings_file}")
            return False

        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                user_settings = json.load(f)

            logger_proxy.debug(f"[Proxy] Settings file content: {user_settings}")
            enabled = user_settings.get("enableAutomaticAuthentication", False)
            logger_proxy.debug(
                f"[Proxy] enableAutomaticAuthentication value: {enabled}"
            )
            return enabled

        except Exception as e:
            logger_proxy.warn(f"[Proxy] Failed to read settings file: {e}")
            return False

    @classmethod
    def set_lab_info(
        cls, host: Optional[str], port: Optional[str], state: Optional[uuid.UUID]
    ) -> None:
        if host is None:
            raise ValueError("Host cannot be null.")
        if port is None:
            raise ValueError("Port cannot be null.")
        if state is None:
            raise ValueError("State cannot be null.")

        cls.lab_host = host
        cls.lab_port = port
        cls.expected_state = state

    def do_GET(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        logger_proxy.info("The path is: {path}".format(path=path))
        if path == "/status":
            self.handle_status_get()
        elif path.startswith("/financials/"):
            self.handle_financials()
        elif path.startswith("/yieldbook/"):
            self.handle_yieldbook()
        elif path == "/auth":
            self.handle_proxy()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        self.handle_request()

    def do_PUT(self) -> None:
        self.handle_request()

    def do_DELETE(self) -> None:
        self.handle_request()

    def handle_request(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path.startswith("/financials/"):
            self.handle_financials()
        elif self.path.startswith("/yieldbook/"):
            self.handle_yieldbook()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_status_get(self) -> None:
        try:
            print("Handling GET request for /status")
            self.send_response(200)
            self.send_header("Content-type", json_type)
            self.end_headers()

            response_data = {
                "lsegProxyEnabled": self._is_proxy_enabled(),
            }

            json_response = json.dumps(response_data)
            self.wfile.write(json_response.encode("utf-8"))
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
            # Client closed connection before we could send response - this is normal
            logger_proxy.debug(f"Client disconnected during /status request: {e}")
        except Exception as e:
            logger_proxy.error(f"Unexpected error in handle_status_get: {e}")

    def handle_financials(self) -> None:
        self._handle_backend_request("financials")

    def handle_yieldbook(self) -> None:
        self._handle_backend_request("yieldbook")

    def _handle_backend_request(self, api_name: str) -> None:
        logger_proxy.info(
            f"[Proxy] Starting handle_{api_name} for {self.command} {self.path}"
        )

        if not self._is_proxy_enabled():
            # NOTE: Keep this response (status code & semantics) aligned with the VSCode extension's
            # LoopbackServer.featureProxyEnabled middleware.
            # VSCode currently returns HTTP 400 when the proxy feature is disabled.
            logger_proxy.warn(
                "[Proxy] Request blocked - automatic authentication disabled"
            )
            self.send_response(400)
            self.send_header("Content-type", json_type)
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Proxy is disabled in user settings"}).encode(
                    "utf-8"
                )
            )
            return

        backend_url = self.settings.get("SDK_API")
        path = self.path
        full_url = f"{backend_url}{path}"
        logger_proxy.info(f"[Proxy] Target URL: {full_url}")

        # Get session with automatic token refresh (centralized in SessionService)
        logger_proxy.debug("[Proxy] Requesting session from SessionService...")
        session = self._session_service.get_session()
        if session is None:
            logger_proxy.error(
                "[Proxy] SessionService.get_session() returned None - no active session or token refresh failed"
            )
            self.send_response(401)
            self.send_header("Content-type", json_type)
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"error": "No active session found or token refresh failed"}
                ).encode("utf-8")
            )
            return

        logger_proxy.info(
            f"[Proxy] Session obtained - access_token length: {len(session.access_token) if session.access_token else 0}"
        )
        logger_proxy.debug(
            f"[Proxy] Session expiry: {getattr(session, 'expiry_date_time_ms', 'N/A')}"
        )

        if not self._user_has_lfa_access():
            logger_proxy.warn(
                "[Proxy] Request blocked - user is not authorized for LSEG Financial Analytics"
            )
            self.send_response(403)
            self.send_header("Content-type", json_type)
            self.end_headers()
            try:
                self.wfile.write(
                    json.dumps({"error": AUTHORIZATION_ERROR_MESSAGE}).encode("utf-8")
                )
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
                logger_proxy.debug(
                    f"[Proxy] Client disconnected while sending authorization error: {e}"
                )
            return

        access_token = session.access_token

        extension_version = self.settings["extension_version"]
        sdk_user_agent = self.headers.get("User-Agent", "unknown")
        user_agent = f"lseg-ide-jupyter/v{extension_version} for {sdk_user_agent}"
        unique_req_id = str(uuid.uuid4())
        headers = {
            "Content-Type": json_type,
            "Authorization": "Bearer " + access_token,
            "User-Agent": user_agent,
            "x-lseg-client-requestid": unique_req_id,
        }

        logger_proxy.info(f"[Proxy] Request ID: {unique_req_id}")
        logger_proxy.debug(
            f"[Proxy] Request headers prepared - User-Agent: {user_agent}"
        )

        try:
            logger_proxy.info(f"[Proxy] Making {self.command} request to backend...")

            if self.command == "GET":
                response = requests.get(full_url, headers=headers)

            elif self.command == "POST":
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                logger_proxy.debug(f"[Proxy] POST data length: {len(post_data)}")
                response = requests.post(full_url, headers=headers, data=post_data)

            elif self.command == "PUT":
                content_length = int(self.headers["Content-Length"])
                put_data = self.rfile.read(content_length)
                logger_proxy.debug(f"[Proxy] PUT data length: {len(put_data)}")
                response = requests.put(full_url, headers=headers, data=put_data)

            elif self.command == "DELETE":
                response = requests.delete(full_url, headers=headers)

            else:
                logger_proxy.warn(
                    f"[Proxy] Method not allowed for {api_name}: {self.command}"
                )
                self.send_response(405)
                self.send_header("Content-type", json_type)
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "Method not allowed"}).encode("utf-8")
                )
                return

            logger_proxy.info(
                f"[Proxy] Backend response - Status: {response.status_code}, Content-Length: {len(response.content)}"
            )

            # Log specific error responses that might indicate token issues
            if response.status_code == 401:
                logger_proxy.error(
                    "[Proxy] Backend returned 401 Unauthorized - token may be expired or invalid"
                )
                logger_proxy.debug(
                    "[Proxy] Response content: {response.content[:500]}..."
                )  # First 500 chars
            elif response.status_code == 403:
                logger_proxy.error(
                    "[Proxy] Backend returned 403 Forbidden - access denied"
                )
                logger_proxy.debug(
                    f"[Proxy] Response content: {response.content[:500]}..."
                )
            elif response.status_code >= 400:
                logger_proxy.warn(
                    f"[Proxy] Backend returned error {response.status_code}"
                )
                logger_proxy.debug(
                    f"[Proxy] Response content: {response.content[:500]}..."
                )

            self.send_response(response.status_code)
            self.send_header("Content-type", json_type)
            self.end_headers()

            try:
                self.wfile.write(response.content)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
                logger_proxy.debug(
                    f"[Proxy] Client disconnected while sending response: {e}"
                )
                return

            logger_proxy.info(
                f"[Proxy] Successfully proxied {api_name} {self.command} request - final status: {response.status_code}"
            )

        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
            logger_proxy.debug(
                f"[Proxy] Client disconnected during request processing: {e}"
            )
        except RequestException as e:
            logger_proxy.error(
                f"[Proxy] RequestException during {self.command} to {full_url}: {str(e)}"
            )
            try:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                logger_proxy.debug(
                    "[Proxy] Client disconnected while sending error response"
                )
        except Exception as e:
            logger_proxy.error(
                f"[Proxy] Unexpected exception during {self.command} to {full_url}: {str(e)}"
            )
            try:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Internal server error: {str(e)}".encode("utf-8"))
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                logger_proxy.debug(
                    "[Proxy] Client disconnected while sending error response"
                )

    def _user_has_lfa_access(self) -> bool:
        has_access = self._enablement_status_service.user_has_lfa_access()
        logger_proxy.debug(f"[Proxy] Cached enablement check returned {has_access}")
        return has_access

    def handle_proxy(self) -> None:
        try:
            query = urllib.parse.urlparse(self.path).query
            code = urllib.parse.parse_qs(query).get("code", [None])[0]
            state = urllib.parse.parse_qs(query).get("state", [None])[0]

            if state is None or str(self.expected_state) != state:
                raise ValueError(ERROR_INVALID_STATE)

            if code:
                callback_url = f"//{self.lab_host}:{self.lab_port}/api/lseg-analytics-jupyterlab/callback/?code={code}"
                logger_proxy.info("Redirecting to callback")
                self.send_response(302)
                self.send_header("Location", callback_url)
                self.end_headers()
            else:
                logger_proxy.warn("Bad request")
                self.send_response(400)
                self.end_headers()
        except Exception as e:
            # send error message to client in case of state mismatches
            logger_proxy.error(ERROR_UNEXPECTED)
            WebSocket.send_message_to_client(
                json.dumps(
                    {
                        "message_type": "AUTHENTICATION",
                        "message": {"content": ERROR_UNEXPECTED, "log_level": "ERROR"},
                    }
                )
            )
            self.send_response(500, str(e))
            self.end_headers()
