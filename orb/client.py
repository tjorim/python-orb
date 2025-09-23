"""Module providing the OrbClient class for interacting with the Orb local API."""

import logging
from types import TracebackType
from typing import Any, Dict, List, Optional, Type
from urllib.parse import urljoin

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .exceptions import OrbAPIError, OrbConnectionError

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger: logging.Logger = logging.getLogger(__name__)


class OrbClient:
    """A Python wrapper for the Orb local API, handling dataset requests.

    Attributes:
        base_url (str): The base URL for the Orb Local API.
        caller_id (str): Unique caller ID for tracking requests.
        timeout (float): Request timeout in seconds.
        max_retries (int): Maximum number of retry attempts.
        retry_delay (float): Base delay between retries in seconds.

    """

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
        """Initialize the Orb client.

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
        self._owns_client = True  # Track ownership

        default_headers = {
            "User-Agent": (
                "python-orb/0.1.0 "
                "(https://github.com/tjorim/python-orb; python-orb)"
            ),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if headers:
            default_headers.update(headers)

        self._headers = default_headers
        # Initialize client immediately for backward compatibility
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self._headers,
        )
        logger.info("OrbClient instance created")

    async def __aenter__(self) -> "OrbClient":
        """Initialize the httpx client when entering the async context."""
        if self._client and not self._client.is_closed:
            logger.debug("Using existing httpx client")
        elif not self._client or self._client.is_closed:
            logger.debug("Creating new internal httpx client")
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self._headers,
            )
        return self

    async def __aexit__(
        self, 
        exc_type: Optional[Type[BaseException]], 
        exc: Optional[BaseException], 
        tb: Optional[TracebackType]
    ) -> None:
        """Close the httpx client when exiting the async context."""
        if self._client:
            if self._client.is_closed:
                logger.debug("Client is already closed, skipping closure")
            elif not self._owns_client:
                logger.debug("Client is externally provided; not closing it")
            else:
                logger.debug("Closing httpx client")
                try:
                    await self._client.aclose()
                except Exception as e:
                    logger.error("Error while closing httpx client: %s", e)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
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
        """Make an HTTP request with retry logic.

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
        logger.info("Starting request to endpoint: %s", endpoint)
        if self._client is None or self._client.is_closed:
            logger.error(
                "Client not initialized or closed. "
                "Use 'async with' context manager to initialize the client."
            )
            raise OrbConnectionError(
                "Client not initialized or closed. "
                "Use 'async with' context manager."
            )

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

                logger.error(
                    "Request failed with status code: %s, response: %s", 
                    response.status_code, 
                    error_data
                )
                raise OrbAPIError(
                    message=(
                        f"HTTP {response.status_code}: "
                        f"{error_data.get('error', 'Unknown error')}"
                    ),
                    status_code=response.status_code,
                    response_data=error_data,
                )

            # Parse JSON response
            try:
                json_data = response.json()
                if not json_data:
                    logger.warning("Empty response received")
                return json_data
            except Exception as e:
                logger.error("Failed to parse JSON response: %s", e)
                raise OrbAPIError(
                    message=f"Failed to parse JSON response: {e}",
                    status_code=response.status_code,
                    response_data={"raw_response": response.text},
                ) from e

        except httpx.NetworkError as e:
            logger.error("Network error connecting to %s: %s", url, e)
            raise OrbConnectionError(
                message=f"Network error connecting to {url}: {e}",
                original_error=e,
            ) from e
        except httpx.TimeoutException as e:
            logger.error("Timeout connecting to %s: %s", url, e)
            raise OrbConnectionError(
                message=f"Timeout connecting to {url}: {e}",
                original_error=e,
            ) from e
        except httpx.HTTPError as e:
            logger.error("HTTP error: %s", e)
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
        """Get dataset records from the Orb Local API.

        Args:
            name: Dataset name (e.g., 'scores_1m', 'responsiveness_1s', 
                  'speed_results', 'web_responsiveness_results')
            format: Response format ('json' or 'jsonl') (default: 'json')
            caller_id: Override the default caller ID for this request

        Returns:
            List[Dict[str, Any]]: List of dataset records as dictionaries

        Example:
            async with OrbClient() as client:
                scores = await client.get_dataset('scores_1m')
                if scores:
                    print(f"Retrieved {len(scores)} score records")

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
    async def get_scores_1m(
        self, caller_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get 1-minute scores dataset.

        Args:
            caller_id: Override the default caller ID for this request

        Returns:
            List[Dict[str, Any]]: List of 1-minute score records

        Example:
            async with OrbClient() as client:
                scores = await client.get_scores_1m()

        """
        return await self.get_dataset("scores_1m", caller_id=caller_id)

    async def get_responsiveness_1s(
        self, caller_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get 1-second responsiveness dataset.

        Args:
            caller_id: Override the default caller ID for this request

        Returns:
            List[Dict[str, Any]]: List of 1-second responsiveness records

        Example:
            async with OrbClient() as client:
                responsiveness = await client.get_responsiveness_1s()

        """
        return await self.get_dataset("responsiveness_1s", caller_id=caller_id)

    async def get_responsiveness_15s(
        self, caller_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get 15-second responsiveness dataset.

        Args:
            caller_id: Override the default caller ID for this request

        Returns:
            List[Dict[str, Any]]: List of 15-second responsiveness records

        Example:
            async with OrbClient() as client:
                responsiveness = await client.get_responsiveness_15s()

        """
        return await self.get_dataset("responsiveness_15s", caller_id=caller_id)

    async def get_responsiveness_1m(
        self, caller_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get 1-minute responsiveness dataset.

        Args:
            caller_id: Override the default caller ID for this request

        Returns:
            List[Dict[str, Any]]: List of 1-minute responsiveness records

        Example:
            async with OrbClient() as client:
                responsiveness = await client.get_responsiveness_1m()

        """
        return await self.get_dataset("responsiveness_1m", caller_id=caller_id)

    async def get_speed_results(
        self, caller_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get speed test results dataset.

        Args:
            caller_id: Override the default caller ID for this request

        Returns:
            List[Dict[str, Any]]: List of speed test result records

        Example:
            async with OrbClient() as client:
                speed_results = await client.get_speed_results()

        """
        return await self.get_dataset("speed_results", caller_id=caller_id)

    async def get_web_responsiveness_results(
        self, caller_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get web responsiveness results dataset.

        Args:
            caller_id: Override the default caller ID for this request

        Returns:
            List[Dict[str, Any]]: List of web responsiveness result records

        Example:
            async with OrbClient() as client:
                web_results = await client.get_web_responsiveness_results()

        """
        return await self.get_dataset("web_responsiveness_results", caller_id=caller_id)
