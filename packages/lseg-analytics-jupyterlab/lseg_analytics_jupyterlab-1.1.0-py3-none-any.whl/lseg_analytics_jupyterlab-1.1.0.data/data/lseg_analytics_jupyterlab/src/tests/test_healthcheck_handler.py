# type: ignore
import pytest
from unittest.mock import Mock, patch
from lseg_analytics_jupyterlab.src.handlers.healthCheckHandler import HealthCheckHandler
from tornado.web import Application


@pytest.fixture()
def health_check_handler():
    mock_request = Mock()
    application = Application([("/healthcheck", HealthCheckHandler)])

    handler = HealthCheckHandler(application, mock_request)

    return handler


@patch("tornado.web.RequestHandler.finish")
async def test_health_check_handler(mock_finish, health_check_handler):

    health_check_handler.get()
    # assert
    mock_finish.assert_called_once_with(
        '{"status": "success", "message": "I am healthy!", "data": null, "error": null}'
    )


@patch("tornado.web.RequestHandler.finish")
async def test_error_health_check_handler(mock_finish, health_check_handler):
    mock_finish.side_effect = [Exception("my_custom_error_message"), ""]

    health_check_handler.get()
    # assert
    mock_finish.assert_called_with(
        '{"status": "error", "message": "An unexpected error occurred", "data": null, "error": "my_custom_error_message"}'
    )
