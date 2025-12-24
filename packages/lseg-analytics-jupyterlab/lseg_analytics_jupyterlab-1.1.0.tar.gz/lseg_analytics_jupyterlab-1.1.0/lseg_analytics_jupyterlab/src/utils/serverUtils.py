import json
from typing import Any, Dict, Optional, Union
import requests


ERROR_INVALID_STATE = "Invalid state."
ERROR_UNEXPECTED = "unexpected_error"


def create_response(
    status: str,
    message: str,
    additional_data: Optional[Union[str, Dict[str, Any]]] = None,
):
    return json.dumps(
        {
            "status": status,
            "message": message,
            "data": additional_data if status == "success" else None,
            "error": additional_data if status == "error" else None,
        }
    )


def ensure_auth_settings(settings: Dict[str, Any]) -> None:
    """
    Checks that all of the settings required by sign in, sign out, and token refresh
    are present in the settings dictionary. Raises RuntimeError if any are missing
    or could not be fetched.

    CLIENT_ID and BASE_URL are expected to be present already as they are hard-coded.

    The AUTH_URL and TOKEN_URL are fetched from the OpenID configuration endpoint.
    This method checks if they are already in the settings, and fetches them if not.
    """

    if "BASE_URL" not in settings:
        raise RuntimeError("[Internal error] BASE_URL is missing from settings")

    if "CLIENT_ID" not in settings:
        raise RuntimeError("[Internal error] CLIENT_ID is missing from settings")

    if "AUTH_URL" not in settings or "TOKEN_URL" not in settings:
        try:
            openid_config = fetch_openid_configuration(settings["BASE_URL"])
            settings["AUTH_URL"] = openid_config["authorization_endpoint"]
            settings["TOKEN_URL"] = openid_config["token_endpoint"]
        except Exception as e:
            raise RuntimeError(f"Error fetching OpenID configuration: {str(e)}")


def fetch_openid_configuration(base_url: str):
    """
    Fetches the OpenID configuration from the given base URL.
    Should only be called by ensure_auth_settings.
    """
    openid_config_url = f"{base_url}/.well-known/openid-configuration"
    response = requests.get(openid_config_url, timeout=(10, 30))
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError("Failed to fetch OpenID configuration")
