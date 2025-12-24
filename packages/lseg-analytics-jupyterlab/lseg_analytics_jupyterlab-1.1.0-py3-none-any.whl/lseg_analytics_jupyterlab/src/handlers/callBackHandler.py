import uuid
import jwt
import time
from jupyter_server.base.handlers import APIHandler
import requests
from lseg_analytics_jupyterlab.src.classes.baseUserSession import BaseUserSession
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
from lseg_analytics_jupyterlab.src.handlers.webSocketHandler import WebSocket
from lseg_analytics_jupyterlab.src.utils.serverUtils import create_response
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
import json


class CallBackHandler(APIHandler):
    """
    The CallBackHandler class handles the callback from the proxy server. It retrieves the authorization code and uses \
    the code verifier from the application settings to request tokens from the token endpoint. If successful, it returns
    the tokens. Otherwise, it returns an error message.
    """

    def initialize(self, session_service: SessionService):
        assert session_service is not None
        self._session_service = session_service

    def get(self):
        try:
            code = self.get_argument("code")
            code_verifier = self.settings["code_verifier"]
            response = requests.post(
                self.settings["TOKEN_URL"],
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.settings["redirect_uri"],
                    "client_id": self.settings["CLIENT_ID"],
                    "code_verifier": code_verifier,
                },
            )

            if response.status_code == 200:
                tokens = response.json()
                id_token = tokens.get("id_token")
                access_token = tokens.get("access_token")
                refresh_token = tokens.get("refresh_token")
                expires_in = tokens.get("expires_in")

                host = self.settings["BASE_URL"]

                # setup a PyJWKClient to get the appropriate signing key
                jwks_client = jwt.PyJWKClient(f"{host}/pf/JWKS")

                # get signing_key from id_token
                signing_key = jwks_client.get_signing_key_from_jwt(id_token)

                # decode id_token to get user_id and user_name
                # Reference CIAM doc: https://confluence.refinitiv.com/display/CIAMDOC/JWT+Token+Validation
                # TODO: correct typing checks for decoded_token
                decoded_token = jwt.decode(  # type: ignore
                    id_token,
                    key=signing_key.key,  # type: ignore
                    issuer=host,
                    algorithms=["ES256", "RS256"],
                    options={"require": ["exp", "iss", "sub"]},
                    audience=self.settings["CLIENT_ID"],
                )
                user_id = decoded_token.get("sub") or ""
                user_name = decoded_token.get("name") or ""
                current_time_ms = int(time.time() * 1000)
                expiry_timestamp_ms = current_time_ms + (expires_in * 1000)
                # store token
                session_id = str(uuid.uuid4())
                user_session = BaseUserSession(
                    session_id,
                    user_id,
                    user_name,
                    access_token,
                    refresh_token,
                    expiry_timestamp_ms,
                )
                # Update diagnostics with actual timestamps
                user_session.diagnostics["sessionStartTimestampMs"] = current_time_ms
                user_session.diagnostics["lastTokenRefreshTimestampMs"] = (
                    current_time_ms
                )
                user_session.diagnostics["refreshCount"] = 0
                self._session_service.set_session(user_session)
                session_dict = {
                    "id": user_session.id,
                    "customerId": user_session.user_id,
                    "userDisplayName": user_session.user_display_name,
                    "accessToken": user_session.access_token,
                    "refreshToken": user_session.refresh_token,
                    "expiryDatetimeMs": user_session.expiry_date_time_ms,
                    "diagnostics": user_session.diagnostics,
                }

                # logging
                logger_main.info("Tokens retrieved successfully")
                self.finish(create_response("success", "Tokens retrieved successfully"))
                WebSocket.send_message_to_client(
                    json.dumps(
                        {
                            "message_type": "AUTHENTICATION",
                            "message": {
                                "content": "tokens_received",
                                "log_level": "INFO",
                                "session": session_dict,
                            },
                        }
                    )
                )
            else:
                self.set_status(400)
                error_message = "Authentication failed, please try again."
                logger_main.error("Authentication failed, please try again.")
                self.finish(create_response("error", error_message))
                WebSocket.send_message_to_client(
                    json.dumps(
                        {
                            "message_type": "AUTHENTICATION",
                            "message": {"content": "auth_fail", "log_level": "ERROR"},
                        }
                    )
                )
        except Exception as e:
            self.set_status(500)
            error_message = f"An unexpected error occurred: {str(e)}"
            logger_main.error(error_message)
            self.finish(create_response("error", error_message))
            WebSocket.send_message_to_client(
                json.dumps(
                    {
                        "message_type": "AUTHENTICATION",
                        "message": {
                            "content": "unexpected_error",
                            "log_level": "ERROR",
                        },
                    }
                )
            )
