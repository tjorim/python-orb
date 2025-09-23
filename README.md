# python-orb

Async Python client for the Orb Local API — access datasets from your Orb devices locally.

This implementation is based on the official Orb Local Analytics API specification and provides typed access to Orb datasets including scores, responsiveness, speed tests, and web responsiveness measurements.

## Features

- **Async/await support**: Built with `httpx` for modern async Python applications
- **Typed models**: Uses Pydantic for robust data validation and type safety
- **Official API support**: Implements the official Orb Local API specification
- **Dataset access**: Supports all Orb datasets (scores, responsiveness, speed, web responsiveness)
- **Caller ID tracking**: Proper caller ID management for efficient polling
- **Multiple formats**: Supports both JSON and JSONL response formats
- **Retry logic**: Built-in exponential backoff retry for robust error handling
- **Clear exceptions**: Structured exception hierarchy for different error types
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
    async with OrbClient(base_url="http://localhost:7080", caller_id="my-app") as client:
        # Get latest scores
        scores = await client.get_scores_1m()
        if scores:
            latest = scores[-1]
            print(f"Orb Score: {latest['orb_score']}")
        
        # Get responsiveness data
        responsiveness = await client.get_responsiveness_1s()
        if responsiveness:
            latest = responsiveness[-1]
            print(f"Lag: {latest['lag_avg_us']} μs")
        
        # Get speed test results
        speed_tests = await client.get_speed_results()
        if speed_tests:
            latest = speed_tests[-1]
            print(f"Download: {latest['download_kbps']} Kbps")

asyncio.run(main())
```

## API Reference

### OrbClient

The main client class for interacting with the Orb API.

#### Constructor

```python
OrbClient(
    base_url: str = "http://localhost:7080",
    caller_id: str = "python-orb-client",
    timeout: float = 30.0,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    headers: Optional[Dict[str, str]] = None
)
```

**Parameters:**
- `base_url`: Base URL for the Orb Local API (default: "http://localhost:7080")
- `caller_id`: Unique caller ID for tracking requests (default: "python-orb-client")
- `timeout`: Request timeout in seconds (default: 30.0)
- `max_retries`: Maximum number of retry attempts (default: 3)
- `retry_delay`: Base delay between retries in seconds (default: 1.0)
- `headers`: Additional headers to include in requests

#### Methods

##### `async get_dataset(name: str, format: str = "json", caller_id: Optional[str] = None) -> List[Dict[str, Any]]`

Get dataset records from the Orb Local API.

**Parameters:**
- `name`: Dataset name (`scores_1m`, `responsiveness_1s`, `responsiveness_15s`, `responsiveness_1m`, `speed_results`, `web_responsiveness_results`)
- `format`: Response format (`json` or `jsonl`) (default: `json`)
- `caller_id`: Override the default caller ID for this request

**Returns:** List of dataset records as dictionaries

**Example:**
```python
records = await client.get_dataset("scores_1m")
for record in records:
    print(f"Orb Score: {record['orb_score']}")
```

##### Convenience Methods

The client provides convenient methods for each dataset type:

```python
# Get 1-minute scores data
scores = await client.get_scores_1m()

# Get responsiveness data at different intervals
resp_1s = await client.get_responsiveness_1s()
resp_15s = await client.get_responsiveness_15s()  
resp_1m = await client.get_responsiveness_1m()

# Get speed test results
speed_tests = await client.get_speed_results()

# Get web responsiveness results
web_resp = await client.get_web_responsiveness_results()
```

### Dataset Records

The client provides typed Pydantic models for each dataset type:

#### BaseDatasetRecord

Base model with common fields for all dataset records.

**Common Fields:**
- `orb_id: str` - Orb Sensor identifier
- `orb_name: str` - Current Orb friendly name
- `device_name: str` - Hostname or device name
- `orb_version: str` - Semantic version of collecting Orb
- `timestamp: int` - Timestamp in epoch milliseconds
- `network_type: Optional[int]` - Network interface type (0=unknown, 1=wifi, 2=ethernet, 3=other)
- `country_code: Optional[str]` - Geocoded 2-digit ISO country code
- `public_ip: Optional[str]` - Public IP address
- `latitude/longitude: Optional[float]` - Orb location coordinates

#### Scores1mRecord

1-minute aggregated scores dataset.

**Key Fields:**
- `orb_score: Optional[float]` - Overall Orb Score (0-100)
- `responsiveness_score: Optional[float]` - Responsiveness component (0-100)
- `speed_score: Optional[float]` - Speed component (0-100)
- `lag_avg_us: Optional[float]` - Average lag in microseconds
- `download_avg_kbps/upload_avg_kbps: Optional[int]` - Speed measurements

#### ResponsivenessRecord

Responsiveness measurements (1s, 15s, 1m intervals).

**Key Fields:**
- `lag_avg_us: Optional[int]` - Average lag in microseconds
- `latency_avg_us: Optional[int]` - Average latency in microseconds  
- `packet_loss_pct: Optional[float]` - Packet loss percentage
- `jitter_avg_us: Optional[int]` - Average jitter in microseconds

#### SpeedRecord

Speed test results.

**Key Fields:**
- `download_kbps: Optional[int]` - Download speed in Kbps
- `upload_kbps: Optional[int]` - Upload speed in Kbps
- `speed_test_server: Optional[str]` - Test server URL

#### WebResponsivenessRecord

Web responsiveness measurements.

**Key Fields:**
- `ttfb_us: Optional[int]` - Time to First Byte in microseconds
- `dns_us: Optional[int]` - DNS resolution time in microseconds
- `web_url: Optional[str]` - Test URL

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
        scores = await client.get_scores_1m()
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
export ORB_BASE_URL="http://localhost:7080"
export ORB_CALLER_ID="my-application"
export ORB_TIMEOUT="60"
export ORB_MAX_RETRIES="5"
```

### Custom Headers

Add custom headers for authentication or other purposes:

```python
client = OrbClient(
    base_url="http://192.168.1.100:7080",
    caller_id="monitoring-system",
    headers={
        "Authorization": "Bearer your-token",
        "X-Custom-Header": "value"
    }
)
```

### Caller ID Management

The Orb Local API uses caller IDs to track which records have been delivered to each client, ensuring you only receive new data on subsequent requests:

```python
# Each client should use a unique caller ID
async with OrbClient(caller_id="dashboard-app") as client:
    scores = await client.get_scores_1m()  # Gets all available records first time
    
    # On subsequent calls, only new records since last request are returned
    new_scores = await client.get_scores_1m()  # Only new records

# Different caller ID gets all records again
async with OrbClient(caller_id="backup-system") as client:
    all_scores = await client.get_scores_1m()  # Gets all available records
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

See the `examples/` directory for usage examples:

- `examples/basic_usage.py` - Complete example showing all dataset types

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
- [Orb Datasets Configuration Documentation](https://orb.net/docs/deploy-and-configure/datasets-configuration#local-api) 
- [Orb Datasets Documentation](https://orb.net/docs/deploy-and-configure/datasets)

This client implementation is based on the official Orb Local Analytics API specification and provides full support for all documented datasets and endpoints.
