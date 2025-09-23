# python-orb

Async Python client for the Orb local API — query datasets, manage configurations, and fetch analytics from Orb locally.

## Features

- **Async/await support**: Built with `httpx` for modern async Python applications
- **Typed models**: Uses Pydantic for robust data validation and type safety
- **Comprehensive API coverage**: Supports datasets (list, details, query) and status endpoints
- **Retry logic**: Built-in exponential backoff retry for robust error handling
- **Clear exceptions**: Structured exception hierarchy for different error types
- **JSON handling**: Automatic JSON serialization/deserialization
- **Context manager support**: Automatic resource cleanup

## Installation

```bash
pip install python-orb
```

For development:

```bash
pip install python-orb[dev]
```

## Quick Start

```python
import asyncio
from orb import OrbClient

async def main():
    async with OrbClient(base_url="http://localhost:8080") as client:
        # Get system status
        status = await client.get_status()
        print(f"Orb status: {status.status}")
        
        # List datasets
        datasets = await client.list_datasets()
        for dataset in datasets:
            print(f"Dataset: {dataset.name}")
        
        # Query a dataset
        if datasets:
            result = await client.query_dataset(
                datasets[0].name,
                "SELECT * FROM table LIMIT 10"
            )
            print(f"Query returned {result.row_count} rows")

asyncio.run(main())
```

## API Reference

### OrbClient

The main client class for interacting with the Orb API.

#### Constructor

```python
OrbClient(
    base_url: str = "http://localhost:8080",
    timeout: float = 30.0,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    headers: Optional[Dict[str, str]] = None
)
```

**Parameters:**
- `base_url`: Base URL for the Orb API (default: "http://localhost:8080")
- `timeout`: Request timeout in seconds (default: 30.0)
- `max_retries`: Maximum number of retry attempts (default: 3)
- `retry_delay`: Base delay between retries in seconds (default: 1.0)
- `headers`: Additional headers to include in requests

#### Methods

##### `async get_status() -> Status`

Get the current status of the Orb system.

**Returns:** `Status` object with system information

**Example:**
```python
status = await client.get_status()
print(f"Status: {status.status}")
print(f"Version: {status.version}")
print(f"Uptime: {status.uptime}")
```

##### `async list_datasets() -> List[Dataset]`

List all available datasets.

**Returns:** List of `Dataset` objects

**Example:**
```python
datasets = await client.list_datasets()
for dataset in datasets:
    print(f"{dataset.name}: {dataset.row_count} rows")
```

##### `async get_dataset(name: str) -> DatasetDetails`

Get detailed information about a specific dataset.

**Parameters:**
- `name`: Dataset name

**Returns:** `DatasetDetails` object with comprehensive dataset information

**Example:**
```python
details = await client.get_dataset("my_dataset")
print(f"Description: {details.description}")
print(f"Columns: {len(details.columns)}")
```

##### `async query_dataset(name: str, query: str, limit: Optional[int] = None, offset: Optional[int] = None, parameters: Optional[Dict[str, Any]] = None) -> DatasetQueryResponse`

Execute a query against a dataset.

**Parameters:**
- `name`: Dataset name
- `query`: SQL query to execute
- `limit`: Maximum number of rows to return
- `offset`: Number of rows to skip
- `parameters`: Query parameters for parameterized queries

**Returns:** `DatasetQueryResponse` with query results

**Example:**
```python
result = await client.query_dataset(
    "sales_data",
    "SELECT * FROM sales WHERE amount > ? LIMIT ?",
    limit=100,
    parameters=[1000, 100]
)

print(f"Found {result.row_count} rows")
for row in result.data:
    print(row)
```

### Data Models

#### Dataset

Basic dataset information.

**Fields:**
- `name: str` - Dataset name (required)
- `description: Optional[str]` - Dataset description
- `created_at: Optional[datetime]` - Creation timestamp
- `updated_at: Optional[datetime]` - Last update timestamp
- `schema_: Optional[Dict[str, Any]]` - Dataset schema
- `size: Optional[int]` - Dataset size in bytes
- `row_count: Optional[int]` - Number of rows

#### DatasetDetails

Detailed dataset information extending Dataset.

**Additional Fields:**
- `columns: Optional[List[Dict[str, Any]]]` - Column information
- `indexes: Optional[List[Dict[str, Any]]]` - Index information
- `metadata: Optional[Dict[str, Any]]` - Additional metadata

#### DatasetQueryResponse

Query execution results.

**Fields:**
- `query: str` - The executed query (required)
- `data: List[Dict[str, Any]]` - Query result data (required)
- `columns: List[str]` - Column names (required)
- `row_count: int` - Number of rows returned (required)
- `execution_time_ms: Optional[float]` - Query execution time in milliseconds
- `metadata: Optional[Dict[str, Any]]` - Additional query metadata

#### Status

System status information.

**Fields:**
- `status: str` - Overall system status (required)
- `version: Optional[str]` - Orb version
- `uptime: Optional[str]` - System uptime
- `timestamp: Optional[datetime]` - Status timestamp
- `services: Optional[Dict[str, Any]]` - Service status details
- `metrics: Optional[Dict[str, Union[int, float, str]]]` - System metrics
- `health: Optional[Dict[str, Any]]` - Health check results

### Exceptions

#### OrbError

Base exception for all Orb client errors.

**Attributes:**
- `message: str` - Error message
- `details: Dict[str, Any]` - Additional error details

#### OrbAPIError

Exception raised for API-level errors. Inherits from `OrbError`.

**Additional Attributes:**
- `status_code: Optional[int]` - HTTP status code
- `response_data: Dict[str, Any]` - Response data from the API

#### OrbConnectionError

Exception raised for connection-related errors. Inherits from `OrbError`.

**Additional Attributes:**
- `original_error: Optional[Exception]` - The original underlying error

## Error Handling

The client provides structured exception handling:

```python
from orb import OrbClient, OrbAPIError, OrbConnectionError

async with OrbClient() as client:
    try:
        datasets = await client.list_datasets()
    except OrbAPIError as e:
        print(f"API Error: {e.message}")
        print(f"Status Code: {e.status_code}")
        print(f"Response: {e.response_data}")
    except OrbConnectionError as e:
        print(f"Connection Error: {e.message}")
        print(f"Original Error: {e.original_error}")
    except OrbError as e:
        print(f"General Orb Error: {e.message}")
```

## Configuration

### Environment Variables

You can configure the client using environment variables:

```bash
export ORB_BASE_URL="http://localhost:8080"
export ORB_TIMEOUT="60"
export ORB_MAX_RETRIES="5"
```

### Custom Headers

Add custom headers for authentication or other purposes:

```python
client = OrbClient(
    headers={
        "Authorization": "Bearer your-token",
        "X-Custom-Header": "value"
    }
)
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=orb
```

### Code Quality

```bash
# Format code
ruff format

# Lint code
ruff check

# Type checking
mypy orb/
```

## Examples

See the `examples/` directory for more comprehensive usage examples:

- `examples/basic_usage.py` - Basic client usage
- `examples/error_handling.py` - Error handling patterns
- `examples/batch_queries.py` - Batch query operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## References

- [Orb Local Analytics Documentation](https://orb.net/docs/deploy-and-configure/local-analytics)
- [Orb Datasets Documentation](https://orb.net/docs/deploy-and-configure/datasets)
