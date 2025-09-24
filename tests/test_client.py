"""Test the OrbClient class."""

from unittest.mock import AsyncMock, patch

import pytest

from orb import OrbAPIError, OrbClient, OrbConnectionError


class TestOrbClient:
    """Test cases for OrbClient."""

    def test_init_default_params(self):
        """Test client initialization with default parameters."""
        client = OrbClient()
        assert client.base_url == "http://localhost:7080"
        assert client.caller_id == "python-orb-client"
        assert client.timeout.total == 30.0
        assert client.max_retries == 3
        assert client.retry_delay == 1.0

    def test_init_custom_params(self):
        """Test client initialization with custom parameters."""
        client = OrbClient(
            base_url="http://custom.example.com:9090/",
            caller_id="my-custom-client",
            timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
            headers={"X-Custom": "test"},
        )
        assert client.base_url == "http://custom.example.com:9090"
        assert client.caller_id == "my-custom-client"
        assert client.timeout.total == 60.0
        assert client.max_retries == 5
        assert client.retry_delay == 2.0

    def test_build_url(self, client):
        """Test URL building."""
        assert client._build_url("/api/v2/datasets/scores_1m.json") == "http://test.example.com/api/v2/datasets/scores_1m.json"
        assert client._build_url("api/v2/datasets/scores_1m.json") == "http://test.example.com/api/v2/datasets/scores_1m.json"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager usage."""
        async with OrbClient(base_url="http://test.example.com", caller_id="test") as client:
            assert isinstance(client, OrbClient)
            assert client.session is not None
            assert not client.session.closed

    @pytest.mark.asyncio
    async def test_get_dataset_success(self, client):
        """Test successful dataset retrieval."""
        mock_data = [
            {
                "orb_id": "test123",
                "orb_name": "TestOrb",
                "device_name": "test-device",
                "orb_version": "v1.3.0",
                "timestamp": 1640995200000,
                "orb_score": 85.5,
                "responsiveness_score": 90.0,
                "speed_score": 80.0,
                "network_type": 1,
                "country_code": "US"
            },
            {
                "orb_id": "test123",
                "orb_name": "TestOrb",
                "device_name": "test-device",
                "orb_version": "v1.3.0",
                "timestamp": 1640995260000,
                "orb_score": 87.2,
                "responsiveness_score": 92.0,
                "speed_score": 82.0,
                "network_type": 1,
                "country_code": "US"
            }
        ]

        # Mock the aiohttp session with proper initialization
        with patch.object(client, 'session', create=True) as mock_session:
            mock_session.closed = False
            # Create a mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_data
            
            # Configure the context manager behavior
            mock_session.request.return_value.__aenter__.return_value = mock_response

            records = await client.get_dataset("scores_1m")

            assert len(records) == 2
            assert all(isinstance(record, dict) for record in records)
            assert records[0]["orb_score"] == 85.5
            assert records[1]["orb_score"] == 87.2

    @pytest.mark.asyncio
    async def test_session_not_initialized_error(self):
        """Test error when session is not initialized."""
        client = OrbClient()
        # Don't initialize the session (no async context manager)
        
        with pytest.raises(OrbConnectionError) as exc_info:
            await client.get_dataset("scores_1m")
            
        assert "Session not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_convenience_methods_exist(self):
        """Test that all convenience methods exist and are callable."""
        client = OrbClient()
        
        # Test that methods exist (no actual HTTP calls)
        assert hasattr(client, 'get_scores_1m')
        assert hasattr(client, 'get_responsiveness_1s')
        assert hasattr(client, 'get_responsiveness_15s')
        assert hasattr(client, 'get_responsiveness_1m')
        assert hasattr(client, 'get_speed_results')
        assert hasattr(client, 'get_web_responsiveness_results')
        
        # All methods should be callable
        assert callable(client.get_scores_1m)
        assert callable(client.get_responsiveness_1s)
        assert callable(client.get_responsiveness_15s)
        assert callable(client.get_responsiveness_1m)
        assert callable(client.get_speed_results)
        assert callable(client.get_web_responsiveness_results)

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client):
        """Test API error handling."""
        # Mock a 404 error response
        with patch.object(client, 'session', create=True) as mock_session:
            mock_session.closed = False
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.json.return_value = {"error": "Dataset not found", "code": "NOT_FOUND"}
            mock_session.request.return_value.__aenter__.return_value = mock_response

            with pytest.raises(OrbAPIError) as exc_info:
                await client.get_dataset("scores_1m")

            error = exc_info.value
            assert error.status_code == 404
            assert "Dataset not found" in error.message