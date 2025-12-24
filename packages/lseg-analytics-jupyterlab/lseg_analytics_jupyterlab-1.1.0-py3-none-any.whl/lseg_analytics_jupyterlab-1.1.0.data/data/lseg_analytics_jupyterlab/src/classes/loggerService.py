import json
import traceback
from typing import Any, Dict


class LogLevel:
    def __init__(self, prefix: str, fore_colour: str) -> None:
        self.prefix = prefix
        self.fore_colour = fore_colour


class LoggerService:
    DEFAULT = "\033[0m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[36m"

    def __init__(self, name: str) -> None:
        self.logger_name = name

        self.DEBUG_LOG = LogLevel("DEBUG", self.BLUE)
        self.INFO_LOG = LogLevel("INFO", self.GREEN)
        self.WARN_LOG = LogLevel("WARN", self.YELLOW)
        self.ERROR_LOG = LogLevel("ERROR", self.RED)

    def _safe_stringify(self, obj: Any) -> str:
        """
        Safely stringify an object for logging

        Args:
            obj: The object to stringify

        Returns:
            str: A string representation of the object
        """
        if isinstance(obj, str):
            return obj

        if isinstance(obj, Exception):
            return f"Error: {str(obj)}\nStack: {traceback.format_exc()}"

        try:
            return json.dumps(
                obj,
                indent=2,
                default=lambda o: f"<<Non-serializable object of type {type(o).__name__}>>",
            )
        except Exception as e:
            return f"[Object could not be stringified: {str(e)}]"

    def _log_message(self, message: Any, log_level: LogLevel) -> None:
        # Convert message to string if it's not already
        if not isinstance(message, str):
            message = self._safe_stringify(message)

        log_str = (
            log_level.fore_colour
            + "{server} - [{func}] ".format(
                server=self.logger_name,
                func=log_level.prefix,
            )
            + self.DEFAULT
            + message
        )
        print(log_str)

        log_message: Dict[str, Any] = {
            "message_type": "LOGGER",
            "message": {
                "log_level": log_level.prefix,
                "content": log_str,
                "channel": self.logger_name,
            },
        }

        # Dynamic import prevents circular dependency: WebSocket imports loggerService,
        # so importing WebSocket at module level would create a circular import.
        # This affects both production and test environments.
        try:
            from lseg_analytics_jupyterlab.src.handlers.webSocketHandler import (
                WebSocket,
            )

            WebSocket.send_message_to_client(json.dumps(log_message))
        except ImportError:
            # Handle case where WebSocket is not available
            pass

    def debug(self, message: Any) -> None:
        self._log_message(message, self.DEBUG_LOG)

    def info(self, message: Any) -> None:
        self._log_message(message, self.INFO_LOG)

    def error(self, message: Any) -> None:
        self._log_message(message, self.ERROR_LOG)

    def warn(self, message: Any) -> None:
        self._log_message(message, self.WARN_LOG)
