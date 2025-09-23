"""Pydantic models for Orb API responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class Dataset(BaseModel):
    """Model for dataset information."""
    
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(..., description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    schema_: Optional[Dict[str, Any]] = Field(None, alias="schema", description="Dataset schema")
    size: Optional[int] = Field(None, description="Dataset size in bytes")
    row_count: Optional[int] = Field(None, description="Number of rows")


class DatasetDetails(BaseModel):
    """Model for detailed dataset information."""
    
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(..., description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    schema_: Optional[Dict[str, Any]] = Field(None, alias="schema", description="Dataset schema")
    size: Optional[int] = Field(None, description="Dataset size in bytes")
    row_count: Optional[int] = Field(None, description="Number of rows")
    columns: Optional[List[Dict[str, Any]]] = Field(None, description="Column information")
    indexes: Optional[List[Dict[str, Any]]] = Field(None, description="Index information")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DatasetQueryResponse(BaseModel):
    """Model for dataset query response."""
    
    model_config = ConfigDict(extra="allow")
    
    query: str = Field(..., description="The executed query")
    data: List[Dict[str, Any]] = Field(..., description="Query result data")
    columns: List[str] = Field(..., description="Column names")
    row_count: int = Field(..., description="Number of rows returned")
    execution_time_ms: Optional[float] = Field(None, description="Query execution time in milliseconds")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional query metadata")


class Status(BaseModel):
    """Model for Orb system status."""
    
    model_config = ConfigDict(extra="allow")
    
    status: str = Field(..., description="Overall system status")
    version: Optional[str] = Field(None, description="Orb version")
    uptime: Optional[str] = Field(None, description="System uptime")
    timestamp: Optional[datetime] = Field(None, description="Status timestamp")
    services: Optional[Dict[str, Any]] = Field(None, description="Service status details")
    metrics: Optional[Dict[str, Union[int, float, str]]] = Field(None, description="System metrics")
    health: Optional[Dict[str, Any]] = Field(None, description="Health check results")