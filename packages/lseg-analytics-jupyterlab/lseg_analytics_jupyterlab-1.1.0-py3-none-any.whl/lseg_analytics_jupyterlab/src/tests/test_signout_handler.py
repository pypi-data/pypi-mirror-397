# type: ignore
import pytest
from unittest.mock import Mock, patch
from lseg_analytics_jupyterlab.src.classes.baseUserSession import BaseUserSession
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
from lseg_analytics_jupyterlab.src.handlers.signoutHandler import SignOutHandler
from lseg_analytics_jupyterlab.src.classes.enablementStatusService import (
    EnablementStatusService,
)
from tornado.web import Application

mock_proxy_server = Mock()


@pytest.fixture()
def session_service_instance():
    session_service = SessionService(settings={})
    session_service.set_session(
        BaseUserSession(
            "test_id",
            "test_user_id",
            "test_user_name",
            "test_access_token",
            "test_refresh_token",
            "test_expiry_date",
        )
    )
    return session_service


@pytest.fixture()
def enablement_status_service():
    return Mock(spec=EnablementStatusService)


@pytest.fixture()
def sign_out_handler(session_service_instance, enablement_status_service):
    mock_proxy_server.reset_mock()

    application = Application()
    mock_request = Mock()
    handler = SignOutHandler(
        application,
        mock_request,
        proxy_server=mock_proxy_server,
        session_service=session_service_instance,
        enablement_status_service=enablement_status_service,
    )
    handler.settings["BASE_URL"] = "https://login.stage.ciam.refinitiv.com"

    return handler


@patch("tornado.web.RequestHandler.finish")
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.info")
async def test_sign_out_handler(
    mock_logger_info,
    mock_finish,
    sign_out_handler,
    session_service_instance,
    enablement_status_service,
):
    sign_out_handler.get()
    mock_finish.assert_called_once_with(
        '{"status": "success", "message": "Signed out successfully", "data": null, "error": null}'
    )
    mock_logger_info.assert_called_once_with("Signed out successfully")
    mock_proxy_server.stop.assert_called_once()
    enablement_status_service.clear_status.assert_called_once_with()
    assert session_service_instance.get_session() is None


@patch("tornado.web.RequestHandler.finish")
@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService.error")
async def test_error_sign_out_handler(
    mock_logger_error,
    mock_finish,
    sign_out_handler,
    enablement_status_service,
):
    sign_out_handler.handlelogout = Mock(
        side_effect=Exception("my_custom_error_message")
    )
    sign_out_handler.get()
    mock_finish.assert_called_once_with(
        '{"status": "error", "message": "An unexpected error occured", "data": null, "error": "my_custom_error_message"}'
    )
    mock_logger_error.assert_called_once_with(
        "An unexpected error occuredmy_custom_error_message"
    )
    mock_proxy_server.stop.assert_not_called()
    enablement_status_service.clear_status.assert_not_called()
