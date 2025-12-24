# type: ignore
import pytest
from unittest.mock import Mock, patch, MagicMock
from lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager import (
    DependencyWatcherManager,
)
from lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler import EventType


class TestDependencyWatcherManagerWebSocketIntegration:
    """Tests for DependencyWatcherManager WebSocket integration."""

    @pytest.fixture
    def dependency_manager(self):
        """Create a DependencyWatcherManager instance for testing."""
        return DependencyWatcherManager()

    def test_dependency_change_callback_sends_websocket_notification(
        self, dependency_manager
    ):
        """Test that dependency change callback sends WebSocket notification."""
        package_name = "lseg_analytics-1.0.0.dist-info"
        event_type = EventType.CREATED

        with patch(
            "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket"
        ) as mock_websocket:
            # Call the callback
            dependency_manager._dependency_change_callback(package_name, event_type)

            # Verify WebSocket notification was sent
            mock_websocket.send_dependency_change_notification.assert_called_once_with(
                package_name, event_type.value
            )

    def test_dependency_change_callback_handles_websocket_error(
        self, dependency_manager
    ):
        """Test that dependency change callback handles WebSocket errors gracefully."""
        package_name = "lseg_analytics-1.0.0.dist-info"
        event_type = EventType.MODIFIED

        with patch(
            "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket"
        ) as mock_websocket:
            # Mock WebSocket to raise exception
            mock_websocket.send_dependency_change_notification.side_effect = Exception(
                "WebSocket error"
            )

            # Should not raise exception
            dependency_manager._dependency_change_callback(package_name, event_type)

            # Verify notification was attempted
            mock_websocket.send_dependency_change_notification.assert_called_once_with(
                package_name, event_type.value
            )

    @pytest.mark.parametrize(
        "event_type",
        [EventType.CREATED, EventType.MODIFIED, EventType.DELETED, EventType.CHANGED],
    )
    def test_dependency_change_callback_with_different_event_types(
        self, dependency_manager, event_type
    ):
        """Test dependency change callback with different event types."""
        package_name = "lseg_analytics-2.0.0.dist-info"

        with patch(
            "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket"
        ) as mock_websocket:
            # Call the callback
            dependency_manager._dependency_change_callback(package_name, event_type)

            # Verify WebSocket notification was sent with correct event type
            mock_websocket.send_dependency_change_notification.assert_called_once_with(
                package_name, event_type.value
            )

    def test_dependency_change_callback_import_error_handling(self, dependency_manager):
        """Test handling of import errors in dependency change callback."""
        package_name = "lseg_analytics-1.0.0.dist-info"
        event_type = EventType.CREATED

        # Mock the import to raise ImportError
        with patch("builtins.__import__", side_effect=ImportError("Module not found")):
            # Should not raise exception
            dependency_manager._dependency_change_callback(package_name, event_type)

    def test_dependency_change_callback_logging(self, dependency_manager):
        """Test that dependency change callback logs appropriately."""
        package_name = "lseg_analytics-1.0.0.dist-info"
        event_type = EventType.CREATED

        with patch("lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket"):
            with patch(
                "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main"
            ) as mock_logger:
                # Call the callback
                dependency_manager._dependency_change_callback(package_name, event_type)

                # Verify debug log was called (changed from info to debug per Duncan's review)
                mock_logger.debug.assert_called_with(
                    f"[DependencyWatcherManager] Dependency change detected for package: {package_name} ({event_type.value})"
                )

                # Verify no error log was called (since no exception occurred)
                mock_logger.error.assert_not_called()

    def test_dependency_change_callback_error_logging(self, dependency_manager):
        """Test that dependency change callback logs errors appropriately."""
        package_name = "lseg_analytics-1.0.0.dist-info"
        event_type = EventType.CREATED
        error_message = "WebSocket connection failed"

        with patch(
            "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket"
        ) as mock_websocket:
            with patch(
                "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main"
            ) as mock_logger:
                # Mock WebSocket to raise exception
                mock_websocket.send_dependency_change_notification.side_effect = (
                    Exception(error_message)
                )

                # Call the callback
                dependency_manager._dependency_change_callback(package_name, event_type)

                # Verify error log was called
                mock_logger.error.assert_called_with(
                    f"[DependencyWatcherManager] Error sending WebSocket notification: {error_message}"
                )

    @pytest.mark.parametrize(
        "package_name,event_type",
        [
            ("lseg_analytics-1.0.0.dist-info", EventType.CREATED),
            ("lseg_analytics-1.1.0.dist-info", EventType.MODIFIED),
            ("lseg_analytics-2.0.0.dist-info", EventType.DELETED),
        ],
    )
    def test_dependency_change_callback_multiple_packages(
        self, dependency_manager, package_name, event_type
    ):
        """Test dependency change callback with different packages and event types."""
        with patch(
            "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket"
        ) as mock_websocket:
            dependency_manager._dependency_change_callback(package_name, event_type)

            # Verify notification was sent with correct arguments
            mock_websocket.send_dependency_change_notification.assert_called_once_with(
                package_name, event_type.value
            )

    def test_dependency_change_callback_concurrent_calls(self, dependency_manager):
        """Test dependency change callback with concurrent calls."""
        import threading
        import time

        package_name = "lseg_analytics-1.0.0.dist-info"
        event_type = EventType.CREATED
        num_threads = 5

        with patch(
            "lseg_analytics_jupyterlab.src.handlers.webSocketHandler.WebSocket"
        ) as mock_websocket:
            # Add a small delay to simulate processing time
            mock_websocket.send_dependency_change_notification.side_effect = (
                lambda p, e: time.sleep(0.1)
            )

            threads = []
            for i in range(num_threads):
                thread = threading.Thread(
                    target=dependency_manager._dependency_change_callback,
                    args=(f"{package_name}-{i}", event_type),
                )
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Verify all notifications were sent
            assert (
                mock_websocket.send_dependency_change_notification.call_count
                == num_threads
            )
