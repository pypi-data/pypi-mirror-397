# type: ignore
from unittest.mock import Mock, patch
import pytest
import json
from types import SimpleNamespace

from lseg_analytics_jupyterlab.src.classes.loggerService import LogLevel, LoggerService


@pytest.fixture
def logger_instance():
    return LoggerService("Test Server")


@patch(
    "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket.send_message_to_client"
)
@patch("builtins.print")
def test_log_message(mocked_print, mocked_websocket_send, logger_instance):
    # Test the basic logging functionality without timestamp expectations
    logger_instance._log_message("Test_info_message", LogLevel("INFO", "\033[32m"))
    mocked_print.assert_called_once_with(
        "\x1b[32mTest Server - [INFO] \x1b[0mTest_info_message"
    )
    mocked_websocket_send.assert_called_once()
    sent_message = mocked_websocket_send.call_args[0][0]
    parsed_message = json.loads(sent_message)

    # Verifying the message structure includes the channel field
    assert parsed_message["message_type"] == "LOGGER"
    assert parsed_message["message"]["channel"] == "Test Server"
    assert parsed_message["message"]["log_level"] == "INFO"


@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService._log_message")
def test_info(mocked_log_message, logger_instance):
    logger_instance.info("Test info")
    mocked_log_message.assert_called_with("Test info", logger_instance.INFO_LOG)


@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService._log_message")
def test_debug(mocked_log_message, logger_instance):
    logger_instance.debug("Test debug")
    mocked_log_message.assert_called_with("Test debug", logger_instance.DEBUG_LOG)


@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService._log_message")
def test_warn(mocked_log_message, logger_instance):
    logger_instance.warn("Test warn")
    mocked_log_message.assert_called_with("Test warn", logger_instance.WARN_LOG)


@patch("lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService._log_message")
def test_error(mocked_log_message, logger_instance):
    logger_instance.error("Test error")
    mocked_log_message.assert_called_with("Test error", logger_instance.ERROR_LOG)


def test_log_level():
    log_level = LogLevel("test_prefix", "test_fore_color")
    log_level.prefix is "test_prefix"
    log_level.fore_colour is "test_fore_color"


# Tests for the _safe_stringify method
def test_safe_stringify_string(logger_instance):
    """Test that _safe_stringify returns the string as-is when a string is passed."""
    test_string = "This is a test string"
    result = logger_instance._safe_stringify(test_string)
    assert result == test_string


def test_safe_stringify_dict(logger_instance):
    """Test that _safe_stringify correctly serializes a dictionary."""
    test_dict = {"name": "test", "value": 123, "nested": {"key": "value"}}
    result = logger_instance._safe_stringify(test_dict)
    expected = json.dumps(test_dict, indent=2)
    assert result == expected


def test_safe_stringify_list(logger_instance):
    """Test that _safe_stringify correctly serializes a list."""
    test_list = [1, 2, "three", {"four": 4}]
    result = logger_instance._safe_stringify(test_list)
    expected = json.dumps(test_list, indent=2)
    assert result == expected


def test_safe_stringify_exception(logger_instance):
    """Test that _safe_stringify correctly handles Exception objects."""
    try:
        # Generate an exception with a traceback
        raise ValueError("Test error message")
    except Exception as e:
        result = logger_instance._safe_stringify(e)
        # Verify that the error message and stack trace are included
        assert "Error: Test error message" in result
        assert "Stack:" in result


def test_safe_stringify_non_serializable(logger_instance):
    """Test that _safe_stringify handles objects that can't be directly serialized."""

    # Create a custom object that's not directly JSON serializable
    class NonSerializable:
        def __init__(self):
            self.name = "test"

    obj = NonSerializable()
    result = logger_instance._safe_stringify(obj)
    # Verify that the default handler was used
    assert "<<Non-serializable object of type NonSerializable>>" in result


def test_safe_stringify_circular_reference(logger_instance):
    """Test that _safe_stringify handles objects with circular references."""
    # Create an object with a circular reference that would break normal JSON serialization
    circular_dict = {}
    circular_dict["self"] = circular_dict

    result = logger_instance._safe_stringify(circular_dict)
    # Verify that the error was caught and formatted
    assert "[Object could not be stringified:" in result


@patch(
    "lseg_analytics_jupyterlab.src.classes.loggerService.LoggerService._safe_stringify"
)
def test_log_message_calls_safe_stringify(mocked_safe_stringify, logger_instance):
    """Test that _log_message calls _safe_stringify for non-string objects."""
    test_obj = {"test": "object"}
    mocked_safe_stringify.return_value = '{"test": "object"}'

    logger_instance._log_message(test_obj, logger_instance.INFO_LOG)

    # Assert that _safe_stringify was called with the test object
    mocked_safe_stringify.assert_called_once_with(test_obj)
