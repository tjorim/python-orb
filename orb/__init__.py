"""
Async Python client for the Orb local API.

This package provides an asynchronous HTTP client for interacting with Orb's 
local API, including endpoints for datasets and status monitoring.
"""

from .client import OrbClient
from .exceptions import OrbError, OrbAPIError, OrbConnectionError
from .models import Dataset, DatasetDetails, DatasetQueryResponse, Status

__version__ = "0.1.0"
__all__ = [
    "OrbClient",
    "OrbError",
    "OrbAPIError", 
    "OrbConnectionError",
    "Dataset",
    "DatasetDetails",
    "DatasetQueryResponse",
    "Status",
]