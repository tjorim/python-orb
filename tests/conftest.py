"""Test configuration and fixtures."""

from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest

from orb import OrbClient


@pytest.fixture
def client():
    """Create an OrbClient instance for testing."""
    return OrbClient(base_url="http://test.example.com", caller_id="test-client")


@pytest.fixture
def mock_response():
    """Create a mock aiohttp response."""
    def _create_response(status=200, json_data=None, text_data=None):
        response = Mock(spec=aiohttp.ClientResponse)
        response.status = status
        response.json = AsyncMock(return_value=json_data or {})
        response.text = AsyncMock(return_value=text_data or "")
        return response
    return _create_response


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = Mock(spec=aiohttp.ClientSession)
    session.closed = False
    session.close = AsyncMock()
    return session
