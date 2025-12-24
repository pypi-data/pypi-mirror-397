from urllib.parse import urlencode
from jupyter_server.base.handlers import APIHandler
from lseg_analytics_jupyterlab.src.classes.proxyServer import ProxyServer
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main

from lseg_analytics_jupyterlab.src.utils.serverUtils import (
    create_response,
    fetch_openid_configuration,
)
from typing import Dict, Any, cast
import uuid
import pkce


class SignInHandler(APIHandler):
    """
    This class handles the /api/lseg-analytics-jupyterlab/signin route.

    When called, it searches for an available port within the range provided by the webapp settings,
    which can be configured in the config file. It then starts a proxy server on the available port.

    It also fetches the OpenID configuration and constructs an authorization URL. This URL directs
    to the Ping authorization page, which prompts the user to sign in with their username and password.
    """

    _proxy_server: ProxyServer

    def initialize(self, proxy_server: ProxyServer) -> None:
        assert proxy_server is not None
        self._proxy_server = proxy_server

    def get(self) -> None:

        state = generate_state()
        host = cast(str, self.request.host)  # type: ignore
        lab_host = host.split(":")[0]
        lab_port = host.split(":")[1]

        try:
            if not self._proxy_server.is_started:
                try:
                    port_range = [
                        self.settings["port_range"]["start"],
                        self.settings["port_range"]["end"],
                    ]
                    self._proxy_server.start(port_range, lab_host, lab_port, state)

                except Exception as e:
                    error_message = str(e)
                    logger_main.error("Error starting proxy server")

                    # Check if this is a port availability error for specific error type
                    from lseg_analytics_jupyterlab.src.classes.proxyServer import (
                        PORT_UNAVAILABLE_ERROR_MSG_TEMPLATE,
                    )

                    if (
                        PORT_UNAVAILABLE_ERROR_MSG_TEMPLATE.split("{")[0]
                        in error_message
                    ):
                        self.finish(
                            create_response("error", "port_unavailable", error_message)
                        )
                    else:
                        self.finish(
                            create_response(
                                "error", "proxy_server_error", error_message
                            )
                        )
                    return
            else:
                self._proxy_server.update_proxy_server_data(lab_host, lab_port, state)

            proxy_server_port = self._proxy_server.proxy_port
            redirect_uri = (
                f'{self.settings["proxy_server_host"]}:{proxy_server_port}/auth'
            )
            self.settings["redirect_uri"] = redirect_uri

            code_verifier = generate_code_verifier()
            code_challenge = generate_code_challenge(code_verifier)
            self.settings["code_verifier"] = code_verifier

            try:
                openid_config = fetch_openid_configuration(self.settings["BASE_URL"])
                self.settings["AUTH_URL"] = openid_config["authorization_endpoint"]
                self.settings["TOKEN_URL"] = openid_config["token_endpoint"]
            except Exception as e:
                logger_main.error("Error fetching OpenID configuration")
                self.finish(
                    create_response(
                        "error", "Error fetching OpenID configuration", str(e)
                    )
                )
                return

            params: Dict[str, Any] = {
                "response_type": "code",
                "client_id": self.settings["CLIENT_ID"],
                "redirect_uri": redirect_uri,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "state": state,
                # remove scope "trapi.data.quantitative-analytics.read" in the future. It was added as a workaround. Refer to https://jira.refinitiv.com/browse/IDE-2090
                "scope": "openid profile trapi lfa trapi.platform.iam.acl_service trapi.data.quantitative-analytics.read",
                "response_mode": "query",
            }

            auth_url = f"{self.settings['AUTH_URL']}?{urlencode(params)}"
            logger_main.info("Returning authentication URL to client")

            self.finish(
                create_response(
                    "success", "auth_url", {"url": auth_url, "port": proxy_server_port}
                )
            )

        except RuntimeError as e:
            logger_main.error(str(e))
            self.finish(create_response("error", "runtime_error", str(e)))


def generate_state() -> uuid.UUID:
    state = uuid.uuid4()
    return state


def generate_code_verifier() -> str:
    code_verifier = pkce.generate_code_verifier(length=128)
    return code_verifier


def generate_code_challenge(code_verifier: str) -> str:
    code_challenge = pkce.get_code_challenge(code_verifier)
    return code_challenge
