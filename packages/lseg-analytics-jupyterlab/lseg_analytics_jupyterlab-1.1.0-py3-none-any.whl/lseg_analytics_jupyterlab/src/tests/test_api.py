# type: ignore
from unittest.mock import Mock
import pytest
import json

from lseg_analytics_jupyterlab.src.handlers.signinHandler import SignInHandler
from jupyter_server.utils import url_path_join
from lseg_analytics_jupyterlab.src.classes.settingsService import SettingsService
import copy


@pytest.fixture
def jp_server_config(jp_server_config):
    jp_server_config["ServerApp"].update({"port": 8888})
    return jp_server_config


@pytest.fixture
def jp_serverapp(jp_serverapp, jp_base_url):
    settings_service = SettingsService("staging")
    config_copy = copy.deepcopy(settings_service.config)
    config_copy["CLIENT_ID"] = "afd238de-256f-4956-9e39-b31bab87b837"
    config_copy["BASE_URL"] = "https://login.stage.ciam.refinitiv.com"

    jp_serverapp.web_app.settings.update(config_copy)

    signin_route = url_path_join(
        jp_base_url, jp_serverapp.web_app.settings["api_prefix"], "/signin"
    )

    # Create a proxy server in the "started" state
    mock_proxy_server = Mock()
    mock_proxy_server.is_started = True
    # Ensure proxy_port is a primitive int (not a Mock) so JSON serialization works
    mock_proxy_server.proxy_port = 45678

    jp_serverapp.web_app.add_handlers(
        ".*$", [(signin_route, SignInHandler, dict(proxy_server=mock_proxy_server))]
    )

    return jp_serverapp


async def test_signin_api(jp_fetch):
    response = await jp_fetch("api/lseg-analytics-jupyterlab/signin", method="GET")
    assert response.code == 200

    body = json.loads(response.body.decode())
    assert body["status"] == "success"
    assert body["message"] == "auth_url"
    assert "url" in body["data"]
    assert "port" in body["data"]
