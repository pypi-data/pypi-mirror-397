from typing import Dict
import json
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
from jupyter_server.base.handlers import APIHandler
from pathlib import Path


class FirstRunHandler(APIHandler):
    """Exposes the first run status of the application to the client"""

    first_run: bool

    def check_first_run(self):
        """
        Checks if this is the first run of the application by looking for a sentinel file.
        """
        pkg_dir = Path(__file__).parent
        sentinel = pkg_dir / "RESET_ON_INSTALL"

        if sentinel.exists():
            self.first_run = True
            try:
                sentinel.unlink()
            except Exception as e:
                logger_main.error(f"Failed to remove sentinel file: {str(e)}")

    def initialize(self):
        # Set a default value before attempting initialization
        self.first_run = False

        try:
            self.check_first_run()
        except Exception as e:
            logger_main.error(f"Error initializing FirstRunHandler: {str(e)}")

    def get(self):
        try:
            response_data: Dict[str, bool] = {"first_run": self.first_run}
            self.finish(json.dumps(response_data))
        except Exception as e:
            logger_main.error(f"Unexpected error in FirstRunHandler: {str(e)}")
            self.set_status(500)
            error_response: Dict[str, str] = {
                "error": "Internal server error",
                "detail": str(e),
            }
            self.finish(json.dumps(error_response))
