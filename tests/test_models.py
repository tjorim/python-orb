"""Test the Pydantic models."""

from datetime import datetime
from typing import Dict, Any
import pytest

from orb.models import Dataset, DatasetDetails, DatasetQueryResponse, Status


class TestDataset:
    """Test cases for Dataset model."""
    
    def test_dataset_minimal(self):
        """Test Dataset with minimal required fields."""
        dataset = Dataset(name="test_dataset")
        assert dataset.name == "test_dataset"
        assert dataset.description is None
        assert dataset.created_at is None
        assert dataset.size is None
        assert dataset.row_count is None
    
    def test_dataset_full(self):
        """Test Dataset with all fields."""
        data = {
            "name": "test_dataset",
            "description": "A test dataset",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
            "schema": {"type": "table", "columns": []},
            "size": 1024,
            "row_count": 100,
        }
        
        dataset = Dataset(**data)
        assert dataset.name == "test_dataset"
        assert dataset.description == "A test dataset"
        assert isinstance(dataset.created_at, datetime)
        assert isinstance(dataset.updated_at, datetime)
        assert dataset.schema_ == {"type": "table", "columns": []}
        assert dataset.size == 1024
        assert dataset.row_count == 100
    
    def test_dataset_extra_fields(self):
        """Test Dataset accepts extra fields."""
        data = {
            "name": "test_dataset",
            "extra_field": "extra_value",
            "another_field": 42,
        }
        
        dataset = Dataset(**data)
        assert dataset.name == "test_dataset"
        assert dataset.extra_field == "extra_value"
        assert dataset.another_field == 42


class TestDatasetDetails:
    """Test cases for DatasetDetails model."""
    
    def test_dataset_details_minimal(self):
        """Test DatasetDetails with minimal required fields."""
        details = DatasetDetails(name="test_dataset")
        assert details.name == "test_dataset"
        assert details.columns is None
        assert details.indexes is None
        assert details.metadata is None
    
    def test_dataset_details_full(self):
        """Test DatasetDetails with all fields."""
        data = {
            "name": "test_dataset",
            "description": "A detailed test dataset",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
            "schema": {"type": "table"},
            "size": 4096,
            "row_count": 500,
            "columns": [
                {"name": "id", "type": "integer", "nullable": False},
                {"name": "name", "type": "string", "nullable": True},
            ],
            "indexes": [
                {"name": "idx_id", "columns": ["id"], "unique": True},
            ],
            "metadata": {
                "source": "csv",
                "encoding": "utf-8",
                "last_refresh": "2024-01-02T12:00:00Z",
            },
        }
        
        details = DatasetDetails(**data)
        assert details.name == "test_dataset"
        assert details.description == "A detailed test dataset"
        assert len(details.columns) == 2
        assert details.columns[0]["name"] == "id"
        assert details.columns[1]["name"] == "name"
        assert len(details.indexes) == 1
        assert details.indexes[0]["name"] == "idx_id"
        assert details.metadata["source"] == "csv"


class TestDatasetQueryResponse:
    """Test cases for DatasetQueryResponse model."""
    
    def test_query_response_minimal(self):
        """Test DatasetQueryResponse with minimal required fields."""
        response = DatasetQueryResponse(
            query="SELECT * FROM test",
            data=[{"id": 1, "name": "test"}],
            columns=["id", "name"],
            row_count=1,
        )
        
        assert response.query == "SELECT * FROM test"
        assert len(response.data) == 1
        assert response.data[0] == {"id": 1, "name": "test"}
        assert response.columns == ["id", "name"]
        assert response.row_count == 1
        assert response.execution_time_ms is None
        assert response.metadata is None
    
    def test_query_response_full(self):
        """Test DatasetQueryResponse with all fields."""
        data = {
            "query": "SELECT id, name FROM users WHERE active = ?",
            "data": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 3, "name": "Charlie"},
            ],
            "columns": ["id", "name"],
            "row_count": 3,
            "execution_time_ms": 142.5,
            "metadata": {
                "cached": False,
                "explain_plan": "SeqScan on users",
                "parameters": [True],
            },
        }
        
        response = DatasetQueryResponse(**data)
        assert response.query == "SELECT id, name FROM users WHERE active = ?"
        assert len(response.data) == 3
        assert response.data[1]["name"] == "Bob"
        assert response.columns == ["id", "name"]
        assert response.row_count == 3
        assert response.execution_time_ms == 142.5
        assert response.metadata["cached"] is False
        assert response.metadata["parameters"] == [True]
    
    def test_query_response_empty_data(self):
        """Test DatasetQueryResponse with empty result set."""
        response = DatasetQueryResponse(
            query="SELECT * FROM empty_table",
            data=[],
            columns=["id", "name"],
            row_count=0,
        )
        
        assert response.query == "SELECT * FROM empty_table"
        assert response.data == []
        assert response.columns == ["id", "name"]
        assert response.row_count == 0


class TestStatus:
    """Test cases for Status model."""
    
    def test_status_minimal(self):
        """Test Status with minimal required fields."""
        status = Status(status="healthy")
        assert status.status == "healthy"
        assert status.version is None
        assert status.uptime is None
        assert status.services is None
        assert status.metrics is None
    
    def test_status_full(self):
        """Test Status with all fields."""
        data = {
            "status": "healthy",
            "version": "1.2.3",
            "uptime": "7 days, 14:30:25",
            "timestamp": "2024-01-01T12:00:00Z",
            "services": {
                "database": "running",
                "cache": "running",
                "queue": "degraded",
            },
            "metrics": {
                "memory_usage_mb": 2048,
                "cpu_usage_percent": 35.7,
                "disk_usage_gb": 15.2,
                "active_connections": 42,
                "requests_per_second": "150.3",
            },
            "health": {
                "database_latency_ms": 5.2,
                "last_backup": "2024-01-01T06:00:00Z",
                "errors_last_hour": 0,
            },
        }
        
        status = Status(**data)
        assert status.status == "healthy"
        assert status.version == "1.2.3"
        assert status.uptime == "7 days, 14:30:25"
        assert isinstance(status.timestamp, datetime)
        assert status.services["database"] == "running"
        assert status.services["queue"] == "degraded"
        assert status.metrics["memory_usage_mb"] == 2048
        assert status.metrics["cpu_usage_percent"] == 35.7
        assert status.metrics["requests_per_second"] == "150.3"
        assert status.health["database_latency_ms"] == 5.2
        assert status.health["errors_last_hour"] == 0
    
    def test_status_extra_fields(self):
        """Test Status accepts extra fields."""
        data = {
            "status": "healthy",
            "custom_field": "custom_value",
            "build_info": {
                "commit": "abc123",
                "branch": "main",
            },
        }
        
        status = Status(**data)
        assert status.status == "healthy"
        assert status.custom_field == "custom_value"
        assert status.build_info["commit"] == "abc123"