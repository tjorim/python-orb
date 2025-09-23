"""Async HTTP client for the Orb local API.

Note: This implementation is based on common REST API patterns. 
The actual API endpoints and request/response formats should be 
validated against the official Orb Local Analytics documentation:
https://orb.net/docs/deploy-and-configure/local-analytics
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .exceptions import OrbAPIError, OrbConnectionError
from .models import Dataset, DatasetDetails, DatasetQueryResponse, Status


class OrbClient:
    """Async HTTP client for Orb local API."""
    
    # API endpoint paths - update these based on actual Orb API specification
    _STATUS_ENDPOINT = "/api/status"
    _DATASETS_ENDPOINT = "/api/datasets"
    _DATASET_DETAIL_ENDPOINT = "/api/datasets/{name}"
    _DATASET_QUERY_ENDPOINT = "/api/datasets/{name}/query"
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize the Orb client.
        
        Args:
            base_url: Base URL for the Orb API (default: http://localhost:8080)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Base delay between retries in seconds (default: 1.0)
            headers: Additional headers to include in requests
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        default_headers = {
            "User-Agent": "python-orb/0.1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if headers:
            default_headers.update(headers)
            
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers=default_headers,
        )
    
    async def __aenter__(self) -> "OrbClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL for an endpoint."""
        return urljoin(f"{self.base_url}/", endpoint.lstrip("/"))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException)),
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON data for request body
            
        Returns:
            Response data as dictionary
            
        Raises:
            OrbConnectionError: For connection-related errors
            OrbAPIError: For API-level errors
        """
        url = self._build_url(endpoint)
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
            )
            
            # Check for HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"error": response.text}
                
                raise OrbAPIError(
                    message=f"HTTP {response.status_code}: {error_data.get('error', 'Unknown error')}",
                    status_code=response.status_code,
                    response_data=error_data,
                )
            
            # Parse JSON response
            try:
                return response.json()
            except Exception as e:
                raise OrbAPIError(
                    message=f"Failed to parse JSON response: {e}",
                    status_code=response.status_code,
                    response_data={"raw_response": response.text},
                ) from e
                
        except httpx.NetworkError as e:
            raise OrbConnectionError(
                message=f"Network error connecting to {url}: {e}",
                original_error=e,
            ) from e
        except httpx.TimeoutException as e:
            raise OrbConnectionError(
                message=f"Timeout connecting to {url}: {e}",
                original_error=e,
            ) from e
        except httpx.HTTPError as e:
            raise OrbConnectionError(
                message=f"HTTP error: {e}",
                original_error=e,
            ) from e
    
    async def get_status(self) -> Status:
        """
        Get the current status of the Orb system.
        
        Returns:
            Status object with system information
        """
        data = await self._request("GET", self._STATUS_ENDPOINT)
        return Status(**data)
    
    async def list_datasets(self) -> List[Dataset]:
        """
        List all available datasets.
        
        Returns:
            List of Dataset objects
        """
        data = await self._request("GET", self._DATASETS_ENDPOINT)
        
        # Handle different response formats
        if isinstance(data, list):
            datasets = data
        elif isinstance(data, dict) and "datasets" in data:
            datasets = data["datasets"]
        else:
            raise OrbAPIError(
                message="Unexpected response format for list_datasets",
                response_data=data,
            )
        
        return [Dataset(**dataset) for dataset in datasets]
    
    async def get_dataset(self, name: str) -> DatasetDetails:
        """
        Get detailed information about a specific dataset.
        
        Args:
            name: Dataset name
            
        Returns:
            DatasetDetails object with comprehensive dataset information
        """
        endpoint = self._DATASET_DETAIL_ENDPOINT.format(name=name)
        data = await self._request("GET", endpoint)
        return DatasetDetails(**data)
    
    async def query_dataset(
        self,
        name: str,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> DatasetQueryResponse:
        """
        Execute a query against a dataset.
        
        Args:
            name: Dataset name
            query: SQL query to execute
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            parameters: Query parameters for parameterized queries
            
        Returns:
            DatasetQueryResponse with query results
        """
        json_data = {
            "query": query,
        }
        
        if limit is not None:
            json_data["limit"] = limit
        if offset is not None:
            json_data["offset"] = offset
        if parameters:
            json_data["parameters"] = parameters
        
        endpoint = self._DATASET_QUERY_ENDPOINT.format(name=name)
        data = await self._request("POST", endpoint, json_data=json_data)
        return DatasetQueryResponse(**data)