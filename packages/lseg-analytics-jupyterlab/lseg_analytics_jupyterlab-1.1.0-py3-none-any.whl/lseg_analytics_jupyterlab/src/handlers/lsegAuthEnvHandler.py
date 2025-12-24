# lsegAuthEnvHandler.py
# ---------------------
# This handler exposes a REST API endpoint to retrieve runtime environment variables
# for the JupyterLab extension. It is used by the frontend to access whitelisted
# environment variables (e.g., "__LSEG_AUTH_ENVIRONMENT") at runtime.
# The handler includes a security whitelist to prevent access to unauthorized environment variables.

from jupyter_server.base.handlers import APIHandler
from lseg_analytics_jupyterlab.src.utils.serverUtils import create_response
import os
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main


class LsegAuthEnvHandler(APIHandler):
    """
    API Handler to return whitelisted environment variables for the JupyterLab extension.

    GET /api/lseg-analytics-jupyterlab/lseg-auth-env?var=<env_var_name>
    - Accepts a query parameter 'var' specifying the environment variable name
    - Returns: JSON response with the environment variable value or None if not set
    - Only whitelisted environment variables are allowed for security
    """

    # Whitelist of allowed environment variables for security
    ALLOWED_ENV_VARS = {
        "__LSEG_AUTH_ENVIRONMENT",
        "__LSEG_COPILOT_URL_ENDPOINT",
        # Add other environment variables here as needed
        # "COPILOT_ENDPOINT_URL",  # Example for future use
    }

    def get(self):
        """
        Handle GET requests to fetch a specified environment variable.
        """
        try:
            env_var_name = self.get_argument("var", default=None)

            if not env_var_name:
                logger_main.error(
                    "[LsegAuthEnvHandler] No environment variable name provided"
                )
                self.finish(
                    create_response(
                        "error",
                        "Environment variable name is required",
                        "Missing 'var' query parameter",
                    )
                )
                return

            if env_var_name not in self.ALLOWED_ENV_VARS:
                logger_main.error(
                    f"[LsegAuthEnvHandler] Unauthorized environment variable requested: {env_var_name}"
                )
                self.finish(
                    create_response(
                        "error",
                        f"Environment variable '{env_var_name}' is not allowed",
                        "Unauthorized variable",
                    )
                )
                return

            env_value = os.environ.get(env_var_name)
            logger_main.debug(
                f"[LsegAuthEnvHandler] Returning {env_var_name}: {env_value}"
            )
            # Return the value in the data field, not the message field
            # Use a descriptive message instead
            message = f"Environment variable '{env_var_name}' retrieved successfully"
            self.finish(create_response("success", message, env_value))

        except Exception as e:
            logger_main.error(
                f"[LsegAuthEnvHandler] Failed to get environment variable: {e}"
            )
            self.finish(
                create_response("error", "Failed to get environment variable", str(e))
            )
