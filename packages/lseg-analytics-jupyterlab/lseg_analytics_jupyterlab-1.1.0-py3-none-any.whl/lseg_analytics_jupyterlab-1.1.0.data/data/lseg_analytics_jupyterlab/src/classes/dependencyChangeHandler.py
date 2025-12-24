import os
import re
from enum import Enum
from typing import Callable, Optional
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main


class EventType(Enum):
    """Enumeration of supported file system event types."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    CHANGED = "changed"


class DependencyChangeHandler(FileSystemEventHandler):
    """
    Handles file system events for dependency changes.

    This handler specifically watches for LSEG Analytics package changes by:
    - Monitoring METADATA file creation/deletion within .dist-info directories
    - Matching directory names against the pattern 'lseg_analytics_pricing-*.dist-info'
    - Only processing METADATA file events to ensure single notification per installation

    When a matching change is detected, it invokes the provided callback with
    the package name and event type.
    """

    def __init__(self, callback: Callable[[str, EventType], None]):
        """
        Initialize the handler with a callback function.

        Args:
            callback: Function to call when a matching dependency change is detected.
                     Takes package_name and event_type as parameters.
                     Event types: EventType.CREATED, EventType.MODIFIED, EventType.DELETED, EventType.CHANGED
        """
        super().__init__()
        self.callback = callback
        # Pattern to match METADATA files in LSEG Analytics Pricing .dist-info directories (case-insensitive)
        self.metadata_path_pattern = re.compile(
            r"lseg_analytics_pricing-\S+\.dist-info[/\\]METADATA$", re.IGNORECASE
        )

    def _is_lseg_analytics_metadata_file(self, file_path: str) -> bool:
        """
        Check if the file path matches a METADATA file in an LSEG Analytics Pricing .dist-info directory.

        Args:
            file_path: Full path to check
                      e.g., /site-packages/lseg_analytics_pricing-1.0.0.dist-info/METADATA

        Returns:
            True if the path matches the pattern, False otherwise
        """
        return bool(self.metadata_path_pattern.search(file_path))

    def _handle_file_system_event(self, event: FileSystemEvent, event_type: EventType):
        """
        Common handler for file system events.

        Only processes METADATA file events within .dist-info directories to ensure
        a single notification per package installation/uninstallation.

        Important: This watches for METADATA file changes within .dist-info directories
        (like lseg_analytics_pricing-1.0.0.dist-info/METADATA).

        Args:
            event: The file system event
            event_type: Type of event (EventType enum)
        """
        try:
            src_path = event.src_path
            # Normalize path to string (watchdog may return bytes on some platforms)
            if isinstance(src_path, (bytes, bytearray, memoryview)):
                src_path = bytes(src_path).decode("utf-8", errors="ignore")
            elif not isinstance(src_path, str):
                src_path = str(src_path)

            # Normalize path separators
            normalized_path = os.path.normpath(src_path)

            if self._is_lseg_analytics_metadata_file(normalized_path):
                # Extract package name from path for logging
                parent_dir = os.path.dirname(normalized_path)
                package_name = os.path.basename(parent_dir)

                logger_main.debug(
                    f"[DependencyChangeHandler] Dependency {event_type}: {package_name} at {event.src_path}"
                )
                # Invoke the callback with the package name and event type
                self.callback(package_name, event_type)
        except Exception as e:
            logger_main.error(
                f"[DependencyChangeHandler] Error handling {event_type} event for {event.src_path}: {e}"
            )

    def on_created(self, event: FileSystemEvent):
        """Handle file creation events for METADATA files."""
        if not event.is_directory:
            self._handle_file_system_event(event, EventType.CREATED)

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events for METADATA files.

        Note: We ignore MODIFIED events because they cause duplicate notifications.
        During installation, pip creates METADATA and then immediately modifies it,
        triggering both CREATE and MODIFY events. We only need CREATE for installation
        detection and DELETE for uninstallation detection.
        """
        pass

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events for METADATA files."""
        if not event.is_directory:
            self._handle_file_system_event(event, EventType.DELETED)
