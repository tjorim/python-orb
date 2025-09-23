"""Test configuration and fixtures."""

import pytest
import respx

from orb import OrbClient


@pytest.fixture
def client():
    """Create an OrbClient instance for testing."""
    return OrbClient(base_url="http://test.example.com", caller_id="test-client")


@pytest.fixture
def mock_respx():
    """Mock HTTP responses using respx."""
    with respx.mock() as respx_mock:
        yield respx_mock
