"""Test the OrbClient class."""

from unittest.mock import AsyncMock, patch
import pytest
import httpx
import respx

from orb import OrbClient, OrbAPIError, OrbConnectionError


class TestOrbClient:
    """Test cases for OrbClient."""

    def test_init_default_params(self):
        """Test client initialization with default parameters."""
        client = OrbClient()
        assert client.base_url == "http://localhost:7080"
        assert client.caller_id == "python-orb-client"
        assert client.timeout == 30.0
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
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.retry_delay == 2.0

    def test_build_url(self, client):
        """Test URL building."""
        assert (
            client._build_url("/api/v2/datasets/scores_1m.json")
            == "http://test.example.com/api/v2/datasets/scores_1m.json"
        )
        assert (
            client._build_url("api/v2/datasets/scores_1m.json")
            == "http://test.example.com/api/v2/datasets/scores_1m.json"
        )

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_respx):
        """Test async context manager usage."""
        async with OrbClient(
            base_url="http://test.example.com", caller_id="test"
        ) as client:
            assert isinstance(client, OrbClient)

    @pytest.mark.asyncio
    async def test_get_dataset_success(self, client, mock_respx):
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
                "country_code": "US",
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
                "country_code": "US",
            },
        ]

        mock_respx.get("http://test.example.com/api/v2/datasets/scores_1m.json").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        records = await client.get_dataset("scores_1m")

        assert len(records) == 2
        assert all(isinstance(record, dict) for record in records)
        assert records[0]["orb_score"] == 85.5
        assert records[1]["orb_score"] == 87.2

    @pytest.mark.asyncio
    async def test_get_scores_1m(self, client, mock_respx):
        """Test convenience method for scores_1m."""
        mock_data = [
            {
                "orb_id": "test123",
                "orb_name": "TestOrb",
                "device_name": "test-device",
                "orb_version": "v1.3.0",
                "timestamp": 1640995200000,
                "orb_score": 75.0,
                "responsiveness_score": 80.0,
                "speed_score": 70.0,
            }
        ]

        mock_respx.get("http://test.example.com/api/v2/datasets/scores_1m.json").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        records = await client.get_scores_1m()

        assert len(records) == 1
        assert records[0]["orb_score"] == 75.0

    @pytest.mark.asyncio
    async def test_get_responsiveness_1s(self, client, mock_respx):
        """Test convenience method for responsiveness_1s."""
        mock_data = [
            {
                "orb_id": "test123",
                "orb_name": "TestOrb",
                "device_name": "test-device",
                "orb_version": "v1.3.0",
                "timestamp": 1640995200000,
                "lag_avg_us": 25000,
                "latency_avg_us": 15000,
                "packet_loss_pct": 0.5,
            }
        ]

        mock_respx.get(
            "http://test.example.com/api/v2/datasets/responsiveness_1s.json"
        ).mock(return_value=httpx.Response(200, json=mock_data))

        records = await client.get_responsiveness_1s()

        assert len(records) == 1
        assert records[0]["lag_avg_us"] == 25000

    @pytest.mark.asyncio
    async def test_get_speed_results(self, client, mock_respx):
        """Test convenience method for speed_results."""
        mock_data = [
            {
                "orb_id": "test123",
                "orb_name": "TestOrb",
                "device_name": "test-device",
                "orb_version": "v1.3.0",
                "timestamp": 1640995200000,
                "download_kbps": 100000,
                "upload_kbps": 50000,
                "speed_test_server": "https://speed.cloudflare.com/",
            }
        ]

        mock_respx.get(
            "http://test.example.com/api/v2/datasets/speed_results.json"
        ).mock(return_value=httpx.Response(200, json=mock_data))

        records = await client.get_speed_results()

        assert len(records) == 1
        assert records[0]["download_kbps"] == 100000
        assert records[0]["upload_kbps"] == 50000

    @pytest.mark.asyncio
    async def test_get_web_responsiveness_results(self, client, mock_respx):
        """Test convenience method for web_responsiveness_results."""
        mock_data = [
            {
                "orb_id": "test123",
                "orb_name": "TestOrb",
                "device_name": "test-device",
                "orb_version": "v1.3.0",
                "timestamp": 1640995200000,
                "ttfb_us": 150000,
                "dns_us": 25000,
                "web_url": "https://www.google.com/",
            }
        ]

        mock_respx.get(
            "http://test.example.com/api/v2/datasets/web_responsiveness_results.json"
        ).mock(return_value=httpx.Response(200, json=mock_data))

        records = await client.get_web_responsiveness_results()

        assert len(records) == 1
        assert records[0]["ttfb_us"] == 150000
        assert records[0]["dns_us"] == 25000

    @pytest.mark.asyncio
    async def test_get_dataset_with_caller_id(self, client, mock_respx):
        """Test dataset retrieval with custom caller ID."""
        mock_data = [{"orb_id": "test123", "timestamp": 1640995200000}]

        mock_respx.get("http://test.example.com/api/v2/datasets/scores_1m.json").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        records = await client.get_dataset("scores_1m", caller_id="custom-caller")

        # Verify the request was made with the custom caller ID
        request = mock_respx.calls[0].request
        assert "id=custom-caller" in str(request.url)

    @pytest.mark.asyncio
    async def test_get_dataset_jsonl_format(self, client, mock_respx):
        """Test dataset retrieval with JSONL format."""
        mock_data = [{"orb_id": "test123", "timestamp": 1640995200000}]

        mock_respx.get("http://test.example.com/api/v2/datasets/scores_1m.jsonl").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        records = await client.get_dataset("scores_1m", format="jsonl")

        assert len(records) == 1
        assert records[0]["orb_id"] == "test123"

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client, mock_respx):
        """Test API error handling."""
        mock_respx.get("http://test.example.com/api/v2/datasets/scores_1m.json").mock(
            return_value=httpx.Response(
                404, json={"error": "Dataset not found", "code": "NOT_FOUND"}
            )
        )

        with pytest.raises(OrbAPIError) as exc_info:
            await client.get_dataset("scores_1m")

        error = exc_info.value
        assert error.status_code == 404
        assert "Dataset not found" in error.message
        assert error.response_data["error"] == "Dataset not found"
        assert error.response_data["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, client, mock_respx):
        """Test connection error handling."""
        mock_respx.get("http://test.example.com/api/v2/datasets/scores_1m.json").mock(
            side_effect=httpx.NetworkError("Connection failed")
        )

        with pytest.raises(OrbConnectionError) as exc_info:
            await client.get_dataset("scores_1m")

        error = exc_info.value
        assert "Network error" in error.message
        assert isinstance(error.original_error, httpx.NetworkError)

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, client, mock_respx):
        """Test timeout error handling."""
        mock_respx.get("http://test.example.com/api/v2/datasets/scores_1m.json").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )

        with pytest.raises(OrbConnectionError) as exc_info:
            await client.get_dataset("scores_1m")

        error = exc_info.value
        assert "Timeout" in error.message
        assert isinstance(error.original_error, httpx.TimeoutException)

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, client, mock_respx):
        """Test handling of invalid JSON responses."""
        mock_respx.get("http://test.example.com/api/v2/datasets/scores_1m.json").mock(
            return_value=httpx.Response(200, text="invalid json")
        )

        with pytest.raises(OrbAPIError) as exc_info:
            await client.get_dataset("scores_1m")

        error = exc_info.value
        assert "Failed to parse JSON response" in error.message
        assert "invalid json" in error.response_data["raw_response"]

    @pytest.mark.asyncio
    async def test_non_array_response(self, client, mock_respx):
        """Test handling of non-array responses."""
        mock_respx.get("http://test.example.com/api/v2/datasets/scores_1m.json").mock(
            return_value=httpx.Response(200, json={"error": "not an array"})
        )

        with pytest.raises(OrbAPIError) as exc_info:
            await client.get_dataset("scores_1m")

        error = exc_info.value
        assert "Unexpected response format" in error.message
