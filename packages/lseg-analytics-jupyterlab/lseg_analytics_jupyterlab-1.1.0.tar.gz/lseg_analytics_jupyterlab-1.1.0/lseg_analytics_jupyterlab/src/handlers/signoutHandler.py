from jupyter_server.base.handlers import APIHandler
from lseg_analytics_jupyterlab.src.classes.proxyServer import ProxyServer
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
from lseg_analytics_jupyterlab.src.classes.enablementStatusService import (
    EnablementStatusService,
)

from lseg_analytics_jupyterlab.src.utils.serverUtils import create_response


class SignOutHandler(APIHandler):
    _proxy_server: ProxyServer
    _session_service: SessionService
    _enablement_status_service: EnablementStatusService

    def initialize(
        self,
        proxy_server: ProxyServer,
        session_service: SessionService,
        enablement_status_service: EnablementStatusService,
    ) -> None:
        assert (
            proxy_server is not None
            and session_service is not None
            and enablement_status_service is not None
        )
        self._proxy_server = proxy_server
        self._session_service = session_service
        self._enablement_status_service = enablement_status_service

    def get(self) -> None:
        try:
            self.handlelogout()
            logger_main.info("Signed out successfully")
            self.finish(create_response("success", "Signed out successfully"))
            self._proxy_server.stop()

        except Exception as e:
            logger_main.error("An unexpected error occured" + str(e))
            self.finish(create_response("error", "An unexpected error occured", str(e)))

    def handlelogout(self) -> None:
        self._enablement_status_service.clear_status()
        self._session_service.delete_session()
