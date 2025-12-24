# type: ignore
import json
import pytest
import importlib.metadata
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from lseg_analytics_jupyterlab.src.handlers.serverPackageInfoHandler import (
    ServerPackageInfoHandler,
)
from tornado.web import Application
from tornado.httputil import HTTPServerRequest


# Fixture to create a Tornado application with the ServerPackageInfoHandler
@pytest.fixture
def app():
    return Application(
        [
            (
                r"/api/lseg-analytics-jupyterlab/server-package-info",
                ServerPackageInfoHandler,
            )
        ]
    )


# Fixture to create a mock HTTP request
@pytest.fixture
def http_request():
    request = HTTPServerRequest(
        uri="/api/lseg-analytics-jupyterlab/server-package-info?package=lseg_analytics"
    )
    request.connection = Mock()  # Mock the connection attribute
    return request


# Fixture to create an instance of PackageMetadataHandler with the mock application and request
@pytest.fixture
def server_package_info_handler(app, http_request):
    handler = ServerPackageInfoHandler(app, http_request)
    handler.finish = MagicMock()  # Mock the finish method
    handler.set_status = MagicMock()  # Mock the set_status method
    return handler


# Test case for the get method of ServerPackageInfoHandler
@patch("importlib.metadata.Distribution")
def test_get(
    mock_distribution,
    server_package_info_handler,
):
    # Mock distribution object
    mock_dist = MagicMock()
    mock_dist.locate_file.return_value = Path("/fake/path")
    mock_dist.version = "2.1.0b1"
    mock_distribution.from_name.return_value = mock_dist

    # Call the get method
    server_package_info_handler.get()

    expected_location = str(Path("/fake/path").parent)

    # Expected combined metadata
    expected_response = {
        "status": "success",
        "message": "Server package info fetched successfully",
        "data": {
            "name": "lseg_analytics",
            "version": "2.1.0b1",
            "location": expected_location,
        },
        "error": None,
    }

    # Assert that the finish method was called with the expected response
    server_package_info_handler.finish.assert_called_once_with(
        json.dumps(expected_response)
    )


# Test case for missing package parameter
def test_get_missing_package(server_package_info_handler):
    # Override the get_argument method to return None
    server_package_info_handler.get_argument = MagicMock(return_value=None)

    # Call the get method
    server_package_info_handler.get()

    # Expected response
    expected_response = {
        "status": "error",
        "message": "Missing 'package' query parameter",
        "data": None,
        "error": None,
    }

    # Assert that the status was set to 400
    server_package_info_handler.set_status.assert_called_once_with(400)
    # Assert that the finish method was called with the expected response
    server_package_info_handler.finish.assert_called_once_with(
        json.dumps(expected_response)
    )


# Test case for package not found
@patch("importlib.metadata.Distribution")
def test_get_package_not_found(mock_distribution, server_package_info_handler):
    # Mock distribution to raise PackageNotFoundError
    mock_distribution.from_name.side_effect = importlib.metadata.PackageNotFoundError

    # Call the get method
    server_package_info_handler.get()

    # Expected response
    expected_response = {
        "status": "error",
        "message": "Package 'lseg_analytics' not found",
        "data": None,
        "error": None,
    }

    # Assert that the status was set to 404
    server_package_info_handler.set_status.assert_called_once_with(404)
    # Assert that the finish method was called with the expected response
    server_package_info_handler.finish.assert_called_once_with(
        json.dumps(expected_response)
    )


# Test case for handling error in distributon locate_file
@patch("importlib.metadata.Distribution")
def test_distribution_error(mock_distribution, server_package_info_handler):
    # Mock locate_file to raise an exception
    mock_found_dist = MagicMock()
    mock_found_dist.locate_file.side_effect = Exception("Test exception in locate_file")

    # mock the patched distribution to return the "found" distribution
    mock_distribution.from_name.return_value = mock_found_dist

    # Call the get method
    server_package_info_handler.get()

    # Expected response
    expected_response = {
        "status": "error",
        "message": "Internal Server Error",
        "data": None,
        "error": "Test exception in locate_file",
    }

    # Assert that the status was set to 500
    server_package_info_handler.set_status.assert_called_once_with(500)
    # Assert that the finish method was called with the expected response
    server_package_info_handler.finish.assert_called_once_with(
        json.dumps(expected_response)
    )
