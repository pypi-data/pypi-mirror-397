import json
import asyncio
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock, Mock, call
from tornado.web import Application
from tornado.httputil import HTTPServerRequest
from lseg_analytics_jupyterlab.src.handlers.sdkInstallHandler import SdkInstallHandler


@pytest.fixture
def sdk_install_handler():
    app = Application()
    request = HTTPServerRequest(uri="/install-sdk", method="POST")
    request.connection = Mock()
    handler = SdkInstallHandler(app, request)
    handler.finish = MagicMock()
    handler.set_status = MagicMock()
    return handler


@patch("lseg_analytics_jupyterlab.src.utils.serverUtils.create_response")
def test_post_invalid_json(mock_create_response, sdk_install_handler):
    """Invalid JSON returns 400."""
    mock_create_response.return_value = json.dumps({"error": "Invalid JSON"})
    sdk_install_handler.request.body = b"invalid json"

    asyncio.run(sdk_install_handler.post())
    assert sdk_install_handler.set_status.call_count == 2
    assert sdk_install_handler.finish.called


@pytest.mark.parametrize(
    "payload",
    [
        {},  # empty body -> defaults name, but missing version_rules -> 400
        {"package_name": None, "version_rules": [">=1.0.0"]},  # invalid package
        {"package_name": "", "version_rules": [">=1.0.0"]},  # empty package
        {"package_name": "lseg-analytics-pricing", "version_rules": []},  # empty rules
    ],
)
@patch("lseg_analytics_jupyterlab.src.utils.serverUtils.create_response")
def test_post_parameter_validation_errors(
    mock_create_response, sdk_install_handler, payload
):
    """Missing/invalid params return 400."""
    mock_create_response.return_value = json.dumps({"error": "Missing parameters"})
    sdk_install_handler.request.body = json.dumps(payload).encode("utf-8")

    asyncio.run(sdk_install_handler.post())

    sdk_install_handler.set_status.assert_called_once_with(400)
    sdk_install_handler.finish.assert_called_once()


@pytest.mark.parametrize(
    "rules, expected_spec",
    [
        ([">=1.0.0"], "lseg-analytics-pricing>=1.0.0"),
        (["<=2.0.0", ">=1.5.0"], "lseg-analytics-pricing<=2.0.0,>=1.5.0"),
        (["==2.1.0b5"], "lseg-analytics-pricing==2.1.0b5"),
    ],
)
@patch("lseg_analytics_jupyterlab.src.handlers.sdkInstallHandler.subprocess.run")
@patch(
    "lseg_analytics_jupyterlab.src.handlers.sdkInstallHandler.asyncio.get_running_loop"
)
@patch("lseg_analytics_jupyterlab.src.utils.serverUtils.create_response")
def test_post_success_variants_builds_correct_spec(
    mock_create_response,
    mock_get_loop,
    mock_run,
    sdk_install_handler,
    rules,
    expected_spec,
):
    """Successful installation with various version rules constructs correct pip spec."""

    # Dummy loop that executes the function inline
    class _DummyLoop:
        async def run_in_executor(self, executor, func, *args, **kwargs):
            return func()

    mock_get_loop.return_value = _DummyLoop()
    mock_run.return_value = SimpleNamespace(returncode=0, stdout="OK", stderr="")

    mock_create_response.return_value = json.dumps({"status": "success"})

    sdk_install_handler.request.body = json.dumps(
        {"package_name": "lseg-analytics-pricing", "version_rules": rules}
    ).encode("utf-8")

    asyncio.run(sdk_install_handler.post())

    # Assert HTTP 200 and finish called
    sdk_install_handler.set_status.assert_called_once_with(200)
    sdk_install_handler.finish.assert_called_once()

    # Verify subprocess.run got the expected package spec at the end of the command
    called_cmd = mock_run.call_args[0][0]
    assert called_cmd[-1] == expected_spec


@patch("lseg_analytics_jupyterlab.src.handlers.sdkInstallHandler.subprocess.run")
@patch(
    "lseg_analytics_jupyterlab.src.handlers.sdkInstallHandler.asyncio.get_running_loop"
)
@patch("lseg_analytics_jupyterlab.src.utils.serverUtils.create_response")
@pytest.mark.parametrize(
    "simulate, expected_status, expected_finish_calls",
    [
        ("failure", 500, 1),  # pip returns non-zero exit code
        ("timeout", 500, 1),  # asyncio.TimeoutError raised
    ],
)
def test_post_installation_error_paths(
    mock_create_response,
    mock_get_loop,
    mock_run,
    sdk_install_handler,
    simulate,
    expected_status,
    expected_finish_calls,
):
    """
    Covers both pip failure (non-zero exit code) and timeout error.
    Ensures handler sets status 500 and finishes response in both cases.
    """

    class _DummyLoop:
        async def run_in_executor(self, executor, func, *args, **kwargs):
            if simulate == "timeout":
                raise asyncio.TimeoutError("Simulated timeout")
            return func()

    mock_get_loop.return_value = _DummyLoop()
    if simulate == "failure":
        mock_run.return_value = SimpleNamespace(
            returncode=1, stdout="", stderr="some pip error"
        )
    else:
        mock_run.return_value = SimpleNamespace(returncode=0, stdout="OK", stderr="")

    mock_create_response.return_value = json.dumps({"status": "error"})

    sdk_install_handler.request.body = json.dumps(
        {"package_name": "lseg-analytics-pricing", "version_rules": [">=1.0.0"]}
    ).encode("utf-8")

    asyncio.run(sdk_install_handler.post())

    sdk_install_handler.set_status.assert_called_once_with(expected_status)
    assert sdk_install_handler.finish.call_count == expected_finish_calls
