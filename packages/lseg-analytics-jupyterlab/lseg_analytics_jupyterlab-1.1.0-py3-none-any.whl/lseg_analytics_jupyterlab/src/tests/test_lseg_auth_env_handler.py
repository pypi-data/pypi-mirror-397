import pytest
from unittest.mock import patch
from lseg_analytics_jupyterlab.src.handlers.lsegAuthEnvHandler import LsegAuthEnvHandler
from tornado.web import Application
from tornado.httputil import HTTPServerRequest
from unittest.mock import Mock


@pytest.fixture()
def lseg_auth_env_handler():
    application = Application([("/lseg-auth-env", LsegAuthEnvHandler)])
    request = HTTPServerRequest(method="GET", uri="/lseg-auth-env")
    request.connection = Mock()  # Add dummy connection to satisfy Tornado
    handler = LsegAuthEnvHandler(application, request)
    return handler


@patch("tornado.web.RequestHandler.finish")
@patch("tornado.web.RequestHandler.get_argument")
def test_lseg_auth_env_handler_success(
    mock_get_argument, mock_finish, lseg_auth_env_handler
):
    mock_get_argument.return_value = "__LSEG_AUTH_ENVIRONMENT"
    with patch("os.environ.get", return_value="staging"):
        lseg_auth_env_handler.get()
        mock_finish.assert_called_once_with(
            '{"status": "success", "message": "Environment variable \'__LSEG_AUTH_ENVIRONMENT\' retrieved successfully", "data": "staging", "error": null}'
        )


@patch("tornado.web.RequestHandler.finish")
@patch("tornado.web.RequestHandler.get_argument")
def test_lseg_auth_env_handler_none_value(
    mock_get_argument, mock_finish, lseg_auth_env_handler
):
    mock_get_argument.return_value = "__LSEG_AUTH_ENVIRONMENT"
    with patch("os.environ.get", return_value=None):
        lseg_auth_env_handler.get()
        mock_finish.assert_called_once_with(
            '{"status": "success", "message": "Environment variable \'__LSEG_AUTH_ENVIRONMENT\' retrieved successfully", "data": null, "error": null}'
        )


@patch("tornado.web.RequestHandler.finish")
@patch("tornado.web.RequestHandler.get_argument")
def test_lseg_auth_env_handler_empty_string(
    mock_get_argument, mock_finish, lseg_auth_env_handler
):
    mock_get_argument.return_value = "__LSEG_AUTH_ENVIRONMENT"
    with patch("os.environ.get", return_value=""):
        lseg_auth_env_handler.get()
        mock_finish.assert_called_once_with(
            '{"status": "success", "message": "Environment variable \'__LSEG_AUTH_ENVIRONMENT\' retrieved successfully", "data": "", "error": null}'
        )


@patch("lseg_analytics_jupyterlab.src.classes.loggers.logger_main.error")
@patch("tornado.web.RequestHandler.finish")
@patch("tornado.web.RequestHandler.get_argument")
def test_lseg_auth_env_handler_missing_var_param(
    mock_get_argument, mock_finish, mock_logger, lseg_auth_env_handler
):
    mock_get_argument.return_value = None
    lseg_auth_env_handler.get()
    mock_finish.assert_called_once()
    args, _ = mock_finish.call_args
    assert "Environment variable name is required" in args[0]
    mock_logger.assert_called_once_with(
        "[LsegAuthEnvHandler] No environment variable name provided"
    )


@patch("lseg_analytics_jupyterlab.src.classes.loggers.logger_main.error")
@patch("tornado.web.RequestHandler.finish")
@patch("tornado.web.RequestHandler.get_argument")
def test_lseg_auth_env_handler_unauthorized_var(
    mock_get_argument, mock_finish, mock_logger, lseg_auth_env_handler
):
    mock_get_argument.return_value = "UNAUTHORIZED_VAR"
    lseg_auth_env_handler.get()
    mock_finish.assert_called_once()
    args, _ = mock_finish.call_args
    assert "Environment variable 'UNAUTHORIZED_VAR' is not allowed" in args[0]
    mock_logger.assert_called_once_with(
        "[LsegAuthEnvHandler] Unauthorized environment variable requested: UNAUTHORIZED_VAR"
    )


@patch("lseg_analytics_jupyterlab.src.classes.loggers.logger_main.error")
@patch("tornado.web.RequestHandler.finish")
@patch("tornado.web.RequestHandler.get_argument")
def test_lseg_auth_env_handler_error(
    mock_get_argument, mock_finish, mock_logger, lseg_auth_env_handler
):
    mock_get_argument.side_effect = Exception("fail")
    lseg_auth_env_handler.get()
    mock_finish.assert_called_once()
    args, _ = mock_finish.call_args
    assert "Failed to get environment variable" in args[0]
    assert "fail" in args[0]
    mock_logger.assert_called_once()


@patch("tornado.web.RequestHandler.finish")
@patch("tornado.web.RequestHandler.get_argument")
def test_lseg_auth_env_handler_whitelist_validation(
    mock_get_argument, mock_finish, lseg_auth_env_handler
):
    # Test that __LSEG_AUTH_ENVIRONMENT is in the whitelist
    mock_get_argument.return_value = "__LSEG_AUTH_ENVIRONMENT"
    with patch("os.environ.get", return_value="production"):
        lseg_auth_env_handler.get()
        mock_finish.assert_called_once_with(
            '{"status": "success", "message": "Environment variable \'__LSEG_AUTH_ENVIRONMENT\' retrieved successfully", "data": "production", "error": null}'
        )
