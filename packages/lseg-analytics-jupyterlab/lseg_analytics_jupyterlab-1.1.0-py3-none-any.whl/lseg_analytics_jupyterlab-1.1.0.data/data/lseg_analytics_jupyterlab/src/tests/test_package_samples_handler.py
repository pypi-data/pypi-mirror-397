# type: ignore
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock, Mock
from lseg_analytics_jupyterlab.src.handlers.packageSamplesHandler import (
    PackageSamplesHandler,
)
from jupyter_server.base.handlers import APIHandler
from tornado.web import RequestHandler, Application
from tornado.httputil import HTTPServerRequest
from tornado.testing import AsyncHTTPTestCase, gen_test


# Fixture to create a Tornado application with the PackageSamplesHandler
@pytest.fixture
def app():
    return Application(
        [(r"/api/lseg-analytics-jupyterlab/package-samples", PackageSamplesHandler)]
    )


# Fixture to create a mock HTTP request
@pytest.fixture
def http_request():
    request = HTTPServerRequest(
        uri="/api/lseg-analytics-jupyterlab/package-samples?package=lseg_analytics",
    )
    request.connection = Mock()  # Mock the connection attribute
    return request


# Fixture to create an instance of PackageSamplesHandler with the mock application and request
@pytest.fixture
def package_metadata_handler(app, http_request):
    handler = PackageSamplesHandler(app, http_request)
    handler.finish = MagicMock()  # Mock the finish method
    handler.set_status = MagicMock()  # Mock the set_status method
    return handler


@pytest.mark.parametrize(
    "relative_path_to_samples, file_name",
    [
        (None, "sample.json"),
        ("", "sample.json"),
        ("lseg_analytics", None),
        ("lseg_analytics", ""),
    ],
)
def test_get_missing_or_empty_query_parameters(
    package_metadata_handler,
    relative_path_to_samples,
    file_name,
):

    # Call the get method with missing or empty query parameters
    _set_get_arguments(package_metadata_handler, relative_path_to_samples, file_name)

    package_metadata_handler.get()

    # Assert that the status was set to the expected status and the error message was returned
    package_metadata_handler.set_status.assert_called_once_with(400)
    package_metadata_handler.finish.assert_called_once_with(
        json.dumps(
            {
                "error": "Missing 'relative_path_to_samples' or 'file_path' query parameter"
            }
        )
    )


@patch("lseg_analytics_jupyterlab.src.handlers.packageSamplesHandler.files")
@patch("builtins.open", new_callable=mock_open)
@pytest.mark.parametrize(
    "file_name, file_content, expected_result",
    [
        ("sample.json", '{"key": "value"}', json.dumps({"key": "value"})),
        ("sample.py", "print('Hello, World!')", "print('Hello, World!')"),
        ("sample.ipynb", '{"cells": []}', '{"cells": []}'),
    ],
)
def test_get_supported_files(
    mock_open,
    mock_files,
    package_metadata_handler,
    file_name,
    file_content,
    expected_result,
):
    # Mock the return value of files().joinpath()
    mock_file_path = Mock()
    mock_file_path.__str__ = Mock(return_value=f"/fake/path/{file_name}")
    mock_file_path.is_file = Mock(return_value=True)
    mock_files.return_value.joinpath.return_value = mock_file_path

    # Mock the file content
    mock_open.return_value.read.return_value = file_content

    # Call the get method with the file
    _set_get_arguments(package_metadata_handler, "package/aaa/samples", file_name)
    package_metadata_handler.get()

    # Check the expected file was searched for
    mock_files.assert_called_once_with("package")
    mock_files.return_value.joinpath.assert_called_once_with("aaa/samples/" + file_name)
    # Check the expected file was opened
    mock_open.assert_called_once_with(f"/fake/path/{file_name}", "r", encoding="utf-8")

    # Assert that the finish method was called with the expected content and text/plain content type
    package_metadata_handler.finish.assert_called_once_with(
        expected_result, set_content_type="text/plain"
    )


@patch("lseg_analytics_jupyterlab.src.handlers.packageSamplesHandler.files")
def test_get_file_not_found(mock_files, package_metadata_handler):
    # Mock the return value of files().joinpath() to indicate file doesn't exist
    mock_file_path = Mock()
    mock_file_path.is_file = Mock(return_value=False)
    mock_files.return_value.joinpath.return_value = mock_file_path

    # Call the get method with a non-existent file
    _set_get_arguments(
        package_metadata_handler, "lseg_analytics/samples", "nonexistent.json"
    )
    package_metadata_handler.get()

    # Sanity check that the files mocks were called as expected
    mock_files.assert_called_once_with("lseg_analytics")
    mock_file_path.is_file.assert_called_once()

    # Assert that the status was set to 404 and the error message was returned
    package_metadata_handler.set_status.assert_called_once_with(404)
    package_metadata_handler.finish.assert_called_once_with(
        json.dumps({"error": "File not found"})
    )


def test_get_unsupported_file_type(package_metadata_handler):
    # Call the get method with an unsupported file type
    _set_get_arguments(package_metadata_handler, "lseg_analytics/samples", "sample.txt")
    package_metadata_handler.get()

    # Assert that the status was set to 400 and the error message was returned
    package_metadata_handler.set_status.assert_called_once_with(400)
    package_metadata_handler.finish.assert_called_once_with(
        json.dumps(
            {
                "error": "Unsupported file type 'sample.txt'. Only .json, .py, and .ipynb are allowed."
            }
        )
    )


@patch("lseg_analytics_jupyterlab.src.classes.loggers.logger_main.error")
@patch("lseg_analytics_jupyterlab.src.handlers.packageSamplesHandler.files")
@patch("builtins.open", new_callable=mock_open)
def test_get_internal_server_error(
    mock_open, mock_files, mock_logger_error, package_metadata_handler
):
    # Mock the return value of files().joinpath()
    mock_file_path = Mock()
    mock_file_path.__str__ = Mock(return_value="/fake/path/sample.json")
    mock_file_path.is_file = Mock(return_value=True)
    mock_files.return_value.joinpath.return_value = mock_file_path

    # Mock open to raise an exception
    mock_open.side_effect = Exception("error thrown in test")

    # Call the get method
    _set_get_arguments(
        package_metadata_handler, "lseg_analytics/samples", "sample.json"
    )
    package_metadata_handler.get()

    # Sanity check that the file open method was called as expected
    mock_open.assert_called_once()

    # Check the error was logged
    mock_logger_error.assert_called_once_with(
        "[Server][File Retrieval] Error processing file sample.json: error thrown in test"
    )

    # Assert that the status was set to 500 and the error message was returned
    package_metadata_handler.set_status.assert_called_once_with(500)
    package_metadata_handler.finish.assert_called_once_with(
        json.dumps({"error": "Internal Server Error"})
    )


@patch("lseg_analytics_jupyterlab.src.classes.loggers.logger_main.error")
@patch("lseg_analytics_jupyterlab.src.handlers.packageSamplesHandler.files")
def test_module_not_found(mock_files, mock_logger_error, package_metadata_handler):
    # Mock files to raise ModuleNotFoundError
    mock_files.side_effect = ModuleNotFoundError("Package not found")

    # Call the get method with valid parameters
    _set_get_arguments(
        package_metadata_handler, "lseg_analytics/samples", "sample.json"
    )
    package_metadata_handler.get()

    # Sanity check that the files mock was called as expected
    mock_files.assert_called_once()

    # Check the error was logged
    mock_logger_error.assert_called_once_with(
        "[Server][File Retrieval] Error processing file sample.json: Package not found"
    )

    # Assert that the status was set to 500 and the error message was returned
    package_metadata_handler.set_status.assert_called_once_with(500)
    package_metadata_handler.finish.assert_called_once_with(
        json.dumps({"error": "Internal Server Error"})
    )


def test_error_if_relative_path_to_samples_ends_with_slash(package_metadata_handler):
    _set_get_arguments(
        package_metadata_handler, "should not end/with a slash/", "any.json"
    )
    package_metadata_handler.get()

    # Assert that the status was set to 500 and the error message was returned
    package_metadata_handler.set_status.assert_called_once_with(500)
    package_metadata_handler.finish.assert_called_once_with(
        json.dumps({"error": "Internal Server Error"})
    )


def test_error_if_relative_path_to_samples_does_not_contain_subfolder(
    package_metadata_handler,
):
    _set_get_arguments(
        package_metadata_handler, "should contain a subfolder", "any.json"
    )
    package_metadata_handler.get()

    # Assert that the status was set to 500 and the error message was returned
    package_metadata_handler.set_status.assert_called_once_with(500)
    package_metadata_handler.finish.assert_called_once_with(
        json.dumps({"error": "Internal Server Error"})
    )


def _set_get_arguments(
    handler: PackageSamplesHandler, relative_path_to_samples: str, file_name: str
) -> None:
    """Helper to mock the input values used by the get method."""
    handler.get_argument = MagicMock(
        side_effect=lambda key, default=None: (
            relative_path_to_samples if key == "relative_path_to_samples" else file_name
        )
    )
