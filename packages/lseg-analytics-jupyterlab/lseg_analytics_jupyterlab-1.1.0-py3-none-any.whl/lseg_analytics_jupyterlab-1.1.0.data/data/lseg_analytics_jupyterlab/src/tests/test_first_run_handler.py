# type: ignore
import unittest
from unittest import mock
from lseg_analytics_jupyterlab.src.handlers.firstRunHandler import FirstRunHandler
from tornado.web import Application
from unittest.mock import Mock
import json


class TestFirstRunHandler(unittest.TestCase):
    def setUp(self):
        mock_request = Mock()
        application = Application([("/first-run", FirstRunHandler)])

        self.handler = FirstRunHandler(application, mock_request)

    @mock.patch("lseg_analytics_jupyterlab.src.handlers.firstRunHandler.Path")
    def test_check_first_run_when_sentinel_exists(self, mock_path):
        # Setup mock path to have sentinel file exist
        mock_path_instance = mock.MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.parent = mock_path_instance
        mock_sentinel = mock.Mock()
        mock_path_instance.__truediv__.return_value = mock_sentinel
        mock_sentinel.exists.return_value = True

        # Call method to test
        self.handler.check_first_run()

        # Assertions
        self.assertTrue(self.handler.first_run)
        mock_sentinel.unlink.assert_called_once()

    @mock.patch("lseg_analytics_jupyterlab.src.handlers.firstRunHandler.Path")
    def test_check_first_run_when_sentinel_does_not_exist(self, mock_path):
        # Setup mock path to have sentinel file not exist
        mock_path_instance = mock.MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.parent = mock_path_instance
        mock_sentinel = mock.Mock()
        mock_path_instance.__truediv__.return_value = mock_sentinel
        mock_sentinel.exists.return_value = False

        # Call method to test
        self.handler.check_first_run()

        # Assertions
        self.assertFalse(self.handler.first_run)
        mock_sentinel.unlink.assert_not_called()

    @mock.patch("lseg_analytics_jupyterlab.src.handlers.firstRunHandler.Path")
    @mock.patch("lseg_analytics_jupyterlab.src.handlers.firstRunHandler.logger_main")
    def test_check_first_run_when_sentinel_delete_fails(self, mock_logger, mock_path):
        # Setup mock path to have sentinel file exist but fail on delete
        mock_path_instance = mock.MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.parent = mock_path_instance
        mock_sentinel = mock.Mock()
        mock_path_instance.__truediv__.return_value = mock_sentinel
        mock_sentinel.exists.return_value = True
        mock_sentinel.unlink.side_effect = Exception("Permission denied")

        # Call method to test
        self.handler.check_first_run()

        # Assertions
        self.assertTrue(self.handler.first_run)
        mock_sentinel.unlink.assert_called_once()
        mock_logger.error.assert_called_with(
            "Failed to remove sentinel file: Permission denied"
        )

    @mock.patch.object(FirstRunHandler, "check_first_run")
    def test_initialize_successful(self, mock_check_first_run):
        # Call method to test
        self.handler.initialize()

        # Verify check_first_run was called
        mock_check_first_run.assert_called_once()

    @mock.patch.object(FirstRunHandler, "check_first_run")
    @mock.patch("lseg_analytics_jupyterlab.src.handlers.firstRunHandler.logger_main")
    def test_initialize_with_exception(self, mock_logger, mock_check_first_run):
        # Setup check_first_run to raise exception
        mock_check_first_run.side_effect = Exception("Initialization error")

        # Call method to test
        self.handler.initialize()

        # Assertions
        self.assertFalse(self.handler.first_run)
        mock_logger.error.assert_called_with(
            "Error initializing FirstRunHandler: Initialization error"
        )

    def test_get_successful_first_run_true(self):
        # Setup
        self.handler.first_run = True
        self.handler.finish = mock.Mock()

        # Call method to test
        self.handler.get()

        # Assertions
        expected_response = json.dumps({"first_run": True})
        self.handler.finish.assert_called_once_with(expected_response)

    def test_get_successful_first_run_false(self):
        # Setup
        self.handler.first_run = False
        self.handler.finish = mock.Mock()

        # Call method to test
        self.handler.get()

        # Assertions
        expected_response = json.dumps({"first_run": False})
        self.handler.finish.assert_called_once_with(expected_response)

    @mock.patch("lseg_analytics_jupyterlab.src.handlers.firstRunHandler.json.dumps")
    @mock.patch("lseg_analytics_jupyterlab.src.handlers.firstRunHandler.logger_main")
    def test_get_with_exception(self, mock_logger, mock_dumps):
        # Setup
        exception_msg = "JSON encoding error"
        # First dumps call raises exception, second one (in error handler) succeeds
        mock_dumps.side_effect = [
            Exception(exception_msg),
            '{"error": "Internal server error", "detail": "JSON encoding error"}',
        ]
        self.handler.set_status = mock.Mock()
        self.handler.finish = mock.Mock()

        # Call the method
        self.handler.get()

        # Verify error is logged
        mock_logger.error.assert_called_with(
            f"Unexpected error in FirstRunHandler: {exception_msg}"
        )

        # Verify status code is set to 500
        self.handler.set_status.assert_called_once_with(500)

        # Verify finish is called with the error response from the second dumps call
        self.handler.finish.assert_called_once_with(
            '{"error": "Internal server error", "detail": "JSON encoding error"}'
        )
