"""
Async Python client for the Orb local API.

This package provides an asynchronous HTTP client for interacting with Orb's
local API, including endpoints for datasets and status monitoring.

Based on the official Orb Local Analytics API specification.
"""

from .client import OrbClient
from .exceptions import OrbError, OrbAPIError, OrbConnectionError
from .models import (
    BaseDatasetRecord,
    Scores1mRecord,
    ResponsivenessRecord,
    WebResponsivenessRecord,
    SpeedRecord,
)

__version__ = "0.1.0"
__all__ = [
    "OrbClient",
    "OrbError",
    "OrbAPIError",
    "OrbConnectionError",
    "BaseDatasetRecord",
    "Scores1mRecord",
    "ResponsivenessRecord",
    "WebResponsivenessRecord",
    "SpeedRecord",
]
