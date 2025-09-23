"""Async HTTP client for the Orb local API.

This implementation is based on the official Orb Local Analytics API specification:
https://orb.net/docs/deploy-and-configure/local-analytics
https://orb.net/docs/deploy-and-configure/datasets-configuration#local-api
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


class OrbClient:
    """Async HTTP client for Orb Local API."""
    
    # API endpoint paths based on official Orb API specification
    _DATASET_ENDPOINT = "/api/v2/datasets/{name}.{format}"
    
    def __init__(
        self,
        base_url: str = "http://localhost:7080",
        caller_id: str = "python-orb-client",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize the Orb client.
        
        Args:
            base_url: Base URL for the Orb API (default: http://localhost:7080)
            caller_id: Unique caller ID for tracking requests (default: python-orb-client)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Base delay between retries in seconds (default: 1.0)
            headers: Additional headers to include in requests
        """
        self.base_url = base_url.rstrip("/")
        self.caller_id = caller_id
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
    
    async def get_dataset(
        self, 
        name: str, 
        format: str = "json",
        caller_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get dataset records from the Orb Local API.
        
        Args:
            name: Dataset name (e.g., 'scores_1m', 'responsiveness_1s', 'speed_results', 'web_responsiveness_results')
            format: Response format ('json' or 'jsonl') (default: 'json')
            caller_id: Override the default caller ID for this request
            
        Returns:
            List of dataset records as dictionaries
        """
        endpoint = self._DATASET_ENDPOINT.format(name=name, format=format)
        params = {"id": caller_id or self.caller_id}
        
        data = await self._request("GET", endpoint, params=params)
        
        # The API returns a JSON array directly
        if not isinstance(data, list):
            raise OrbAPIError(
                message=f"Unexpected response format for dataset {name}",
                response_data=data,
            )
        
        return data
    
    # Convenience methods for specific datasets
    async def get_scores_1m(self, caller_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get 1-minute scores dataset."""
        return await self.get_dataset("scores_1m", caller_id=caller_id)
    
    async def get_responsiveness_1s(self, caller_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get 1-second responsiveness dataset."""
        return await self.get_dataset("responsiveness_1s", caller_id=caller_id)
    
    async def get_responsiveness_15s(self, caller_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get 15-second responsiveness dataset."""
        return await self.get_dataset("responsiveness_15s", caller_id=caller_id)
    
    async def get_responsiveness_1m(self, caller_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get 1-minute responsiveness dataset."""
        return await self.get_dataset("responsiveness_1m", caller_id=caller_id)
    
    async def get_speed_results(self, caller_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get speed test results dataset."""
        return await self.get_dataset("speed_results", caller_id=caller_id)
    
    async def get_web_responsiveness_results(self, caller_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get web responsiveness results dataset."""
        return await self.get_dataset("web_responsiveness_results", caller_id=caller_id)