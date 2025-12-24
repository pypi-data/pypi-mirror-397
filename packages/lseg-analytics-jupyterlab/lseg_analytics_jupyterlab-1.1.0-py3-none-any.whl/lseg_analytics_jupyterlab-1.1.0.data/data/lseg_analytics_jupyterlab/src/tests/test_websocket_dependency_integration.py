# type: ignore
import pytest
import json
from unittest.mock import Mock, patch
from tornado.web import Application
from lseg_analytics_jupyterlab.src.handlers.webSocketHandler import WebSocket
from lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager import (
    DependencyWatcherManager,
)
from lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler import EventType
from lseg_analytics_jupyterlab.src.constants.message_types import MessageType


class TestDependencyWatchingIntegration:
    """
    Integration tests for dependency watching WebSocket functionality.

    These tests focus on verifying the end-to-end callback flow from dependency changes
    to WebSocket notifications that cannot be effectively tested through unit tests alone.

    Key integration points tested:
    1. Real callback flow from dependency manager to WebSocket notifications
    2. Enum serialization across component boundaries
    3. WebSocket lifecycle integration with dependency watching system

    Unit tests with mocks cover individual components well, but these integration tests
    validate the actual cross-component data flow and error handling.
    """

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Reset WebSocket singleton before and after each test."""
        WebSocket._reset_singleton()
        yield
        WebSocket._reset_singleton()

    def test_dependency_change_notification_flow(self):
        """
        Test the complete flow from dependency change callback to WebSocket notification.

        This test verifies the actual callback chain from dependency manager to WebSocket
        notification, testing real object interactions rather than mocked interfaces.
        """
        # Setup WebSocket
        app = Application([("/ws", WebSocket)])
        request_mock = Mock()
        websocket = WebSocket(app, request_mock)

        # Set as active instance
        WebSocket._active_instance = websocket

        # Mock connection with stream that's not closed (required by enhanced validation)
        mock_stream = Mock()
        mock_stream.closed.return_value = False
        mock_connection = Mock()
        mock_connection.stream = mock_stream
        websocket.ws_connection = mock_connection

        # Set up IOLoop for message sending
        WebSocket._main_ioloop = Mock()

        # Mock the websocket write_message method
        websocket.write_message = Mock()

        # Create a real dependency watcher manager (not mocked)
        manager = DependencyWatcherManager()

        # Simulate a dependency change
        package_name = "lseg_analytics-1.0.0.dist-info"
        event_type = EventType.CREATED

        # Mock only the logger to prevent actual log output
        with patch(
            "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main"
        ), patch("lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"):
            # Call the actual callback to test the real notification flow
            manager._dependency_change_callback(package_name, event_type)

        # Verify WebSocket notification was sent with correct payload
        expected_message = {
            "message_type": MessageType.DEPENDENCY_CHANGED,
            "message": {"event_type": event_type.value, "packageName": package_name},
        }

        # Check that the message was sent to the client through the ioloop
        WebSocket._main_ioloop.add_callback.assert_called_once()
        call_args = WebSocket._main_ioloop.add_callback.call_args
        assert call_args[0][0] == websocket.write_message
        assert call_args[0][1] == json.dumps(expected_message)

    def test_websocket_singleton_connection_lifecycle(self):
        """
        Test WebSocket connection lifecycle and disconnection with dependency watching.

        This test verifies the integration between WebSocket lifecycle events and
        the dependency watching system, including graceful handling of notifications
        when no client is connected.
        """
        app = Application([("/ws", WebSocket)])
        request_mock = Mock()
        ws = WebSocket(app, request_mock)

        # Test connection opening sets up IOLoop and active instance
        with patch(
            "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
        ):
            ws.open()
        assert WebSocket._main_ioloop is not None
        assert WebSocket._active_instance is ws

        # Test connection closing
        with patch(
            "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.logger_main"
        ):
            ws.on_close()

        # After close, active instance should be cleared
        assert WebSocket._active_instance is None

        # Test that notifications don't crash when no active connection
        # This tests the real error handling path
        WebSocket.send_dependency_change_notification("test-package", "created")
        # Should complete without raising exceptions
