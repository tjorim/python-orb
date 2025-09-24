"""Test configuration and fixtures."""

import pytest

from orb import OrbClient


@pytest.fixture
def client():
    """Create an OrbClient instance for testing."""
    return OrbClient(base_url="http://test.example.com", caller_id="test-client")
