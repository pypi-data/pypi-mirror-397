# type: ignore
import pytest
from unittest.mock import MagicMock
from lseg_analytics_jupyterlab.src.classes.settingsService import (
    SettingsService,
)  # Replace 'your_module' with the actual module name


def test_staging_environment():
    # Test initialization with staging environment
    service = SettingsService("staging")
    assert service.get_setting("CLIENT_ID") == "afd238de-256f-4956-9e39-b31bab87b837"
    assert service.get_setting("BASE_URL") == "https://login.stage.ciam.refinitiv.com"
    assert service.get_setting("SDK_API") == "https://ppe.api.analytics.lseg.com"
    assert service.get_common_setting("proxy_server_host") == "http://127.0.0.1"


def test_production_environment():
    # Test initialization with production environment
    service = SettingsService("production")
    assert service.get_setting("CLIENT_ID") == "78bb1b02-b708-4560-90a9-96cf1814b881"
    assert service.get_setting("BASE_URL") == "https://login.ciam.refinitiv.com"
    assert service.get_setting("SDK_API") == "https://api.analytics.lseg.com"
    assert service.get_common_setting("proxy_server_host") == "http://127.0.0.1"


@pytest.mark.parametrize(
    "env_input, should_warn",
    [
        ("invalid_env", True),  # An unknown string should trigger a warning.
        (None, False),  # None is an expected fallback and should not warn.
        ("", False),  # Empty string is an expected fallback and should not warn.
    ],
)
def test_unknown_or_missing_env_defaults_to_production(mocker, env_input, should_warn):
    """
    Tests that the service defaults to PRODUCTION for any unknown, None, or empty environment string.
    """
    # Mock the logger to verify warning calls
    mock_logger = MagicMock()
    mocker.patch(
        "lseg_analytics_jupyterlab.src.classes.settingsService.logger_main", mock_logger
    )

    # Initialize the service with the test input
    service = SettingsService(env_input)

    # Assert that the effective environment is production and settings are correct
    assert service.environment == "production"
    assert service.get_setting("CLIENT_ID") == "78bb1b02-b708-4560-90a9-96cf1814b881"

    # Assert that a warning was logged only for unexpected, non-empty strings
    if should_warn:
        mock_logger.warn.assert_called_once()
    else:
        mock_logger.warn.assert_not_called()

    # Assert the info log was always called to confirm execution flow
    mock_logger.debug.assert_called_once()


def test_staging_is_case_insensitive_and_trims_whitespace():
    """
    Tests that 'staging' is recognized regardless of case or surrounding whitespace.
    """
    service = SettingsService(" STAGING ")
    assert service.environment == "staging"
    assert service.get_setting("CLIENT_ID") == "afd238de-256f-4956-9e39-b31bab87b837"


def test_common_settings():
    # Test retrieval of common settings
    service = SettingsService("staging")
    assert service.get_common_setting("proxy_server_host") == "http://127.0.0.1"
    assert service.get_common_setting("port_range") == {"start": 60100, "end": 60110}
    assert service.get_common_setting("api_prefix") == "/api/lseg-analytics-jupyterlab/"
