# type: ignore
import os
import tempfile
import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call
from watchdog.observers import Observer
from lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager import (
    DependencyWatcherManager,
)
from lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler import EventType


@pytest.fixture
def manager():
    """Create a DependencyWatcherManager instance for testing."""
    return DependencyWatcherManager()


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestDependencyWatcherManager:
    def test_prepare_dependency_paths_normalizes_and_deduplicates(self, manager):
        """_prepare_dependency_paths should normalize, deduplicate, and ignore empty entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = os.path.join(temp_dir, "packages")
            os.makedirs(target_dir)

            duplicate_path = target_dir + os.sep  # Same path with trailing separator
            equivalent_path = os.path.join(target_dir, "..", "packages")

            dependencies = [target_dir, duplicate_path, "", equivalent_path]

            result = manager._prepare_dependency_paths(dependencies)

            assert result == [os.path.normpath(target_dir)]

    def test_maybe_restart_watchers_not_watching(self, manager):
        """When not currently watching, _maybe_restart_watchers should not request a restart."""
        with manager._lock:
            observers_to_join, skip_start = manager._maybe_restart_watchers(["/new"])

        assert observers_to_join == []
        assert skip_start is False

    def test_maybe_restart_watchers_same_directories(self, manager):
        """_maybe_restart_watchers should skip restarting when directories are unchanged."""
        manager._is_watching = True
        manager._watched_directories = ["/existing"]

        with patch(
            "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main"
        ) as mock_logger, manager._lock:
            observers_to_join, skip_start = manager._maybe_restart_watchers(
                ["/existing"]
            )

        assert observers_to_join == []
        assert skip_start is True
        mock_logger.debug.assert_called_once_with(
            "[DependencyWatcherManager] Dependency watching already active for requested directories"
        )

    def test_maybe_restart_watchers_restart_required(self, manager):
        """_maybe_restart_watchers should stop current observers when directories change."""
        mock_observer = Mock()
        mock_observer.is_alive.return_value = True

        manager._is_watching = True
        manager._observers = [mock_observer]
        manager._watched_directories = ["/old"]

        with patch(
            "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main"
        ) as mock_logger, manager._lock:
            observers_to_join, skip_start = manager._maybe_restart_watchers(["/new"])

        assert observers_to_join == [mock_observer]
        assert skip_start is False
        mock_observer.stop.assert_called_once()
        mock_logger.debug.assert_any_call(
            "[DependencyWatcherManager] Restarting dependency watching for updated directories"
        )
        mock_logger.debug.assert_any_call(
            "[DependencyWatcherManager] Stopping dependency watching for 1 observers"
        )

    def test_init(self, manager):
        """Test manager initialization."""
        assert manager._observers == []
        assert manager._is_watching is False
        assert isinstance(manager._lock, type(threading.RLock()))

    def test_is_watching_initial_state(self, manager):
        """Test initial watching state."""
        assert manager.is_watching() is False

    def test_get_watched_directories_count_initial(self, manager):
        """Test initial watched directories count."""
        assert manager.get_watched_directories_count() == 0

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.Observer")
    @patch(
        "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.DependencyChangeHandler"
    )
    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_start_watching_success(
        self,
        mock_logger,
        mock_handler_class,
        mock_observer_class,
        manager,
        temp_directory,
    ):
        """Test successful start of watching."""
        # Setup mocks
        mock_handler = Mock()
        mock_observer = Mock()
        mock_handler_class.return_value = mock_handler
        mock_observer_class.return_value = mock_observer

        dependencies = [temp_directory]

        manager.start_watching(dependencies)

        # Verify observer was configured and started
        mock_observer.schedule.assert_called_once_with(
            mock_handler, temp_directory, recursive=True
        )
        mock_observer.start.assert_called_once()

        # Verify internal state
        assert manager.is_watching() is True
        assert manager.get_watched_directories_count() == 1
        assert len(manager._observers) == 1

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.Observer")
    @patch(
        "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.DependencyChangeHandler"
    )
    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_start_watching_same_dependencies_no_restart(
        self,
        mock_logger,
        mock_handler_class,
        mock_observer_class,
        manager,
        temp_directory,
    ):
        """Test reusing existing watchers when the same dependencies are requested."""

        mock_handler = Mock()
        mock_observer = Mock()
        mock_observer.is_alive.return_value = True
        mock_handler_class.return_value = mock_handler
        mock_observer_class.return_value = mock_observer

        manager.start_watching([temp_directory])

        assert manager.is_watching() is True
        assert manager.get_watched_directories_count() == 1

        mock_logger.reset_mock()
        mock_handler_class.reset_mock()
        mock_observer_class.reset_mock()

        manager.start_watching([temp_directory])

        mock_observer_class.assert_not_called()
        mock_handler_class.assert_not_called()
        mock_logger.warn.assert_not_called()
        assert manager.is_watching() is True
        assert manager.get_watched_directories_count() == 1

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_start_watching_no_dependencies_when_idle(self, mock_logger, manager):
        """Calling start_watching with no dependencies should log and keep watcher stopped."""
        manager.start_watching([])

        mock_logger.debug.assert_called_once_with(
            "[DependencyWatcherManager] No valid dependency directories provided"
        )
        assert manager.is_watching() is False
        assert manager.get_watched_directories_count() == 0

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_start_watching_nonexistent_path(self, mock_logger, manager):
        """Test starting watching with non-existent path."""
        nonexistent_path = "/nonexistent/path"
        normalized_path = os.path.normpath(nonexistent_path)

        with patch("os.path.exists", return_value=False):
            manager.start_watching([nonexistent_path])

        mock_logger.warn.assert_any_call(
            f"[DependencyWatcherManager] Dependency path does not exist: {normalized_path}"
        )
        assert manager.is_watching() is False
        assert manager.get_watched_directories_count() == 0

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_start_watching_file_instead_of_directory(self, mock_logger, manager):
        """Test starting watching with file path instead of directory."""
        file_path = "/some/file.txt"
        normalized_path = os.path.normpath(file_path)

        with patch("os.path.exists", return_value=True), patch(
            "os.path.isdir", return_value=False
        ):
            manager.start_watching([file_path])

        mock_logger.warn.assert_any_call(
            f"[DependencyWatcherManager] Dependency path is not a directory: {normalized_path}"
        )
        assert manager.is_watching() is False
        assert manager.get_watched_directories_count() == 0

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.Observer")
    @patch(
        "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.DependencyChangeHandler"
    )
    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_start_watching_exception(
        self,
        mock_logger,
        mock_handler_class,
        mock_observer_class,
        manager,
        temp_directory,
    ):
        """Test exception handling during start watching."""
        # Setup mocks
        mock_observer_class.side_effect = Exception("Test error")

        dependencies = [temp_directory]

        manager.start_watching(dependencies)

        # Verify error was logged
        mock_logger.error.assert_called_once_with(
            f"[DependencyWatcherManager] Failed to start watching {temp_directory}: Test error"
        )
        assert manager.is_watching() is False
        assert manager.get_watched_directories_count() == 0

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.Observer")
    @patch(
        "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.DependencyChangeHandler"
    )
    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_start_watching_no_dependencies_after_existing_watchers(
        self,
        mock_logger,
        mock_handler_class,
        mock_observer_class,
        manager,
        temp_directory,
    ):
        """start_watching([]) should stop existing observers and log monitoring stopped."""

        mock_handler_class.return_value = Mock()
        mock_observer = Mock()
        mock_observer.is_alive.return_value = True
        mock_observer_class.return_value = mock_observer

        manager.start_watching([temp_directory])

        assert manager.is_watching() is True

        manager.start_watching([])

        mock_observer.stop.assert_called_once()
        mock_observer.join.assert_called_once_with(timeout=5.0)
        mock_logger.debug.assert_any_call(
            "[DependencyWatcherManager] Restarting dependency watching for updated directories"
        )
        mock_logger.debug.assert_any_call(
            "[DependencyWatcherManager] No valid dependency directories provided; monitoring stopped"
        )
        assert manager.is_watching() is False
        assert manager.get_watched_directories_count() == 0

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.Observer")
    @patch(
        "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.DependencyChangeHandler"
    )
    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_start_watching_switch_dependencies(
        self,
        mock_logger,
        mock_handler_class,
        mock_observer_class,
        manager,
    ):
        """Test switching monitoring to a new dependency path."""

        first_observer = Mock()
        first_observer.is_alive.return_value = True
        second_observer = Mock()
        second_observer.is_alive.return_value = True

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_observer_class.side_effect = [first_observer, second_observer]

        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            manager.start_watching([first_dir])
            assert manager.is_watching() is True
            assert manager.get_watched_directories_count() == 1

            manager.start_watching([second_dir])

            first_observer.stop.assert_called_once()
            first_observer.join.assert_called_once_with(timeout=5.0)
            second_observer.start.assert_called_once()
            assert manager.is_watching() is True
            assert manager.get_watched_directories_count() == 1

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_stop_watching_not_watching(self, mock_logger, manager):
        """Test stopping when not watching."""
        manager.stop_watching()

        mock_logger.debug.assert_called_once_with(
            "[DependencyWatcherManager] Dependency watching is not active"
        )

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_stop_watching_success(self, mock_logger, manager):
        """Test successful stop of watching."""
        # Setup mock observers
        mock_observer1 = Mock()
        mock_observer1.is_alive.return_value = True
        mock_observer2 = Mock()
        mock_observer2.is_alive.return_value = True

        # Set up manager state
        manager._observers = [mock_observer1, mock_observer2]
        manager._is_watching = True

        manager.stop_watching()

        # Verify observers were stopped and joined
        mock_observer1.stop.assert_called_once()
        mock_observer1.join.assert_called_once_with(timeout=5.0)
        mock_observer2.stop.assert_called_once()
        mock_observer2.join.assert_called_once_with(timeout=5.0)

        # Verify internal state was cleared
        assert manager._observers == []
        assert manager.is_watching() is False

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_stop_watching_observer_not_alive(self, mock_logger, manager):
        """Test stopping watching when observer is not alive."""
        mock_observer = Mock()
        mock_observer.is_alive.return_value = False

        manager._observers = [mock_observer]
        manager._is_watching = True

        manager.stop_watching()

        # Observer is not alive, so stop and join should NOT be called
        mock_observer.stop.assert_not_called()
        mock_observer.join.assert_not_called()

        assert manager.is_watching() is False

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_stop_watching_timeout_warning(self, mock_logger, manager):
        """Test warning when observer doesn't stop within timeout."""
        mock_observer = Mock()
        mock_observer.is_alive.side_effect = [True, True]  # Alive before and after join

        manager._observers = [mock_observer]
        manager._is_watching = True

        manager.stop_watching()

        mock_logger.warn.assert_called_once_with(
            "[DependencyWatcherManager] Observer did not stop gracefully within timeout"
        )

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_stop_watching_exception(self, mock_logger, manager):
        """Test exception handling during stop watching."""
        mock_observer = Mock()
        mock_observer.stop.side_effect = Exception("Stop error")

        manager._observers = [mock_observer]
        manager._is_watching = True

        manager.stop_watching()

        mock_logger.error.assert_called_once_with(
            "[DependencyWatcherManager] Error stopping observer: Stop error"
        )
        assert manager.is_watching() is False

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_join_observers_logs_error_on_exception(self, mock_logger, manager):
        """_join_observers should log and continue when join raises an exception."""
        mock_observer = Mock()
        mock_observer.join.side_effect = Exception("join failure")

        manager._join_observers([mock_observer])

        mock_logger.error.assert_called_once_with(
            "[DependencyWatcherManager] Error joining observer: join failure"
        )

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.Observer")
    @patch(
        "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.DependencyChangeHandler"
    )
    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.logger_main")
    def test_full_lifecycle(
        self,
        mock_logger,
        mock_handler_class,
        mock_observer_class,
        manager,
        temp_directory,
    ):
        """Test full lifecycle of starting and stopping watching."""
        # Setup mocks
        mock_handler = Mock()
        mock_observer = Mock()
        mock_observer.is_alive.return_value = True
        mock_handler_class.return_value = mock_handler
        mock_observer_class.return_value = mock_observer

        dependencies = [temp_directory]

        # Test start
        manager.start_watching(dependencies)
        assert manager.is_watching() is True
        assert manager.get_watched_directories_count() == 1

        # Test stop
        manager.stop_watching()
        assert manager.is_watching() is False
        assert manager.get_watched_directories_count() == 0

        # Verify observer lifecycle
        mock_observer.schedule.assert_called_once()
        mock_observer.start.assert_called_once()
        mock_observer.stop.assert_called_once()
        mock_observer.join.assert_called_once()

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.Observer")
    @patch(
        "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.DependencyChangeHandler"
    )
    def test_thread_safety(self, mock_handler_class, mock_observer_class, manager):
        """Test thread safety of the manager operations."""
        # Setup mocks
        mock_handler = Mock()
        mock_observer = Mock()
        mock_observer.is_alive.return_value = True
        mock_handler_class.return_value = mock_handler
        mock_observer_class.return_value = mock_observer

        def start_watching_thread():
            with tempfile.TemporaryDirectory() as temp_dir:
                manager.start_watching([temp_dir])

        def stop_watching_thread():
            time.sleep(0.1)  # Small delay to ensure start happens first
            manager.stop_watching()

        # Start threads
        start_thread = threading.Thread(target=start_watching_thread)
        stop_thread = threading.Thread(target=stop_watching_thread)

        start_thread.start()
        stop_thread.start()

        # Wait for completion
        start_thread.join()
        stop_thread.join()

        # Manager should be in stopped state
        assert manager.is_watching() is False
        assert manager.get_watched_directories_count() == 0

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.Observer")
    @patch(
        "lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager.DependencyChangeHandler"
    )
    def test_stop_watching_no_lock_contention(
        self, mock_handler_class, mock_observer_class, manager
    ):
        """Test that stop_watching doesn't hold the lock during join operations."""
        import threading
        import time

        # Setup mocks
        mock_handler = Mock()
        mock_observer = Mock()
        mock_observer.is_alive.return_value = True

        # Make join() take a long time to simulate the contention scenario
        def slow_join(timeout=None):
            time.sleep(0.5)  # Simulate slow shutdown

        mock_observer.join = slow_join

        mock_handler_class.return_value = mock_handler
        mock_observer_class.return_value = mock_observer

        # Start watching first
        with tempfile.TemporaryDirectory() as temp_dir:
            manager.start_watching([temp_dir])

            # Verify we're watching
            assert manager.is_watching() is True

            # Start stop_watching in a separate thread
            stop_thread = threading.Thread(target=manager.stop_watching)
            stop_thread.start()

            # Give the stop thread a moment to start and acquire the lock initially
            time.sleep(0.1)

            # Now try to call is_watching() - this should NOT be blocked by the join operation
            start_time = time.time()
            result = manager.is_watching()  # This should return quickly
            end_time = time.time()

            # The call should complete quickly (not blocked by join),
            # and should return False since observers were cleared before join
            assert (
                end_time - start_time
            ) < 0.2  # Should be much faster than the 0.5s join
            assert result is False  # State should be cleared immediately

            # Wait for stop thread to complete
            stop_thread.join()

            # Verify final state
            assert manager.is_watching() is False
            assert manager.get_watched_directories_count() == 0
