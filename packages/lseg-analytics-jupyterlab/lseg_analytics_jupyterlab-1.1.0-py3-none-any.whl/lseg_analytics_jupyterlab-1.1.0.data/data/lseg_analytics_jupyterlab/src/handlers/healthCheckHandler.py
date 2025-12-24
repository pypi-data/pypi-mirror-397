from jupyter_server.base.handlers import APIHandler
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main

from lseg_analytics_jupyterlab.src.utils.serverUtils import create_response


class HealthCheckHandler(APIHandler):
    """
    A simple request handler class to perform health checks on the server.

    This handler is useful for debugging or for client-side applications to verify if the server is running.
    """

    def get(self):
        try:
            self.set_status(200)
            logger_main.info("Success" + "I am healthy!")

            self.finish(create_response("success", "I am healthy!"))
        except Exception as e:
            self.set_status(500)
            logger_main.error("An unexpected error occurred" + str(e))

            self.finish(
                create_response("error", "An unexpected error occurred", str(e))
            )
