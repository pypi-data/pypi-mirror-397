"""
Constants for WebSocket message types.
"""


# Message types for WebSocket communication
class MessageType:
    """WebSocket message types."""

    AUTH = "AUTHENTICATION"
    LOGGER = "LOGGER"
    DEPENDENCY_CHANGED = "DEPENDENCY_CHANGED"
    TOKEN_UPDATED = "TOKEN_UPDATED"
    ENABLEMENT_STATUS = "ENABLEMENT_STATUS"
