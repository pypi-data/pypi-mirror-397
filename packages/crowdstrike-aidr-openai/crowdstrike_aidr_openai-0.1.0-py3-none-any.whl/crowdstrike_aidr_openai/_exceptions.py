from __future__ import annotations

__all__ = ("CrowdStrikeError", "CrowdStrikeAIDRBlockedError")


class CrowdStrikeError(Exception):
    pass


class CrowdStrikeAIDRBlockedError(CrowdStrikeError):
    """Raised when CrowdStrike AIDR returns a blocked response."""

    def __init__(self, message: str = "CrowdStrike AIDR returned a blocked response.") -> None:
        super().__init__(message)
