"""Test the exception classes."""

import pytest
from orb.exceptions import OrbError, OrbAPIError, OrbConnectionError


class TestOrbError:
    """Test cases for OrbError base exception."""

    def test_orb_error_basic(self):
        """Test basic OrbError creation."""
        error = OrbError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details == {}

    def test_orb_error_with_details(self):
        """Test OrbError with details."""
        details = {"code": "TEST_ERROR", "context": "test context"}
        error = OrbError("Test error", details=details)

        assert error.message == "Test error"
        assert error.details == details
        assert error.details["code"] == "TEST_ERROR"


class TestOrbAPIError:
    """Test cases for OrbAPIError."""

    def test_orb_api_error_basic(self):
        """Test basic OrbAPIError creation."""
        error = OrbAPIError("API error")
        assert str(error) == "API error"
        assert error.message == "API error"
        assert error.status_code is None
        assert error.response_data == {}
        assert error.details == {}

    def test_orb_api_error_with_status_code(self):
        """Test OrbAPIError with status code."""
        error = OrbAPIError("Bad request", status_code=400)
        assert error.message == "Bad request"
        assert error.status_code == 400

    def test_orb_api_error_with_response_data(self):
        """Test OrbAPIError with response data."""
        response_data = {
            "error": "Invalid parameter",
            "field": "dataset_name",
            "code": "INVALID_PARAMETER",
        }
        error = OrbAPIError("Validation failed", response_data=response_data)

        assert error.message == "Validation failed"
        assert error.response_data == response_data
        assert error.response_data["field"] == "dataset_name"

    def test_orb_api_error_full(self):
        """Test OrbAPIError with all parameters."""
        response_data = {"error": "Not found", "resource": "dataset"}
        details = {"request_id": "12345", "timestamp": "2024-01-01T00:00:00Z"}

        error = OrbAPIError(
            "Resource not found",
            status_code=404,
            response_data=response_data,
            details=details,
        )

        assert error.message == "Resource not found"
        assert error.status_code == 404
        assert error.response_data["resource"] == "dataset"
        assert error.details["request_id"] == "12345"


class TestOrbConnectionError:
    """Test cases for OrbConnectionError."""

    def test_orb_connection_error_basic(self):
        """Test basic OrbConnectionError creation."""
        error = OrbConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert error.message == "Connection failed"
        assert error.original_error is None
        assert error.details == {}

    def test_orb_connection_error_with_original(self):
        """Test OrbConnectionError with original error."""
        original = ValueError("Original error")
        error = OrbConnectionError("Connection failed", original_error=original)

        assert error.message == "Connection failed"
        assert error.original_error is original
        assert isinstance(error.original_error, ValueError)

    def test_orb_connection_error_with_details(self):
        """Test OrbConnectionError with details."""
        details = {"host": "localhost", "port": 8080, "timeout": 30}
        error = OrbConnectionError("Timeout", details=details)

        assert error.message == "Timeout"
        assert error.details == details
        assert error.details["host"] == "localhost"

    def test_orb_connection_error_full(self):
        """Test OrbConnectionError with all parameters."""
        original = ConnectionError("Network unreachable")
        details = {"retry_count": 3, "last_attempt": "2024-01-01T00:00:00Z"}

        error = OrbConnectionError(
            "Max retries exceeded",
            original_error=original,
            details=details,
        )

        assert error.message == "Max retries exceeded"
        assert error.original_error is original
        assert error.details["retry_count"] == 3


class TestExceptionInheritance:
    """Test exception inheritance and behavior."""

    def test_inheritance_chain(self):
        """Test that exceptions inherit correctly."""
        # Test OrbAPIError inherits from OrbError
        api_error = OrbAPIError("API error")
        assert isinstance(api_error, OrbError)
        assert isinstance(api_error, Exception)

        # Test OrbConnectionError inherits from OrbError
        conn_error = OrbConnectionError("Connection error")
        assert isinstance(conn_error, OrbError)
        assert isinstance(conn_error, Exception)

    def test_exception_catching(self):
        """Test that exceptions can be caught by base classes."""
        # Test catching OrbAPIError as OrbError
        with pytest.raises(OrbError):
            raise OrbAPIError("API error")

        # Test catching OrbConnectionError as OrbError
        with pytest.raises(OrbError):
            raise OrbConnectionError("Connection error")

        # Test catching any Orb error as Exception
        with pytest.raises(Exception):
            raise OrbAPIError("Any error")
