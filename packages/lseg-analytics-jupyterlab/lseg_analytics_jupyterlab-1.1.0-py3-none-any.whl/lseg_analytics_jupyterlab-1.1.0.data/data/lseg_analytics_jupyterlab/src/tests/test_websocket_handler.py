import json
from unittest.mock import Mock, patch

from lseg_analytics_jupyterlab.src.handlers.webSocketHandler import WebSocket
from lseg_analytics_jupyterlab.src.constants.message_types import MessageType


@patch("lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main")
def test_handle_enablement_status_message_updates_cache(mock_logger):
    handler = object.__new__(WebSocket)
    enablement_status_service = Mock()

    with patch.object(
        WebSocket,
        "_get_enablement_status_service",
        return_value=enablement_status_service,
    ):
        handler._handle_enablement_status_message({"hasLfaAccess": True})

    enablement_status_service.update_status.assert_called_once_with(True)
    mock_logger.debug.assert_called()


@patch("lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main")
def test_handle_enablement_status_message_defaults_false(mock_logger):
    handler = object.__new__(WebSocket)
    enablement_status_service = Mock()

    with patch.object(
        WebSocket,
        "_get_enablement_status_service",
        return_value=enablement_status_service,
    ):
        handler._handle_enablement_status_message({})

    enablement_status_service.update_status.assert_called_once_with(False)
    mock_logger.debug.assert_called()


@patch("lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main")
def test_handle_enablement_status_message_logs_error(mock_logger):
    handler = object.__new__(WebSocket)

    with patch.object(
        WebSocket,
        "_get_enablement_status_service",
        side_effect=RuntimeError("boom"),
    ):
        handler._handle_enablement_status_message({"hasLfaAccess": True})

    mock_logger.error.assert_called_once_with(
        "[WebSocketHandler] Failed to process enablement status message: boom"
    )


@patch.object(WebSocket, "_handle_enablement_status_message")
@patch("lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main")
def test_on_message_routes_enablement_status(mock_logger, mock_handler):
    handler = object.__new__(WebSocket)

    payload = {
        "message_type": MessageType.ENABLEMENT_STATUS,
        "message": {"hasLfaAccess": False},
    }

    handler.on_message(json.dumps(payload))

    mock_handler.assert_called_once_with(payload["message"])
    mock_logger.debug.assert_called()  # type: ignore


import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from tornado.web import Application
from lseg_analytics_jupyterlab.src.handlers.webSocketHandler import WebSocket
from lseg_analytics_jupyterlab.src.constants.message_types import MessageType
from lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager import (
    DependencyWatcherManager,
)
import json


@pytest.fixture
def websocket():
    # Reset singleton before each test
    WebSocket._reset_singleton()

    application = Application([("/ws", WebSocket)])
    request_mock = Mock()
    ws = WebSocket(application, request_mock)
    ws.ws_connection = Mock()
    return ws


@pytest.fixture(autouse=True)
def reset_websocket_singleton():
    """Automatically reset WebSocket singleton after each test."""
    yield
    WebSocket._reset_singleton()


def test_open(websocket):
    # Test that opening stores IOLoop and logs connection
    with patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ) as mock_logger:
        websocket.open()

        # Verify IOLoop is stored
        assert WebSocket._main_ioloop is not None

        # Verify debug logs were called (there are now two debug calls)
        assert mock_logger.debug.call_count == 2
        mock_logger.debug.assert_any_call(
            "[WebSocketHandler] WebSocket connection opened"
        )
        mock_logger.debug.assert_any_call(
            "[WebSocketHandler] Active connection state: True"
        )


def test_on_message(websocket):
    message = "Hello, WebSocket!"
    with patch.object(websocket, "write_message") as mock_write, patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ):
        websocket.on_message(message)
        # Non-JSON messages are no longer echoed back
        mock_write.assert_not_called()


def test_on_close(websocket):
    with patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ) as mock_logger:
        websocket.on_close()

        # Verify debug logs were called - now there are multiple debug calls
        assert mock_logger.debug.call_count >= 2
        mock_logger.debug.assert_any_call(
            "[WebSocketHandler] WebSocket connection closed"
        )
        mock_logger.debug.assert_any_call(
            "[WebSocketHandler] WebSocket connection cleanup completed"
        )


def test_send_message_to_client_with_instance_and_ioloop():
    # Setup
    WebSocket._reset_singleton()
    application = Application([("/ws", WebSocket)])
    request_mock = Mock()
    ws = WebSocket(application, request_mock)

    # Set as active instance
    WebSocket._active_instance = ws

    # Mock connection with stream that's not closed
    mock_stream = Mock()
    mock_stream.closed.return_value = False
    mock_connection = Mock()
    mock_connection.stream = mock_stream
    ws.ws_connection = mock_connection  # Simulate active connection

    mock_ioloop = Mock()
    WebSocket._main_ioloop = mock_ioloop
    message = "test message"

    # Execute
    WebSocket.send_message_to_client(message)

    # Assert
    mock_ioloop.add_callback.assert_called_once_with(ws.write_message, message)


def test_send_message_to_client_without_instance():
    # Setup - no instance created
    WebSocket._reset_singleton()
    mock_ioloop = Mock()
    WebSocket._main_ioloop = mock_ioloop
    message = "test message"

    # Execute
    WebSocket.send_message_to_client(message)

    # Assert
    mock_ioloop.add_callback.assert_not_called()


def test_send_message_to_client_without_ioloop():
    # Setup
    WebSocket._reset_singleton()
    application = Application([("/ws", WebSocket)])
    request_mock = Mock()
    ws = WebSocket(application, request_mock)

    # Set as active instance
    WebSocket._active_instance = ws

    # Mock connection with stream that's not closed
    mock_stream = Mock()
    mock_stream.closed.return_value = False
    mock_connection = Mock()
    mock_connection.stream = mock_stream
    ws.ws_connection = mock_connection

    WebSocket._main_ioloop = None
    message = "test message"

    # Execute
    WebSocket.send_message_to_client(message)

    # Assert - Should not raise any errors, but no callback should happen


def test_send_message_to_client_without_connection():
    # Setup - instance exists but no active connection
    WebSocket._reset_singleton()
    application = Application([("/ws", WebSocket)])
    request_mock = Mock()
    ws = WebSocket(application, request_mock)
    # No ws_connection set (simulates closed connection)
    # No active instance set either

    mock_ioloop = Mock()
    WebSocket._main_ioloop = mock_ioloop
    message = "test message"

    # Execute
    WebSocket.send_message_to_client(message)

    # Assert
    mock_ioloop.add_callback.assert_not_called()


def test_singleton_behavior():
    """Test that WebSocket instances can be created normally (no longer singleton)."""
    # Reset to ensure clean state
    WebSocket._reset_singleton()

    application = Application([("/ws", WebSocket)])
    request_mock = Mock()

    # Create two WebSocket instances - they should be different now
    ws1 = WebSocket(application, request_mock)
    ws2 = WebSocket(application, request_mock)

    # Should be different instances now (no longer singleton)
    assert ws1 is not ws2

    # But only one can be active at a time
    WebSocket._active_instance = ws1
    assert WebSocket._active_instance is ws1


def test_reset_singleton():
    """Test that _reset_singleton properly clears active instance and ioloop."""
    # Create an instance
    application = Application([("/ws", WebSocket)])
    request_mock = Mock()
    ws = WebSocket(application, request_mock)
    WebSocket._active_instance = ws
    WebSocket._main_ioloop = Mock()

    # Verify instance exists
    assert WebSocket._active_instance is not None
    assert WebSocket._main_ioloop is not None

    # Reset
    WebSocket._reset_singleton()

    # Verify reset worked
    assert WebSocket._active_instance is None
    assert WebSocket._main_ioloop is None


# New tests for dependency watching WebSocket functionality


def test_on_message_watch_dependencies_start(websocket):
    """Test handling of WatchDependenciesStart message."""
    message = {
        "watch": True,
        "path": ["/path/to/python/site-packages", "/path/to/other/packages"],
    }

    with patch.object(
        websocket, "_get_dependency_watcher_manager"
    ) as mock_get_manager, patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ):
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        websocket.on_message(json.dumps(message))

        mock_manager.start_watching.assert_called_once_with(
            ["/path/to/python/site-packages", "/path/to/other/packages"]
        )


def test_on_message_watch_dependencies_stop(websocket):
    """Test handling of WatchDependenciesStop message."""
    message = {"watch": False}

    with patch.object(
        websocket, "_get_dependency_watcher_manager"
    ) as mock_get_manager, patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ):
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        websocket.on_message(json.dumps(message))

        mock_manager.stop_watching.assert_called_once()


def test_on_message_watch_dependencies_start_empty_path(websocket):
    """Test handling of WatchDependenciesStart message with empty path."""
    message = {"watch": True, "path": []}  # Empty path

    with patch.object(
        websocket, "_get_dependency_watcher_manager"
    ) as mock_get_manager, patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ):
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        websocket.on_message(json.dumps(message))

        # Should not call start_watching with empty path
        mock_manager.start_watching.assert_not_called()


def test_on_message_watch_dependencies_start_missing_path(websocket):
    """Test handling of WatchDependenciesStart message with missing path field."""
    message = {
        "watch": True
        # No path field
    }

    with patch.object(
        websocket, "_get_dependency_watcher_manager"
    ) as mock_get_manager, patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ):
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        websocket.on_message(json.dumps(message))

        # Should not call start_watching when path is missing
        mock_manager.start_watching.assert_not_called()


def test_on_message_invalid_json(websocket):
    """Test handling of invalid JSON message."""
    with patch.object(websocket, "write_message") as mock_write, patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ):
        websocket.on_message("invalid json")
        # Invalid JSON is no longer echoed back
        mock_write.assert_not_called()


def test_on_message_non_watch_message(websocket):
    """Test handling of non-watch JSON message (should echo back)."""
    message = {"type": "other", "content": "test"}

    with patch.object(websocket, "write_message") as mock_write:
        websocket.on_message(json.dumps(message))
        mock_write.assert_called_once_with(json.dumps(message))


def test_send_dependency_change_notification():
    """Test sending dependency change notification to client."""
    with patch.object(WebSocket, "send_message_to_client") as mock_send, patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ):
        WebSocket.send_dependency_change_notification(
            "lseg_analytics-1.0.0.dist-info", "created"
        )

        expected_message = {
            "message_type": MessageType.DEPENDENCY_CHANGED,
            "message": {
                "event_type": "created",
                "packageName": "lseg_analytics-1.0.0.dist-info",
            },
        }

        mock_send.assert_called_once_with(json.dumps(expected_message))


def test_send_dependency_change_notification_error():
    """Test error handling when sending dependency change notification."""
    with patch.object(
        WebSocket, "send_message_to_client", side_effect=Exception("Network error")
    ), patch("lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"):
        # Should not raise exception
        WebSocket.send_dependency_change_notification(
            "lseg_analytics-1.0.0.dist-info", "created"
        )


def test_get_dependency_watcher_manager_global_reference():
    """Test that dependency watcher manager returns consistent instance."""
    # Test that the method returns the same instance consistently (global behavior)
    manager1 = WebSocket._get_dependency_watcher_manager()
    manager2 = WebSocket._get_dependency_watcher_manager()

    # Should return the same global instance
    assert manager1 is manager2
    # Should be a DependencyWatcherManager instance
    assert isinstance(manager1, DependencyWatcherManager)


def test_on_message_watch_exception_handling(websocket):
    """Test exception handling in watch message processing."""
    message = {"watch": True, "path": ["/path/to/packages"]}

    with patch.object(
        websocket,
        "_get_dependency_watcher_manager",
        side_effect=Exception("Test error"),
    ):
        # Should not raise exception
        websocket.on_message(json.dumps(message))


def test_open_closes_previous_connection():
    """Test that opening a new connection closes the previous active connection."""
    WebSocket._reset_singleton()

    application = Application([("/ws", WebSocket)])

    # Create first connection
    request_mock1 = Mock()
    ws1 = WebSocket(application, request_mock1)
    ws1.ws_connection = Mock()

    # Create second connection
    request_mock2 = Mock()
    ws2 = WebSocket(application, request_mock2)
    ws2.ws_connection = Mock()

    with patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ) as mock_logger:
        # Open first connection
        ws1.open()
        assert WebSocket._active_instance is ws1

        # Mock close method on first instance
        ws1.close = Mock()

        # Open second connection - should close first
        ws2.open()

        # Verify first connection was closed
        ws1.close.assert_called_once()
        assert WebSocket._active_instance is ws2
        mock_logger.debug.assert_any_call(
            "[WebSocketHandler] Closed previous connection"
        )


def test_open_previous_connection_close_error():
    """Test handling of error when closing previous connection."""
    WebSocket._reset_singleton()

    application = Application([("/ws", WebSocket)])

    # Create first connection
    request_mock1 = Mock()
    ws1 = WebSocket(application, request_mock1)
    ws1.ws_connection = Mock()

    # Create second connection
    request_mock2 = Mock()
    ws2 = WebSocket(application, request_mock2)
    ws2.ws_connection = Mock()

    with patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ) as mock_logger:
        # Open first connection
        ws1.open()
        assert WebSocket._active_instance is ws1

        # Mock close method to raise exception
        ws1.close = Mock(side_effect=Exception("Close error"))

        # Open second connection - should handle error gracefully
        ws2.open()

        # Verify error was logged and second connection became active
        assert WebSocket._active_instance is ws2
        mock_logger.debug.assert_any_call(
            "[WebSocketHandler] Error closing previous connection: Close error"
        )


def test_on_close_with_dependency_watching():
    """Test on_close when dependency watching is active."""
    WebSocket._reset_singleton()

    application = Application([("/ws", WebSocket)])
    request_mock = Mock()
    ws = WebSocket(application, request_mock)

    # Set as active instance
    WebSocket._active_instance = ws

    with patch.object(ws, "_get_dependency_watcher_manager") as mock_get_manager, patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ) as mock_logger:

        # Mock dependency manager that is watching
        mock_manager = Mock()
        mock_manager.is_watching.return_value = True
        mock_get_manager.return_value = mock_manager

        ws.on_close()

        # Verify dependency watching was stopped
        mock_manager.stop_watching.assert_called_once()
        mock_logger.debug.assert_any_call(
            "[WebSocketHandler] Stopping dependency watching due to connection closure"
        )

        # Verify active instance was cleared
        assert WebSocket._active_instance is None


def test_on_close_dependency_manager_error():
    """Test on_close when dependency manager raises an error."""
    WebSocket._reset_singleton()

    application = Application([("/ws", WebSocket)])
    request_mock = Mock()
    ws = WebSocket(application, request_mock)

    # Set as active instance
    WebSocket._active_instance = ws

    with patch.object(
        ws, "_get_dependency_watcher_manager", side_effect=Exception("Manager error")
    ), patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ) as mock_logger:

        ws.on_close()

        # Verify error was logged
        mock_logger.error.assert_any_call(
            "[WebSocketHandler] Error stopping dependency watching on close: Manager error"
        )

        # Verify active instance was still cleared
        assert WebSocket._active_instance is None


def test_on_close_not_active_instance():
    """Test on_close when this instance is not the active one."""
    WebSocket._reset_singleton()

    application = Application([("/ws", WebSocket)])
    request_mock1 = Mock()
    ws1 = WebSocket(application, request_mock1)

    request_mock2 = Mock()
    ws2 = WebSocket(application, request_mock2)

    # Set ws2 as active instance, but call close on ws1
    WebSocket._active_instance = ws2

    with patch.object(
        ws1, "_get_dependency_watcher_manager"
    ) as mock_get_manager, patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ):

        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        ws1.on_close()

        # Verify dependency manager was not called since ws1 is not active
        mock_manager.stop_watching.assert_not_called()

        # Verify active instance remains ws2
        assert WebSocket._active_instance is ws2


def test_send_message_connection_validation_failure():
    """Test send_message_to_client when connection validation fails."""
    WebSocket._reset_singleton()

    application = Application([("/ws", WebSocket)])
    request_mock = Mock()
    ws = WebSocket(application, request_mock)

    # Set as active instance
    WebSocket._active_instance = ws
    WebSocket._main_ioloop = Mock()

    # Mock connection where accessing the stream property raises an exception
    mock_connection = Mock()
    type(mock_connection).stream = PropertyMock(
        side_effect=Exception("Connection error")
    )
    ws.ws_connection = mock_connection

    with patch("builtins.print") as mock_print:
        WebSocket.send_message_to_client("test message")

        # Verify active instance was cleared
        assert WebSocket._active_instance is None

        # Verify fallback logging was used
        mock_print.assert_called_once_with(
            "[WebSocketHandler] Connection validation failed, cleared stale instance"
        )


def test_reset_connection_state():
    """Test _reset_connection_state method."""
    WebSocket._reset_singleton()

    application = Application([("/ws", WebSocket)])
    request_mock = Mock()
    ws = WebSocket(application, request_mock)

    # Set up state
    WebSocket._active_instance = ws
    WebSocket._main_ioloop = Mock()

    with patch(
        "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
    ) as mock_logger:
        WebSocket._reset_connection_state()

        # Verify only active instance was cleared, ioloop preserved
        assert WebSocket._active_instance is None
        assert WebSocket._main_ioloop is not None

        mock_logger.debug.assert_called_once_with(
            "[WebSocketHandler] Connection state reset"
        )


def test_handle_watch_message_exception_handling(websocket):
    """Test exception handling in _handle_watch_message."""
    message_data = {"watch": True, "path": ["/path/to/packages"]}

    with patch.object(
        websocket,
        "_get_dependency_watcher_manager",
        side_effect=Exception("Test error"),
    ):
        # Should not raise exception
        websocket._handle_watch_message(message_data)
