# type: ignore
import pytest
from unittest.mock import Mock, patch
from watchdog.events import DirDeletedEvent
from lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler import (
    DependencyChangeHandler,
    EventType,
)


@pytest.fixture
def mock_callback():
    """Mock callback function for testing."""
    return Mock()


@pytest.fixture
def handler(mock_callback):
    """Create a DependencyChangeHandler instance for testing."""
    return DependencyChangeHandler(mock_callback)


class TestDependencyChangeHandler:
    def test_init(self, mock_callback):
        """Test handler initialization."""
        handler = DependencyChangeHandler(mock_callback)
        assert handler.callback == mock_callback
        assert handler.metadata_path_pattern is not None

    @pytest.mark.parametrize(
        "file_path",
        [
            "/path/to/lseg_analytics_pricing-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics_pricing-2.1.3.dist-info/METADATA",
            "/path/to/LSEG_ANALYTICS_PRICING-1.0.0.DIST-INFO/METADATA",  # Case insensitive
            "/path/to/lseg_analytics_pricing-1.0.0-beta.dist-info/METADATA",
            "C:\\path\\to\\lseg_analytics_pricing-1.0.0.dist-info\\METADATA",  # Windows path
            "/path/to/lseg_analytics_pricing-1.0.0.dist-info/metadata",  # lowercase metadata
        ],
    )
    def test_is_lseg_analytics_metadata_file_valid_paths(self, handler, file_path):
        """Test pattern matching for valid LSEG analytics pricing METADATA file paths."""
        assert handler._is_lseg_analytics_metadata_file(
            file_path
        ), f"Pattern should match: {file_path}"

    @pytest.mark.parametrize(
        "file_path",
        [
            "/path/to/other_package-1.0.0.dist-info/METADATA",  # Different package
            "/path/to/lseg_analytics_pricing-1.0.0.dist-info/RECORD",  # Not METADATA file
            "/path/to/lseg_analytics_pricing-1.0.0.dist-info/",  # Directory
            "/path/to/lseg_analytics_pricing-1.0.0/METADATA",  # Missing .dist-info
            "/path/to/lseg_analytics_pricing.dist-info/METADATA",  # Missing version
            "/path/to/not_lseg-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics_pricing",  # Directory without version
            "/path/to/lseg_analytics-1.0.0.dist-info/METADATA",  # Different LSEG package (base analytics)
            "/path/to/lseg_analytics_basic_client-1.0.0.dist-info/METADATA",  # Different LSEG package
            "",
        ],
    )
    def test_is_lseg_analytics_metadata_file_invalid_paths(self, handler, file_path):
        """Test pattern matching for invalid file paths."""
        assert not handler._is_lseg_analytics_metadata_file(
            file_path
        ), f"Pattern should not match: {file_path}"

    def test_on_created_matching_metadata_file(self, handler, mock_callback):
        """Test handling METADATA file creation event for matching package."""
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/lseg_analytics_pricing-1.0.0.dist-info/METADATA"

        with patch(
            "lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler.logger_main"
        ):
            handler.on_created(event)

        mock_callback.assert_called_once_with(
            "lseg_analytics_pricing-1.0.0.dist-info", EventType.CREATED
        )

    def test_on_created_non_matching_metadata_file(self, handler, mock_callback):
        """Test handling METADATA file creation for non-matching package."""
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/other_package-1.0.0.dist-info/METADATA"

        handler.on_created(event)
        mock_callback.assert_not_called()

    def test_on_created_non_metadata_file(self, handler, mock_callback):
        """Test that non-METADATA files are ignored."""
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/lseg_analytics_pricing-1.0.0.dist-info/RECORD"

        handler.on_created(event)
        mock_callback.assert_not_called()

    def test_on_created_directory_event_ignored(self, handler, mock_callback):
        """Test that directory creation events are ignored."""
        event = Mock()
        event.is_directory = True
        event.src_path = "/path/to/lseg_analytics_pricing-1.0.0.dist-info"

        handler.on_created(event)
        mock_callback.assert_not_called()

    @pytest.mark.parametrize(
        "file_path",
        [
            "/path/to/lseg_other-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics_basic_client-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics_core-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics_utils-1.0.0.dist-info/METADATA",
            "/path/to/lseg_sdk-1.0.0.dist-info/METADATA",
            "/path/to/lseg_common-1.0.0.dist-info/METADATA",
        ],
    )
    def test_on_created_lseg_wheel_modules_ignored(
        self, handler, mock_callback, file_path
    ):
        """Test that METADATA file creation events for LSEG wheel modules are ignored."""
        event = Mock()
        event.is_directory = False
        event.src_path = file_path
        handler.on_created(event)

        # Verify no callback was triggered for this ignored module
        mock_callback.assert_not_called()

    def test_on_modified_metadata_file_ignored(self, handler, mock_callback):
        """Test that METADATA file modification events are ignored to prevent duplicates."""
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/lseg_analytics_pricing-1.0.0.dist-info/METADATA"

        handler.on_modified(event)
        mock_callback.assert_not_called()

    def test_on_modified_directory_ignored(self, handler, mock_callback):
        """Test that directory modification events are ignored."""
        event = Mock()
        event.is_directory = True
        event.src_path = "/path/to/lseg_analytics_pricing-1.0.0.dist-info/METADATA"

        handler.on_modified(event)
        mock_callback.assert_not_called()

    def test_on_deleted_matching_metadata_file(self, handler, mock_callback):
        """Test handling METADATA file deletion event for matching package."""
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/lseg_analytics_pricing-1.0.0.dist-info/METADATA"

        with patch(
            "lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler.logger_main"
        ):
            handler.on_deleted(event)

        mock_callback.assert_called_once_with(
            "lseg_analytics_pricing-1.0.0.dist-info", EventType.DELETED
        )

    def test_on_deleted_directory_ignored(self, handler, mock_callback):
        """Test that directory deletion events are ignored."""
        event = DirDeletedEvent("/path/to/lseg_analytics_pricing-1.0.0.dist-info")

        handler.on_deleted(event)
        mock_callback.assert_not_called()

    @patch("lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler.logger_main")
    def test_handle_file_system_event_exception(
        self, mock_logger, handler, mock_callback
    ):
        """Test error handling in file system event processing."""
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/lseg_analytics_pricing-1.0.0.dist-info/METADATA"

        with patch.object(
            handler,
            "_is_lseg_analytics_metadata_file",
            side_effect=Exception("Test error"),
        ):
            handler._handle_file_system_event(event, EventType.CREATED)

            mock_callback.assert_not_called()
            mock_logger.error.assert_called_once()

    def test_only_lseg_analytics_pricing_metadata_triggers_notification(
        self, handler, mock_callback
    ):
        """Test that only the lseg_analytics_pricing METADATA file triggers notifications."""
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/lseg_analytics_pricing-1.0.0.dist-info/METADATA"

        with patch(
            "lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler.logger_main"
        ):
            handler.on_created(event)

        # Verify METADATA file triggered callback
        mock_callback.assert_called_once_with(
            "lseg_analytics_pricing-1.0.0.dist-info", EventType.CREATED
        )

    def test_metadata_case_insensitive_triggers_notification(
        self, handler, mock_callback
    ):
        """Test that METADATA filename check is case-insensitive."""
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/lseg_analytics_pricing-1.0.0.dist-info/metadata"

        with patch(
            "lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler.logger_main"
        ):
            handler.on_created(event)

        # Verify lowercase metadata file also triggers callback
        mock_callback.assert_called_once_with(
            "lseg_analytics_pricing-1.0.0.dist-info", EventType.CREATED
        )

    @pytest.mark.parametrize(
        "file_path",
        [
            "/path/to/lseg_analytics_pricing/some_file.py",
            "/path/to/lseg_analytics-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics_basic_client-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics_core-1.0.0.dist-info/METADATA",
        ],
    )
    def test_other_lseg_packages_metadata_do_not_trigger_notification(
        self, handler, mock_callback, file_path
    ):
        """Test that METADATA files from other LSEG packages do not trigger notifications."""
        event = Mock()
        event.is_directory = False
        event.src_path = file_path
        handler.on_created(event)

        # Verify no callback was triggered
        mock_callback.assert_not_called()

    @pytest.mark.parametrize(
        "file_path",
        [
            "/path/to/lseg_analytics_pricing-1.0.0.dist-info/RECORD",
            "/path/to/lseg_analytics_pricing-1.0.0.dist-info/WHEEL",
            "/path/to/lseg_analytics_pricing-1.0.0.dist-info/top_level.txt",
        ],
    )
    def test_non_metadata_files_in_pricing_package_ignored(
        self, handler, mock_callback, file_path
    ):
        """Test that non-METADATA files in pricing package .dist-info are ignored."""
        event = Mock()
        event.is_directory = False
        event.src_path = file_path
        handler.on_created(event)

        # Verify no callback was triggered
        mock_callback.assert_not_called()

    @pytest.mark.parametrize(
        "file_path",
        [
            "/path/to/lseg_analytics/METADATA",
            "/path/to/lseg_analytics-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics_basic_client-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics_core-1.0.0.dist-info/METADATA",
            "/path/to/lseg_sdk-1.0.0.dist-info/METADATA",
        ],
    )
    def test_on_modified_other_lseg_packages_ignored(
        self, handler, mock_callback, file_path
    ):
        """Test that METADATA file modification events for other LSEG packages are ignored."""
        event = Mock()
        event.is_directory = False
        event.src_path = file_path
        handler.on_modified(event)

        # Verify no callback was triggered for this ignored module
        mock_callback.assert_not_called()

    @pytest.mark.parametrize(
        "file_path",
        [
            "/path/to/lseg_analytics_basic_client-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics-1.0.0.dist-info/METADATA",
            "/path/to/lseg_analytics_core-1.0.0.dist-info/METADATA",
            "/path/to/lseg_other-1.0.0.dist-info/METADATA",
        ],
    )
    def test_on_deleted_other_lseg_packages_ignored(
        self, handler, mock_callback, file_path
    ):
        """Test that METADATA file deletion events for other LSEG packages are ignored."""
        event = Mock()
        event.is_directory = False
        event.src_path = file_path
        handler.on_deleted(event)

        # Verify no callback was triggered for this ignored module
        mock_callback.assert_not_called()

    def test_bytes_path_handling(self, handler, mock_callback):
        """Test that byte paths are properly decoded."""
        event = Mock()
        event.is_directory = False
        event.src_path = b"/path/to/lseg_analytics_pricing-1.0.0.dist-info/METADATA"

        with patch(
            "lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler.logger_main"
        ):
            handler.on_created(event)

        mock_callback.assert_called_once_with(
            "lseg_analytics_pricing-1.0.0.dist-info", EventType.CREATED
        )

    def test_non_string_path_handling(self, handler, mock_callback):
        """Test that non-string paths are converted to strings."""
        from pathlib import Path

        event = Mock()
        event.is_directory = False
        event.src_path = Path(
            "/path/to/lseg_analytics_pricing-1.0.0.dist-info/METADATA"
        )

        with patch(
            "lseg_analytics_jupyterlab.src.classes.dependencyChangeHandler.logger_main"
        ):
            handler.on_created(event)

        mock_callback.assert_called_once_with(
            "lseg_analytics_pricing-1.0.0.dist-info", EventType.CREATED
        )
