from typing import Optional
from lseg_analytics_jupyterlab.src.classes.loggers import logger_proxy


class EnablementStatusService:
    """Stores enablement status for the current JupyterLab session."""

    def __init__(self) -> None:
        self._cached_has_access: Optional[bool] = None

    def update_status(self, has_lfa_access: bool) -> None:
        """Persist the latest enablement status broadcast from the client."""
        logger_proxy.debug(
            f"[EnablementStatusService] Updating enablement status to {has_lfa_access}"
        )
        self._cached_has_access = bool(has_lfa_access)

    def user_has_lfa_access(self) -> bool:
        """Return the cached LFA entitlement status for the current session."""
        if self._cached_has_access is None:
            logger_proxy.debug(
                "[EnablementStatusService] No cached enablement status; denying by default"
            )
            return False
        return bool(self._cached_has_access)

    def clear_status(self) -> None:
        """Clear the cached enablement status."""
        logger_proxy.debug("[EnablementStatusService] Clearing enablement status cache")
        self._cached_has_access = None

    def reset(self) -> None:
        """Clear cached status - exposed for testing."""
        self._cached_has_access = None
