from typing import Awaitable, Optional, Union, ClassVar, Any, Dict, List
import tornado
import tornado.websocket
from tornado.ioloop import IOLoop
import threading
import json
from lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager import (
    DependencyWatcherManager,
)
from lseg_analytics_jupyterlab.src.constants.message_types import MessageType
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main


class WebSocket(tornado.websocket.WebSocketHandler):
    """
    WebSocket handler for Jupyter server extension.

    Connection Management:
    - Multiple instances can exist, but only one active connection is supported
    - Class-level variables track the active connection
    - References global dependency manager created in main.py for shared state
    Note: Creating a new connection will automatically close any previous active connection
    to ensure only one WebSocket connection is active at a time.
    """

    _active_instance: ClassVar[Optional["WebSocket"]] = None
    _main_ioloop: ClassVar[Optional[IOLoop]] = None
    _lock: ClassVar[threading.RLock] = threading.RLock()

    def __init__(self, *args, **kwargs):
        """Initialize WebSocket handler instance."""
        super().__init__(*args, **kwargs)
        # Each instance gets created normally by Tornado

    @classmethod
    def _get_dependency_watcher_manager(cls) -> DependencyWatcherManager:
        """Get the global dependency watcher manager from main.py."""
        # Dynamic import prevents circular dependency: main.py imports this module,
        # so importing main.py at module level would create a circular import.
        # This affects both production and test environments.
        from lseg_analytics_jupyterlab.main import dependency_manager

        return dependency_manager

    def open(self, *args: Any, **kwargs: Any) -> Optional[Awaitable[None]]:
        """Handle WebSocket connection opening."""
        with WebSocket._lock:
            # Close any previous active connection
            if WebSocket._active_instance and WebSocket._active_instance != self:
                try:
                    WebSocket._active_instance.close()
                    logger_main.debug("[WebSocketHandler] Closed previous connection")
                except Exception as e:
                    logger_main.debug(
                        f"[WebSocketHandler] Error closing previous connection: {e}"
                    )

            # Set this as the active instance
            WebSocket._active_instance = self

            # Store the IOLoop when the connection is established
            if WebSocket._main_ioloop is None:
                WebSocket._main_ioloop = IOLoop.current()

            logger_main.debug("[WebSocketHandler] WebSocket connection opened")
            logger_main.debug(
                f"[WebSocketHandler] Active connection state: {WebSocket._active_instance is not None}"
            )

    def on_message(self, message: Union[str, bytes]) -> None:
        """Handle incoming WebSocket messages."""
        try:
            # Parse the incoming message
            if isinstance(message, bytes):
                message = message.decode("utf-8")

            message_data = json.loads(message)
            logger_main.debug(f"[WebSocketHandler] Received message: {message_data}")

            if isinstance(message_data, dict):
                message_type = message_data.get("message_type")
                if message_type == MessageType.ENABLEMENT_STATUS:
                    self._handle_enablement_status_message(
                        message_data.get("message", {})
                    )
                    return

            # Handle control messages for dependency watching
            if "watch" in message_data:
                self._handle_watch_message(message_data)
            else:
                # Echo back the message for backward compatibility
                try:
                    self.write_message(message)
                except Exception as write_error:
                    logger_main.error(
                        f"[WebSocketHandler] Failed to write message back to client: {write_error}"
                    )

        except json.JSONDecodeError as e:
            logger_main.error(f"[WebSocketHandler] Failed to parse JSON message: {e}")
        except Exception as e:
            logger_main.error(f"[WebSocketHandler] Error handling message: {e}")

    def _handle_watch_message(self, message_data: Dict[str, Any]) -> None:
        """Handle watch control messages for dependency monitoring."""
        try:
            watch = message_data.get("watch", False)
            path = message_data.get("path", [])

            dependency_manager = self._get_dependency_watcher_manager()

            if watch:
                # Start watching dependencies
                if isinstance(path, list) and path:
                    logger_main.debug(
                        f"[WebSocketHandler] Starting dependency watching for {len(path)} paths"
                    )
                    dependency_manager.start_watching(path)
                else:
                    logger_main.warn(
                        "[WebSocketHandler] WatchDependenciesStart message missing or invalid 'path' field"
                    )
            else:
                # Stop watching dependencies
                logger_main.debug("[WebSocketHandler] Stopping dependency watching")
                dependency_manager.stop_watching()

        except Exception as e:
            logger_main.error(f"[WebSocketHandler] Error handling watch message: {e}")

    def on_close(self) -> None:
        """Handle WebSocket connection closing."""
        logger_main.debug("[WebSocketHandler] WebSocket connection closed")

        # Clean up connection state and resources
        with WebSocket._lock:
            # Only clean up if this is the active instance
            if WebSocket._active_instance == self:
                # Stop dependency watching when connection is lost
                try:
                    dependency_manager = self._get_dependency_watcher_manager()
                    if dependency_manager.is_watching():
                        logger_main.debug(
                            "[WebSocketHandler] Stopping dependency watching due to connection closure"
                        )
                        dependency_manager.stop_watching()
                except Exception as e:
                    logger_main.error(
                        f"[WebSocketHandler] Error stopping dependency watching on close: {e}"
                    )

                # Clear active instance reference
                WebSocket._active_instance = None

        logger_main.debug("[WebSocketHandler] WebSocket connection cleanup completed")

    @classmethod
    def send_dependency_change_notification(
        cls, package_name: str, event_type: str
    ) -> None:
        """Send dependency change notification to client."""
        try:
            # Create the message payload following the client-side DependencyChangedPayload type
            notification_message = {
                "message_type": MessageType.DEPENDENCY_CHANGED,
                "message": {
                    "event_type": event_type,
                    "packageName": package_name,  # Using packageName as requested
                },
            }

            message_json = json.dumps(notification_message)
            cls.send_message_to_client(message_json)

            logger_main.debug(
                f"[WebSocketHandler] Sent dependency change notification: {package_name} ({event_type})"
            )

        except Exception as e:
            logger_main.error(
                f"[WebSocketHandler] Error sending dependency change notification: {e}"
            )

    @classmethod
    def send_message_to_client(cls, message: Union[str, bytes]) -> None:
        """Send message to the client if WebSocket is connected."""
        if cls._active_instance and cls._main_ioloop:
            # Check if the active instance has a valid connection
            try:
                # Check if the connection is still open by accessing the stream
                if (
                    hasattr(cls._active_instance, "ws_connection")
                    and cls._active_instance.ws_connection
                    and hasattr(cls._active_instance.ws_connection, "stream")
                    and cls._active_instance.ws_connection.stream
                    and not cls._active_instance.ws_connection.stream.closed()
                ):

                    cls._main_ioloop.add_callback(cls._active_instance.write_message, message)  # type: ignore
                    return
            except Exception:
                # Clear stale active instance reference without logging to avoid recursion
                with cls._lock:
                    cls._active_instance = None
                # Fallback: log to server console for debugging
                print(
                    f"[WebSocketHandler] Connection validation failed, cleared stale instance"
                )

        # Silently fail when no connection - no logging to avoid recursion with logger service

    @classmethod
    def _reset_singleton(cls) -> None:
        """Reset connection state for testing purposes."""
        with cls._lock:
            cls._active_instance = None
            cls._main_ioloop = None

    @classmethod
    def _reset_connection_state(cls) -> None:
        """Reset connection state while preserving ioloop.

        This method is used for testing purposes to reset only the active connection
        state without clearing the IOLoop, unlike _reset_singleton which clears everything.
        """
        with cls._lock:
            cls._active_instance = None
            logger_main.debug("[WebSocketHandler] Connection state reset")

    @classmethod
    def _get_enablement_status_service(cls):
        from lseg_analytics_jupyterlab.main import enablement_status_service

        return enablement_status_service

    def _handle_enablement_status_message(self, payload: Dict[str, Any]) -> None:
        try:
            has_lfa_access = (
                bool(payload.get("hasLfaAccess"))
                if isinstance(payload, dict)
                else False
            )

            enablement_status_service = self._get_enablement_status_service()
            enablement_status_service.update_status(has_lfa_access)
            logger_main.debug(
                f"[WebSocketHandler] Updated enablement status to {has_lfa_access}"
            )
        except Exception as error:
            logger_main.error(
                f"[WebSocketHandler] Failed to process enablement status message: {error}"
            )
