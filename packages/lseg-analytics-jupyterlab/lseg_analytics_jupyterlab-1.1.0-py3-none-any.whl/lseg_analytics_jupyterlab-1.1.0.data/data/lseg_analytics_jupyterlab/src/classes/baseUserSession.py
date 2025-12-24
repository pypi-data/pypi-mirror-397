from typing import Optional


class BaseUserSession:
    def __init__(
        self,
        id: str,
        user_id: str,
        user_display_name: str,
        access_token: str,
        refresh_token: str,
        expiry_date_time_ms: str,
        diagnostics: Optional[dict] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.user_display_name = user_display_name
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry_date_time_ms = expiry_date_time_ms
        self.diagnostics = diagnostics or {
            "sessionStartTimestampMs": 0,
            "lastTokenRefreshTimestampMs": 0,
            "refreshCount": 0,
        }

    def _get_id(self):
        return self.id
