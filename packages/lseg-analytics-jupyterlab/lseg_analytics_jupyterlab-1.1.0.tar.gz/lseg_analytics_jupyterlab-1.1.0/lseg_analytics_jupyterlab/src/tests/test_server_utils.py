# type: ignore
import pytest
from unittest.mock import Mock, patch
from lseg_analytics_jupyterlab.src.utils.serverUtils import (
    fetch_openid_configuration,
    ensure_auth_settings,
)


@patch("requests.get")
async def test_fetch_open_id_configuration(mock_get):
    test_url = "http/test"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"content": "OK"}
    mock_get.return_value = mock_response

    actual = fetch_openid_configuration(test_url)
    # assert
    mock_get.assert_called_once_with(
        test_url + "/.well-known/openid-configuration", timeout=(10, 30)
    )
    assert actual == {"content": "OK"}


@patch("requests.get")
async def test_open_id_configuration_error(mock_get):
    with pytest.raises(RuntimeError, match="Failed to fetch OpenID configuration"):
        test_url = "http/test"
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "error"}
        mock_get.return_value = mock_response
        actual = fetch_openid_configuration(test_url)
        assert "Error fetching OpenID configuration: fail" in str(excinfo.value)


def test_ensure_auth_settings_fetches_and_sets_urls():
    settings = {"BASE_URL": "base url value", "CLIENT_ID": "client id value"}
    mock_openid_config = {
        "authorization_endpoint": "auth url value",
        "token_endpoint": "token url value",
    }
    with patch(
        "lseg_analytics_jupyterlab.src.utils.serverUtils.fetch_openid_configuration",
        return_value=mock_openid_config,
    ) as mock_fetch:
        ensure_auth_settings(settings)
        assert settings["AUTH_URL"] == "auth url value"
        assert settings["TOKEN_URL"] == "token url value"
        mock_fetch.assert_called_once_with("base url value")


def test_ensure_auth_settings_does_not_fetch_if_present():
    settings = {
        "BASE_URL": "base url value",
        "CLIENT_ID": "client id value",
        "AUTH_URL": "already_set_auth",
        "TOKEN_URL": "already_set_token",
    }
    with patch(
        "lseg_analytics_jupyterlab.src.utils.serverUtils.fetch_openid_configuration"
    ) as mock_fetch:
        ensure_auth_settings(settings)
        mock_fetch.assert_not_called()
        assert settings["AUTH_URL"] == "already_set_auth"
        assert settings["TOKEN_URL"] == "already_set_token"


def test_ensure_auth_settings_raises_on_fetch_error():
    settings = {"BASE_URL": "base url value", "CLIENT_ID": "client id value"}
    with patch(
        "lseg_analytics_jupyterlab.src.utils.serverUtils.fetch_openid_configuration",
        side_effect=Exception("fail"),
    ):
        with pytest.raises(RuntimeError) as excinfo:
            ensure_auth_settings(settings)
        assert "Error fetching OpenID configuration: fail" in str(excinfo.value)


def test_ensure_auth_settings_raises_if_base_url_not_present():
    settings = {
        # "BASE_URL" is intentionally missing
        "CLIENT_ID": "client id value",
    }
    with pytest.raises(RuntimeError) as excinfo:
        ensure_auth_settings(settings)
    assert "[Internal error] BASE_URL is missing from settings" in str(excinfo.value)


def test_ensure_auth_settings_raises_if_client_id_not_present():
    settings = {
        "BASE_URL": "base url value"
        # "CLIENT_ID" is intentionally missing
    }
    with pytest.raises(RuntimeError) as excinfo:
        ensure_auth_settings(settings)
    assert "[Internal error] CLIENT_ID is missing from settings" in str(excinfo.value)
