"""Test the OrbClient class."""

from datetime import datetime
from unittest.mock import AsyncMock, patch
import pytest
import httpx
import respx

from orb import OrbClient, OrbAPIError, OrbConnectionError
from orb.models import Dataset, DatasetDetails, DatasetQueryResponse, Status


class TestOrbClient:
    """Test cases for OrbClient."""
    
    def test_init_default_params(self):
        """Test client initialization with default parameters."""
        client = OrbClient()
        assert client.base_url == "http://localhost:8080"
        assert client.timeout == 30.0
        assert client.max_retries == 3
        assert client.retry_delay == 1.0
    
    def test_init_custom_params(self):
        """Test client initialization with custom parameters."""
        client = OrbClient(
            base_url="http://custom.example.com:9090/",
            timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
            headers={"X-Custom": "test"},
        )
        assert client.base_url == "http://custom.example.com:9090"
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.retry_delay == 2.0
    
    def test_build_url(self, client):
        """Test URL building."""
        assert client._build_url("/api/status") == "http://test.example.com/api/status"
        assert client._build_url("api/status") == "http://test.example.com/api/status"
        assert client._build_url("api/datasets/test") == "http://test.example.com/api/datasets/test"
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_respx):
        """Test async context manager usage."""
        async with OrbClient(base_url="http://test.example.com") as client:
            assert isinstance(client, OrbClient)
    
    @pytest.mark.asyncio
    async def test_get_status_success(self, client, mock_respx):
        """Test successful status retrieval."""
        mock_data = {
            "status": "healthy",
            "version": "1.0.0",
            "uptime": "5 days",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {"database": "running", "api": "running"},
            "metrics": {"memory_usage": 1024, "cpu_usage": 50.5},
        }
        
        mock_respx.get("http://test.example.com/api/status").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        
        status = await client.get_status()
        
        assert isinstance(status, Status)
        assert status.status == "healthy"
        assert status.version == "1.0.0"
        assert status.uptime == "5 days"
        assert status.services == {"database": "running", "api": "running"}
        assert status.metrics == {"memory_usage": 1024, "cpu_usage": 50.5}
    
    @pytest.mark.asyncio
    async def test_list_datasets_success(self, client, mock_respx):
        """Test successful dataset listing."""
        mock_data = [
            {
                "name": "dataset1",
                "description": "Test dataset 1",
                "created_at": "2024-01-01T00:00:00Z",
                "size": 1024,
                "row_count": 100,
            },
            {
                "name": "dataset2", 
                "description": "Test dataset 2",
                "created_at": "2024-01-02T00:00:00Z",
                "size": 2048,
                "row_count": 200,
            },
        ]
        
        mock_respx.get("http://test.example.com/api/datasets").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        
        datasets = await client.list_datasets()
        
        assert len(datasets) == 2
        assert all(isinstance(d, Dataset) for d in datasets)
        assert datasets[0].name == "dataset1"
        assert datasets[0].description == "Test dataset 1"
        assert datasets[0].size == 1024
        assert datasets[0].row_count == 100
        assert datasets[1].name == "dataset2"
    
    @pytest.mark.asyncio
    async def test_list_datasets_wrapped_response(self, client, mock_respx):
        """Test dataset listing with wrapped response format."""
        mock_data = {
            "datasets": [
                {
                    "name": "dataset1",
                    "description": "Test dataset 1",
                    "size": 1024,
                }
            ]
        }
        
        mock_respx.get("http://test.example.com/api/datasets").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        
        datasets = await client.list_datasets()
        
        assert len(datasets) == 1
        assert datasets[0].name == "dataset1"
    
    @pytest.mark.asyncio
    async def test_get_dataset_success(self, client, mock_respx):
        """Test successful dataset details retrieval."""
        mock_data = {
            "name": "test_dataset",
            "description": "A test dataset",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
            "schema": {"type": "table", "columns": []},
            "size": 4096,
            "row_count": 500,
            "columns": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "indexes": [{"name": "idx_id", "columns": ["id"]}],
            "metadata": {"source": "test"},
        }
        
        mock_respx.get("http://test.example.com/api/datasets/test_dataset").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        
        dataset = await client.get_dataset("test_dataset")
        
        assert isinstance(dataset, DatasetDetails)
        assert dataset.name == "test_dataset"
        assert dataset.description == "A test dataset"
        assert dataset.size == 4096
        assert dataset.row_count == 500
        assert len(dataset.columns) == 2
        assert len(dataset.indexes) == 1
        assert dataset.metadata == {"source": "test"}
    
    @pytest.mark.asyncio
    async def test_query_dataset_success(self, client, mock_respx):
        """Test successful dataset query."""
        mock_data = {
            "query": "SELECT * FROM test_table LIMIT 10",
            "data": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
            "columns": ["id", "name"],
            "row_count": 2,
            "execution_time_ms": 150.5,
            "metadata": {"cached": False},
        }
        
        mock_respx.post("http://test.example.com/api/datasets/test_dataset/query").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        
        result = await client.query_dataset(
            "test_dataset",
            "SELECT * FROM test_table LIMIT 10",
            limit=10,
            offset=0,
            parameters={"param1": "value1"},
        )
        
        assert isinstance(result, DatasetQueryResponse)
        assert result.query == "SELECT * FROM test_table LIMIT 10"
        assert len(result.data) == 2
        assert result.columns == ["id", "name"]
        assert result.row_count == 2
        assert result.execution_time_ms == 150.5
        assert result.metadata == {"cached": False}
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, client, mock_respx):
        """Test API error handling."""
        mock_respx.get("http://test.example.com/api/status").mock(
            return_value=httpx.Response(
                500, 
                json={"error": "Internal server error", "code": "INTERNAL_ERROR"}
            )
        )
        
        with pytest.raises(OrbAPIError) as exc_info:
            await client.get_status()
        
        error = exc_info.value
        assert error.status_code == 500
        assert "Internal server error" in error.message
        assert error.response_data["error"] == "Internal server error"
        assert error.response_data["code"] == "INTERNAL_ERROR"
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, client, mock_respx):
        """Test connection error handling."""
        mock_respx.get("http://test.example.com/api/status").mock(
            side_effect=httpx.NetworkError("Connection failed")
        )
        
        with pytest.raises(OrbConnectionError) as exc_info:
            await client.get_status()
        
        error = exc_info.value
        assert "Network error" in error.message
        assert isinstance(error.original_error, httpx.NetworkError)
    
    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, client, mock_respx):
        """Test timeout error handling."""
        mock_respx.get("http://test.example.com/api/status").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )
        
        with pytest.raises(OrbConnectionError) as exc_info:
            await client.get_status()
        
        error = exc_info.value
        assert "Timeout" in error.message
        assert isinstance(error.original_error, httpx.TimeoutException)
    
    @pytest.mark.asyncio
    async def test_invalid_json_response(self, client, mock_respx):
        """Test handling of invalid JSON responses."""
        mock_respx.get("http://test.example.com/api/status").mock(
            return_value=httpx.Response(200, text="invalid json")
        )
        
        with pytest.raises(OrbAPIError) as exc_info:
            await client.get_status()
        
        error = exc_info.value
        assert "Failed to parse JSON response" in error.message
        assert "invalid json" in error.response_data["raw_response"]
    
    @pytest.mark.asyncio
    async def test_list_datasets_unexpected_format(self, client, mock_respx):
        """Test handling of unexpected response format in list_datasets."""
        mock_respx.get("http://test.example.com/api/datasets").mock(
            return_value=httpx.Response(200, json={"unexpected": "format"})
        )
        
        with pytest.raises(OrbAPIError) as exc_info:
            await client.list_datasets()
        
        error = exc_info.value
        assert "Unexpected response format" in error.message