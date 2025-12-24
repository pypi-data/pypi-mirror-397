import os
import threading
from typing import List, Tuple
from watchdog.observers import Observer
from lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler import (
    DependencyChangeHandler,
    EventType,
)
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main


class DependencyWatcherManager:
    """
    Manages Observer lifecycles, dispatches file-change events to the handler,
    and exposes start_watching()/stop_watching() methods.

    This manager specifically watches for LSEG Analytics package changes and handles
    the lifecycle of Watchdog Observer instances for dependency monitoring.
    """

    def __init__(self):
        """Initialize the dependency watcher manager."""
        self._observers: List[Observer] = []
        # Using RLock (Reentrant Lock) for thread safety to allow the same thread
        # to acquire the lock multiple times without deadlocking. This is important
        # since public methods may call each other and all need synchronization.
        # Key benefits:
        # 1. Prevents race conditions when multiple threads try to start/stop watching simultaneously
        # 2. Reentrant nature allows safe method composition without deadlocks
        # 3. Consistent state ensures _is_watching flag and observer lists stay synchronized
        self._lock = threading.RLock()
        self._is_watching = False
        self._watched_directories: List[str] = []

    def _dependency_change_callback(
        self, package_name: str, event_type: EventType
    ) -> None:
        """
        Callback function invoked when a dependency change is detected.

        This method sends WebSocket notifications to clients about LSEG Analytics
        package changes.

        Args:
            package_name: Name of the changed package
            event_type: Type of event (EventType enum). Possible values: EventType.CREATED, EventType.MODIFIED, EventType.DELETED
        """
        logger_main.debug(
            f"[DependencyWatcherManager] Dependency change detected for package: {package_name} ({event_type.value})"
        )

        # Send WebSocket notification to clients
        try:
            # Dynamic import prevents circular dependency: WebSocket imports this module,
            # so importing WebSocket at module level would create a circular import.
            # This affects both production and test environments.
            from lseg_analytics_jupyterlab.src.handlers.webSocketHandler import (
                WebSocket,
            )

            WebSocket.send_dependency_change_notification(
                package_name, event_type.value
            )
        except Exception as e:
            logger_main.error(
                f"[DependencyWatcherManager] Error sending WebSocket notification: {e}"
            )

    def _normalize_path(self, path: str) -> str:
        """Return a normalized version of the dependency path for comparison."""
        return os.path.normcase(os.path.abspath(os.path.normpath(path)))

    def _prepare_dependency_paths(self, dependencies: List[str]) -> List[str]:
        """Normalize dependency paths and remove duplicates while preserving order."""
        unique_paths = []
        seen_normalized = set()

        for dependency_path in dependencies:
            if not dependency_path:
                continue

            normalized = self._normalize_path(dependency_path)
            if normalized in seen_normalized:
                continue

            seen_normalized.add(normalized)
            unique_paths.append(os.path.normpath(dependency_path))

        return unique_paths

    def _stop_watching_locked(self) -> List[Observer]:
        """Internal helper to stop observers. Caller must hold the lock."""
        observers_to_stop: List[Observer] = []

        if not self._is_watching:
            return observers_to_stop

        logger_main.debug(
            f"[DependencyWatcherManager] Stopping dependency watching for {len(self._observers)} observers"
        )

        for observer in self._observers:
            try:
                if observer.is_alive():
                    observer.stop()
                    observers_to_stop.append(observer)
            except Exception as e:
                logger_main.error(
                    f"[DependencyWatcherManager] Error stopping observer: {e}"
                )

        self._observers.clear()
        self._watched_directories.clear()
        self._is_watching = False

        return observers_to_stop

    def _maybe_restart_watchers(
        self, requested_normalized: List[str]
    ) -> Tuple[List[Observer], bool]:
        """Determine if watchers need restarting and return observers to join."""
        if not self._is_watching:
            return [], False

        if requested_normalized == self._watched_directories:
            logger_main.debug(
                "[DependencyWatcherManager] Dependency watching already active for requested directories"
            )
            return [], True

        logger_main.debug(
            "[DependencyWatcherManager] Restarting dependency watching for updated directories"
        )
        return self._stop_watching_locked(), False

    def _handle_no_dependencies(self, had_previous_watchers: bool) -> None:
        """Log and reset state when no dependency directories are provided."""
        message = (
            "[DependencyWatcherManager] No valid dependency directories provided; monitoring stopped"
            if had_previous_watchers
            else "[DependencyWatcherManager] No valid dependency directories provided"
        )
        logger_main.debug(message)
        self._observers.clear()
        self._watched_directories.clear()
        self._is_watching = False

    def _start_new_watchers(
        self, dependencies_with_normalized: List[Tuple[str, str]]
    ) -> None:
        """Start observers for the provided dependency paths."""
        self._observers.clear()
        self._watched_directories.clear()

        logger_main.debug(
            f"[DependencyWatcherManager] Starting dependency watching for {len(dependencies_with_normalized)} directories"
        )

        for dependency_path, normalized_path in dependencies_with_normalized:
            try:
                if not os.path.exists(dependency_path):
                    logger_main.warn(
                        f"[DependencyWatcherManager] Dependency path does not exist: {dependency_path}"
                    )
                    continue

                if not os.path.isdir(dependency_path):
                    logger_main.warn(
                        f"[DependencyWatcherManager] Dependency path is not a directory: {dependency_path}"
                    )
                    continue

                handler = DependencyChangeHandler(self._dependency_change_callback)
                observer = Observer()

                observer.schedule(handler, dependency_path, recursive=True)
                observer.start()

                self._observers.append(observer)
                self._watched_directories.append(normalized_path)

                logger_main.debug(
                    f"[DependencyWatcherManager] Started watching dependency directory: {dependency_path}"
                )

            except Exception as e:
                logger_main.error(
                    f"[DependencyWatcherManager] Failed to start watching {dependency_path}: {e}"
                )

        self._is_watching = bool(self._observers)

        if self._is_watching:
            logger_main.debug(
                f"[DependencyWatcherManager] Dependency watching started successfully for {len(self._observers)} directories"
            )
        else:
            logger_main.debug(
                "[DependencyWatcherManager] No dependency directories are being watched"
            )

    def _join_observers(self, observers: List[Observer]) -> None:
        """Join observer threads outside the lock."""
        for observer in observers:
            try:
                observer.join(timeout=5.0)
                if observer.is_alive():
                    logger_main.warn(
                        "[DependencyWatcherManager] Observer did not stop gracefully within timeout"
                    )
            except Exception as e:
                logger_main.error(
                    f"[DependencyWatcherManager] Error joining observer: {e}"
                )

    def start_watching(self, dependencies: List[str]) -> None:
        """
        Create and start Watchdog Observers with the handler for each dependency directory.

        Args:
            dependencies: List of directory paths to watch for dependency changes
        """
        prepared_dependencies = self._prepare_dependency_paths(dependencies)
        normalized_pairs = [
            (dependency_path, self._normalize_path(dependency_path))
            for dependency_path in prepared_dependencies
        ]
        requested_normalized = [normalized for _, normalized in normalized_pairs]

        observers_to_join: List[Observer] = []
        return_after_join = False

        with self._lock:
            observers_to_join, skip_start = self._maybe_restart_watchers(
                requested_normalized
            )
            if skip_start:
                return

            if not normalized_pairs:
                self._handle_no_dependencies(bool(observers_to_join))
                return_after_join = True
            else:
                self._start_new_watchers(normalized_pairs)

        self._join_observers(observers_to_join)

        if return_after_join:
            return

    def stop_watching(self) -> None:
        """
        Stop and join all observers and clear internal lists.
        """
        # Get observers to stop while holding the lock, then release it before join operations
        observers_to_stop: List[Observer] = []
        with self._lock:
            if not self._is_watching:
                logger_main.debug(
                    "[DependencyWatcherManager] Dependency watching is not active"
                )
                return

            observers_to_stop = self._stop_watching_locked()

        # Now join observers WITHOUT holding the lock to avoid lock contention
        self._join_observers(observers_to_stop)

        logger_main.debug("[DependencyWatcherManager] Stopped all dependency watchers")

    def is_watching(self) -> bool:
        """
        Check if dependency watching is currently active.

        Returns:
            True if watching is active, False otherwise
        """
        with self._lock:
            return self._is_watching

    def get_watched_directories_count(self) -> int:
        """
        Get the number of directories currently being watched.

        Returns:
            Number of active observers
        """
        with self._lock:
            return len(self._observers)
