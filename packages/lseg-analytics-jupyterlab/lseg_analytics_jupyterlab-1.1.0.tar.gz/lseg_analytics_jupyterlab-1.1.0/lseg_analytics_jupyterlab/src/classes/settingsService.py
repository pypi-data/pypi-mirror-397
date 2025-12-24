from typing import Dict, Any, Optional, Union
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main


class SettingsService:
    """
    A service class to manage and provide configuration settings based on the environment.
    This class abstracts the environment-specific settings and provides a unified interface
    to access these settings dynamically.
    """

    config: Dict[str, Any]
    environment: str
    settings: Dict[str, Any]

    def __init__(self, environment: str) -> None:
        self.config = {
            "extension_version": "0.1.0",
            "proxy_server_host": "http://127.0.0.1",
            "port_range": {"start": 60100, "end": 60110},
            "api_prefix": "/api/lseg-analytics-jupyterlab/",
            "staging": {
                "CLIENT_ID": "afd238de-256f-4956-9e39-b31bab87b837",
                "BASE_URL": "https://login.stage.ciam.refinitiv.com",
                "SDK_API": "https://ppe.api.analytics.lseg.com",
            },
            "production": {
                "CLIENT_ID": "78bb1b02-b708-4560-90a9-96cf1814b881",
                "BASE_URL": "https://login.ciam.refinitiv.com",
                "SDK_API": "https://api.analytics.lseg.com",
            },
        }

        requested_env = (environment or "").strip().lower()

        # Determine the effective environment: 'staging' if requested, otherwise 'production'.
        self.environment = "staging" if requested_env == "staging" else "production"
        self.settings = self._get_settings()

        # Log a warning if an unexpected value was provided.
        if requested_env not in ("", "staging", "production"):
            logger_main.warn(
                f"[SettingsService] Unknown Auth Environment='{requested_env}', defaulting to 'production'."
            )

        # Log the requested environment vs. the one that was actually used.
        logger_main.debug(
            f"[SettingsService] Auth env requested='{requested_env or '<unset>'}', effective='{self.environment}'"
        )

    def _get_settings(self) -> Dict[str, Any]:
        # This is now safe because self.environment is guaranteed to be 'staging' or 'production'.
        return self.config.get(self.environment, {})

    def get_setting(self, key: str) -> Optional[str]:
        return self.settings.get(key)

    def get_common_setting(self, key: str) -> Optional[Union[str, Dict[str, Any]]]:
        return self.config.get(key)
