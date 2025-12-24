# type: ignore
import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock, Mock
from lseg_analytics_jupyterlab.src.handlers.packageMetadataHandler import (
    PackageMetadataHandler,
)
from tornado.web import Application
from tornado.httputil import HTTPServerRequest


# Fixture to create a Tornado application with the PackageMetadataHandler
@pytest.fixture
def app():
    return Application(
        [(r"/api/lseg-analytics-jupyterlab/package-metadata", PackageMetadataHandler)]
    )


# Fixture to create a mock HTTP request
@pytest.fixture
def http_request():
    request = HTTPServerRequest(
        uri="/api/lseg-analytics-jupyterlab/package-metadata?packageRootFolderPath=c:\\project\\.venv\\Lib\\site-packages\\lseg_analytics"
    )
    request.connection = Mock()  # Mock the connection attribute
    return request


# Fixture to create an instance of PackageMetadataHandler with the mock application and request
@pytest.fixture
def package_metadata_handler(app, http_request):
    handler = PackageMetadataHandler(app, http_request)
    handler.finish = MagicMock()  # Mock the finish method
    handler.set_status = MagicMock()  # Mock the set_status method
    return handler


# Test case for the get method of PackageMetadataHandler
@patch("os.path.exists")
@patch("os.listdir")
@patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
def test_get(
    mock_open,
    mock_listdir,
    mock_path_exists,
    package_metadata_handler,
):
    # Mock path exists to return True
    mock_path_exists.return_value = True

    # Mock listdir to return JSON files
    mock_listdir.return_value = ["file1.json", "file2.json"]

    # Call the get method
    package_metadata_handler.get()

    # Expected combined metadata
    expected_response = {
        "status": "success",
        "message": "Metadata fetched successfully",
        "data": {
            "file1.json": {"key": "value"},
            "file2.json": {"key": "value"},
        },
        "error": None,
    }

    # Assert that the finish method was called with the expected response
    package_metadata_handler.finish.assert_called_once_with(
        json.dumps(expected_response)
    )


# Test case for missing package parameter
def test_get_missing_package(package_metadata_handler):
    # Override the get_argument method to return None
    package_metadata_handler.get_argument = MagicMock(return_value=None)

    # Call the get method
    package_metadata_handler.get()

    # Expected response
    expected_response = {
        "status": "error",
        "message": "Missing 'packageRootFolderPath' query parameter",
        "data": None,
        "error": None,
    }

    # Assert that the status was set to 400
    package_metadata_handler.set_status.assert_called_once_with(400)
    # Assert that the finish method was called with the expected response
    package_metadata_handler.finish.assert_called_once_with(
        json.dumps(expected_response)
    )


# Test case for the read_and_combine_json_files method
@patch("os.path.exists")
@patch("os.listdir")
@patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
def test_read_and_combine_json_files(
    mock_open,
    mock_listdir,
    mock_path_exists,
    package_metadata_handler,
):
    # Mock path exists to return True
    mock_path_exists.return_value = True

    # Mock listdir to return JSON files
    mock_listdir.return_value = ["file1.json", "file2.json"]

    # Call the read_and_combine_json_files method
    combined_metadata = package_metadata_handler.read_and_combine_json_files(
        "lseg_analytics"
    )

    # Expected combined metadata
    expected_metadata = {"file1.json": {"key": "value"}, "file2.json": {"key": "value"}}

    # Assert that the combined metadata is as expected
    assert combined_metadata == expected_metadata


# Test case for metadata directory not found
@patch("os.path.exists")
def test_metadata_directory_not_found(mock_path_exists, package_metadata_handler):
    # Mock path exists to return False
    mock_path_exists.return_value = False

    # Call the read_and_combine_json_files method
    combined_metadata = package_metadata_handler.read_and_combine_json_files(
        "lseg_analytics"
    )

    # Assert that the combined metadata is empty
    assert combined_metadata == {}


# Test case for an empty directory
@patch("os.path.exists")
@patch("os.listdir")
def test_empty_directory(mock_listdir, mock_path_exists, package_metadata_handler):
    # Mock path exists to return True
    mock_path_exists.return_value = True

    # Mock listdir to return empty list
    mock_listdir.return_value = []

    # Call the read_and_combine_json_files method
    combined_metadata = package_metadata_handler.read_and_combine_json_files(
        "lseg_analytics"
    )

    # Assert that the combined metadata is empty
    assert combined_metadata == {}


# Test case for non-JSON files in the directory
@patch("os.path.exists")
@patch("os.listdir")
@patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
def test_non_json_files_are_ignored(
    mock_open,
    mock_listdir,
    mock_path_exists,
    package_metadata_handler,
):
    # Mock path exists to return True
    mock_path_exists.return_value = True

    # Mock listdir to return JSON and non-JSON files
    mock_listdir.return_value = ["file1.txt", "file2.json"]

    # Call the read_and_combine_json_files method
    combined_metadata = package_metadata_handler.read_and_combine_json_files(
        "lseg_analytics"
    )

    # Expected combined metadata
    expected_metadata = {"file2.json": {"key": "value"}}

    # Assert that the combined metadata is as expected
    assert combined_metadata == expected_metadata


# Test case for file reading errors
@patch("os.path.exists")
@patch("os.listdir")
@patch("builtins.open", new_callable=mock_open)
def test_file_reading_error(
    mock_open,
    mock_listdir,
    mock_path_exists,
    package_metadata_handler,
):
    # Mock path exists to return True
    mock_path_exists.return_value = True

    # Mock listdir to return JSON files
    mock_listdir.return_value = ["file1.json"]

    # Mock open to raise an exception
    mock_open.side_effect = IOError

    # Call the read_and_combine_json_files method
    combined_metadata = package_metadata_handler.read_and_combine_json_files(
        "lseg_analytics"
    )

    # Assert that the combined metadata is empty
    assert combined_metadata == {}


# Test case for no metadata files found
@patch("os.path.exists")
@patch("os.listdir")
@patch("lseg_analytics_jupyterlab.src.handlers.packageMetadataHandler.logger_main")
def test_no_metadata_files_found(
    mock_logger,
    mock_listdir,
    mock_path_exists,
    package_metadata_handler,
):
    # Set up logger mock with all required methods
    mock_logger.warn = MagicMock()
    mock_logger.debug = MagicMock()
    mock_logger.error = MagicMock()

    # Mock path exists to return True
    mock_path_exists.return_value = True

    # Mock listdir to return no JSON files
    mock_listdir.return_value = ["file1.txt", "file2.py"]

    # Call the get method
    package_metadata_handler.get()

    # value for path passed in the mock htrp request
    package_root_folder_path = "c:\\project\\.venv\\Lib\\site-packages\\lseg_analytics"

    # Expected response
    expected_response = {
        "status": "error",
        "message": "No metadata files found",
        "data": None,
        "error": f"location: {package_root_folder_path}",
    }

    # Assert that the finish method was called with the expected response
    package_metadata_handler.finish.assert_called_once_with(
        json.dumps(expected_response)
    )
