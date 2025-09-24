"""Exception classes for the Orb client."""

from typing import Optional, Any, Dict


class OrbError(Exception):
    """Base exception for all Orb client errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class OrbAPIError(OrbError):
    """Exception raised for API-level errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}


class OrbConnectionError(OrbError):
    """Exception raised for connection-related errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.original_error = original_error
