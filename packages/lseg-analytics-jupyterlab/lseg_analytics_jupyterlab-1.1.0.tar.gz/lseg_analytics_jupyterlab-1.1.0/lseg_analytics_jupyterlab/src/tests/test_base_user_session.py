# type: ignore
from lseg_analytics_jupyterlab.src.classes.baseUserSession import BaseUserSession
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
import pytest
from unittest.mock import Mock, patch


@pytest.fixture()
def user_session():
    return BaseUserSession(
        "test_id",
        "test_user_id",
        "test_user_name",
        "test_access_token",
        "test_refresh_token",
        "test_expiry_date",
    )


def test_base_user_session(user_session):
    assert user_session.id == "test_id"
    assert user_session.user_id == "test_user_id"
    assert user_session.user_display_name == "test_user_name"
    assert user_session.access_token == "test_access_token"
    assert user_session.refresh_token == "test_refresh_token"
    assert user_session.expiry_date_time_ms == "test_expiry_date"


def test_base_user_session_default_diagnostics():
    """Test that diagnostics are initialized with default values when not provided."""
    session = BaseUserSession(
        "test_id",
        "test_user_id",
        "test_user_name",
        "test_access_token",
        "test_refresh_token",
        "test_expiry_date",
    )
    assert session.diagnostics is not None
    assert session.diagnostics["sessionStartTimestampMs"] == 0
    assert session.diagnostics["lastTokenRefreshTimestampMs"] == 0
    assert session.diagnostics["refreshCount"] == 0


def test_base_user_session_with_custom_diagnostics():
    """Test that custom diagnostics are preserved when provided."""
    custom_diagnostics = {
        "sessionStartTimestampMs": 1234567890,
        "lastTokenRefreshTimestampMs": 1234567890,
        "refreshCount": 5,
    }
    session = BaseUserSession(
        "test_id",
        "test_user_id",
        "test_user_name",
        "test_access_token",
        "test_refresh_token",
        "test_expiry_date",
        custom_diagnostics,
    )
    assert session.diagnostics == custom_diagnostics
    assert session.diagnostics["sessionStartTimestampMs"] == 1234567890
    assert session.diagnostics["lastTokenRefreshTimestampMs"] == 1234567890
    assert session.diagnostics["refreshCount"] == 5


def test_get_id(user_session):
    user_session.id == user_session._get_id()
