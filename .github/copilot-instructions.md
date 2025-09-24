# Python-Orb: Async Python Client for Orb Local API

Python-Orb is an async Python client library for accessing Orb Local API datasets. It provides typed Pydantic models for network performance metrics including scores, responsiveness, speed tests, and web responsiveness measurements.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Setup (5 seconds)
Run these commands to set up the development environment:
```bash
# Install development dependencies - takes ~3 seconds
pip install -e .[dev]
```

### Build and Test (2 seconds total)
- `pytest` -- runs all 39 tests, takes ~1 second. NEVER CANCEL.
- `pytest --tb=short` -- runs tests with shorter tracefile output
- No separate build step required - this is a pure Python package

### Code Quality and Linting (1 second total)
ALWAYS run these before committing. The code currently has linting issues that need fixing:
- `ruff format` -- auto-formats code, takes ~0.01 seconds
- `ruff check` -- lints code, takes ~0.01 seconds  
- `ruff check --fix` -- auto-fixes lint issues where possible
- `mypy orb/` -- type checking, takes ~0.8 seconds
  - Currently fails due to pyproject.toml python_version setting (3.8) being unsupported
  - Has 1 type error in orb/client.py:137 about returning Any

### Run the Application
This is a client library, not a standalone application. Test functionality via:
- `python examples/basic_usage.py` -- runs example client code
  - Expects Orb Local API service running on http://localhost:7080
  - Will show connection error if no local Orb service is available
  - This is expected behavior when no Orb device is configured

## Validation

### Manual Testing Scenarios
Since this is a client library for hardware devices, full end-to-end testing requires an actual Orb device:

1. **Unit Test Validation**: Always run `pytest` to ensure all 39 tests pass
2. **Import Test**: Test that the library imports correctly:
   ```python
   from orb import OrbClient, OrbError, OrbAPIError, OrbConnectionError
   ```
3. **Example Code**: Run `python examples/basic_usage.py` and verify it attempts connection
4. **Mock Usage**: Create test scenarios with mocked responses using the existing test patterns

### Code Quality Requirements
ALWAYS run before committing or the code will not meet project standards:
```bash
ruff format && ruff check --fix && mypy orb/
```

## Repository Structure

### Key Directories and Files
```
orb/                    # Main package directory
├── __init__.py         # Package exports and version
├── client.py           # OrbClient async HTTP client class  
├── exceptions.py       # Exception hierarchy (OrbError, OrbAPIError, OrbConnectionError)
└── models.py           # Pydantic models for API responses
tests/                  # Test suite (39 tests total)
├── conftest.py         # Test configuration and fixtures
├── test_client.py      # OrbClient functionality tests
├── test_exceptions.py  # Exception handling tests
└── test_models.py      # Pydantic model validation tests
examples/
└── basic_usage.py      # Complete usage example
```

### Configuration Files
- `pyproject.toml` -- Project metadata, dependencies, and tool configuration
- `.gitignore` -- Standard Python gitignore
- `.github/dependabot.yml` -- Dependabot configuration for pip updates

## Common Tasks

### Adding New Features
1. Add implementation to appropriate module in `orb/`
2. Add comprehensive tests in `tests/`
3. Update examples if needed
4. Always run quality checks: `ruff format && ruff check --fix && pytest`

### Dependencies Management
Project uses modern Python packaging with `pyproject.toml`:
- Core deps: `httpx`, `pydantic>=2.0.0`, `tenacity` 
- Dev deps: `pytest`, `pytest-asyncio`, `pytest-mock`, `respx`, `ruff`, `mypy`
- Install: `pip install -e .[dev]`

### Testing Patterns
The project uses pytest with async support. Key testing utilities:
- `respx` for mocking HTTP responses
- `pytest-asyncio` for async test support  
- `pytest-mock` for mocking
- Test fixtures in `conftest.py`

Example test pattern:
```python
@pytest.mark.asyncio
async def test_get_scores_1m(self, client, mock_respx):
    mock_data = [{"orb_id": "test123", "orb_score": 75.0}]
    mock_respx.get("http://test.example.com/api/v2/datasets/scores_1m.json").mock(
        return_value=httpx.Response(200, json=mock_data)
    )
    records = await client.get_scores_1m()
    assert len(records) == 1
    assert records[0]["orb_score"] == 75.0
```

## API Overview

### OrbClient Usage
```python
import asyncio
from orb import OrbClient

async def main():
    async with OrbClient(base_url="http://localhost:7080", caller_id="my-app") as client:
        scores = await client.get_scores_1m()
        responsiveness = await client.get_responsiveness_1s()
        speed_tests = await client.get_speed_results()
        web_resp = await client.get_web_responsiveness_results()

asyncio.run(main())
```

### Dataset Types
- `scores_1m` -- 1-minute aggregated Orb scores
- `responsiveness_1s` -- 1-second responsiveness measurements  
- `speed_results` -- Speed test results
- `web_responsiveness_results` -- Web performance measurements

### Error Handling
- `OrbError` -- Base exception class
- `OrbAPIError` -- HTTP API errors (4xx, 5xx responses)
- `OrbConnectionError` -- Network connection failures

## Current Known Issues

### Code Quality Issues (Must Fix Before Committing)
1. **Formatting**: 9 files need formatting (`ruff format` fixes automatically)
2. **Linting**: 27 lint errors including unused imports, line length, sorting issues
3. **Type Checking**: mypy configuration needs Python 3.9+ (currently set to 3.8)
4. **MyPy Error**: client.py:137 returns Any instead of dict[str, Any]

### Fix Command Sequence
```bash
# Fix most issues automatically
ruff format
ruff check --fix

# Fix mypy config - change python_version from "3.8" to "3.9" in pyproject.toml
# Fix the remaining type annotation issues manually
```

## Project Context

This library implements the official Orb Local Analytics API specification. Orb devices are network performance monitoring hardware that provide real-time metrics about internet connectivity, responsiveness, and speed. The Local API allows querying this data locally without cloud dependencies.

Key concepts:
- **Caller ID**: Unique identifier for polling clients to optimize data retrieval
- **Datasets**: Different types of metrics (scores, responsiveness, speed, web)  
- **Local API**: HTTP API served by Orb devices on port 7080 (default)
- **Identifiable Data**: Optional inclusion of potentially sensitive info like IP addresses

## References

- [Orb Local Analytics Documentation](https://orb.net/docs/deploy-and-configure/local-analytics)
- [Orb Datasets Configuration](https://orb.net/docs/deploy-and-configure/datasets-configuration#local-api)
- [Orb Datasets Documentation](https://orb.net/docs/deploy-and-configure/datasets)