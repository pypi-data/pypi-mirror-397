from jupyter_server.utils import url_path_join
from dotenv import find_dotenv, load_dotenv

from lseg_analytics_jupyterlab.src.classes.proxyServer import ProxyServer
from lseg_analytics_jupyterlab.src.classes.sessionService import SessionService
from lseg_analytics_jupyterlab.src.handlers.callBackHandler import CallBackHandler
from lseg_analytics_jupyterlab.src.handlers.healthCheckHandler import HealthCheckHandler
from lseg_analytics_jupyterlab.src.handlers.refreshTokenHandler import (
    RefreshTokenHandler,
)
from lseg_analytics_jupyterlab.src.handlers.syncSessionHandler import (
    SyncSessionHandler,
)
from lseg_analytics_jupyterlab.src.handlers.sdkInstallHandler import SdkInstallHandler
from lseg_analytics_jupyterlab.src.handlers.signinHandler import SignInHandler
from lseg_analytics_jupyterlab.src.handlers.signoutHandler import SignOutHandler
from lseg_analytics_jupyterlab.src.handlers.lsegAuthEnvHandler import LsegAuthEnvHandler
from lseg_analytics_jupyterlab.src.handlers.webSocketHandler import WebSocket
from lseg_analytics_jupyterlab.src.classes.settingsService import SettingsService
from lseg_analytics_jupyterlab.src.handlers.packageMetadataHandler import (
    PackageMetadataHandler,
)
from lseg_analytics_jupyterlab.src.handlers.firstRunHandler import FirstRunHandler
from lseg_analytics_jupyterlab.src.handlers.packageSamplesHandler import (
    PackageSamplesHandler,
)
from lseg_analytics_jupyterlab.src.handlers.serverPackageInfoHandler import (
    ServerPackageInfoHandler,
)
from lseg_analytics_jupyterlab.src.classes.dependencyWatcherManager import (
    DependencyWatcherManager,
)
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
from lseg_analytics_jupyterlab.src.classes.enablementStatusService import (
    EnablementStatusService,
)
import os
import atexit
import signal
from typing import Any, List
import jupyter_core.paths

# Global dependency watcher manager instance
# This global instance is necessary to ensure proper cleanup during shutdown
# via signal handlers and atexit registration, which require access to the
# same manager instance that was used to start watching
dependency_manager = DependencyWatcherManager()
enablement_status_service = EnablementStatusService()


def setup_handlers(web_app: Any):
    """
    Sets up the URL handlers for the web application.

    This function configures the URL routing for the web application by adding
    specific handlers

    Parameters:
    -----------
    web_app : jupyter_server.serverapp.ServerApp
    The Jupyter web application instance.

    Returns:
    --------
    None
    """
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    healthcheck_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/healthcheck"
    )
    signin_route = url_path_join(base_url, web_app.settings["api_prefix"], "/signin")
    signout_route = url_path_join(base_url, web_app.settings["api_prefix"], "/sign_out")
    lseg_auth_env_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/lseg-auth-env"
    )

    callback_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/callback"
    )
    websocket_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/websocket"
    )
    package_metadata_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/package-metadata"
    )
    first_run_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/first-run"
    )
    package_samples_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/package-samples"
    )
    refresh_token_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/refresh-tokens"
    )
    sync_session_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/sync-session"
    )
    install_sdk_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/install-sdk"
    )
    server_package_info_route = url_path_join(
        base_url, web_app.settings["api_prefix"], "/server-package-info"
    )

    # Create a non-running proxy server and pass it to the sign-in and -out handlers
    session_service = SessionService(settings=web_app.settings)

    proxy_server = ProxyServer(
        session_service=session_service,
        settings=web_app.settings,
        enablement_status_service=enablement_status_service,
    )

    handlers: List[Any] = [
        (healthcheck_route, HealthCheckHandler),
        (signin_route, SignInHandler, dict(proxy_server=proxy_server)),
        (
            signout_route,
            SignOutHandler,
            dict(
                proxy_server=proxy_server,
                session_service=session_service,
                enablement_status_service=enablement_status_service,
            ),
        ),
        (callback_route, CallBackHandler, dict(session_service=session_service)),
        (lseg_auth_env_route, LsegAuthEnvHandler),
        (websocket_route, WebSocket),
        (package_metadata_route, PackageMetadataHandler),
        (first_run_route, FirstRunHandler),
        (package_samples_route, PackageSamplesHandler),
        (
            refresh_token_route,
            RefreshTokenHandler,
            dict(session_service=session_service),
        ),
        (
            sync_session_route,
            SyncSessionHandler,
            dict(session_service=session_service, proxy_server=proxy_server),
        ),
        (install_sdk_route, SdkInstallHandler),
        (server_package_info_route, ServerPackageInfoHandler),
    ]

    web_app.add_handlers(host_pattern, handlers)


def _shutdown_handler(signum=None, frame=None):
    """
    Signal handler for graceful shutdown.

    Args:
        signum: Signal number (for signal handlers)
        frame: Current stack frame (for signal handlers)
    """
    logger_main.info(f"[Main] Received shutdown signal: {signum}")
    dependency_manager.stop_watching()

    if signum is not None:
        # If called from signal handler, exit gracefully
        logger_main.info("[Main] Exiting due to signal")
        os._exit(0)


def main(web_app: Any):
    """
    Main entry point for setting up the web application.
    """
    # Use find_dotenv to reliably locate the .env file whether running
    # from source or as an installed package. It searches up from the
    # current working directory.
    dotenv_path = find_dotenv(usecwd=True)

    # Load the .env file if it was found
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path, override=True)
        logger_main.info(f"[Main] Loaded environment variables from: {dotenv_path}")
    else:
        logger_main.warn("[Main] .env file not found. Using default settings.")
    auth_environment = os.getenv("__LSEG_AUTH_ENVIRONMENT", "production")

    settings_service = SettingsService(auth_environment)

    if not settings_service.get_common_setting("proxy_server_host"):
        print("Configuration is empty or invalid.")
        return

    # Set up user settings directory for ProxyHandler
    try:
        jupyter_config_dir = jupyter_core.paths.jupyter_config_dir()
        settings_dir = os.path.join(jupyter_config_dir, "lab", "user-settings")
        web_app.settings["user_settings_dir"] = settings_dir
        logger_main.info(f"[Main] User settings directory: {settings_dir}")
    except Exception as e:
        logger_main.warn(f"[Main] Could not determine user settings directory: {e}")
        web_app.settings["user_settings_dir"] = None

    # Append the environments that you don't need
    outer_settings = {
        k: v
        for k, v in settings_service.config.items()
        if k not in ["staging", "production"]
    }
    env_settings = settings_service.settings
    web_app.settings.update({**outer_settings, **env_settings})

    # Set up shutdown handlers
    # Register shutdown handler with atexit for normal program termination
    atexit.register(dependency_manager.stop_watching)

    # Install signal handlers for SIGTERM and SIGINT
    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)

    logger_main.info("[Main] Dependency watcher shutdown handlers registered")

    setup_handlers(web_app)
