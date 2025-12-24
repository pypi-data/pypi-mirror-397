from __future__ import annotations


class WaypointError(Exception):
    """Base error for Waypoint SDK."""


class WaypointHTTPError(WaypointError):
    """HTTP-level error."""

    def __init__(self, status_code: int, body: str):
        super().__init__(f"HTTP {status_code}: {body}")
        self.status_code = status_code
        self.body = body


class AnyUnpackError(WaypointError):
    """Raised when an Any message cannot be unpacked into a known type."""

    pass
