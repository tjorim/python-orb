"""Test the Pydantic models."""

from typing import Dict, Any
import pytest

from orb.models import (
    BaseDatasetRecord,
    Scores1mRecord,
    ResponsivenessRecord,
    WebResponsivenessRecord,
    SpeedRecord,
)


class TestBaseDatasetRecord:
    """Test cases for BaseDatasetRecord model."""

    def test_base_dataset_minimal(self):
        """Test BaseDatasetRecord with minimal required fields."""
        record = BaseDatasetRecord(
            orb_id="test123",
            orb_name="TestOrb",
            device_name="test-device",
            orb_version="v1.3.0",
            timestamp=1640995200000,
        )
        assert record.orb_id == "test123"
        assert record.orb_name == "TestOrb"
        assert record.device_name == "test-device"
        assert record.orb_version == "v1.3.0"
        assert record.timestamp == 1640995200000
        assert record.network_type is None
        assert record.country_code is None

    def test_base_dataset_full(self):
        """Test BaseDatasetRecord with all fields."""
        data = {
            "orb_id": "test123",
            "orb_name": "TestOrb",
            "device_name": "test-device",
            "orb_version": "v1.3.0",
            "timestamp": 1640995200000,
            "network_type": 1,
            "network_state": 6,
            "country_code": "US",
            "city_name": "Seattle",
            "isp_name": "Example ISP",
            "public_ip": "203.0.113.1",
            "latitude": 47.6,
            "longitude": -122.3,
            "location_source": 1,
        }

        record = BaseDatasetRecord(**data)
        assert record.orb_id == "test123"
        assert record.network_type == 1
        assert record.country_code == "US"
        assert record.city_name == "Seattle"
        assert record.public_ip == "203.0.113.1"
        assert record.latitude == 47.6
        assert record.longitude == -122.3

    def test_base_dataset_extra_fields(self):
        """Test BaseDatasetRecord accepts extra fields."""
        data = {
            "orb_id": "test123",
            "orb_name": "TestOrb",
            "device_name": "test-device",
            "orb_version": "v1.3.0",
            "timestamp": 1640995200000,
            "extra_field": "extra_value",
            "another_field": 42,
        }

        record = BaseDatasetRecord(**data)
        assert record.orb_id == "test123"
        assert record.extra_field == "extra_value"
        assert record.another_field == 42


class TestScores1mRecord:
    """Test cases for Scores1mRecord model."""

    def test_scores_minimal(self):
        """Test Scores1mRecord with minimal required fields."""
        record = Scores1mRecord(
            orb_id="test123",
            orb_name="TestOrb",
            device_name="test-device",
            orb_version="v1.3.0",
            timestamp=1640995200000,
        )
        assert record.orb_id == "test123"
        assert record.orb_score is None
        assert record.responsiveness_score is None

    def test_scores_full(self):
        """Test Scores1mRecord with all fields."""
        data = {
            "orb_id": "test123",
            "orb_name": "TestOrb",
            "device_name": "test-device",
            "orb_version": "v1.3.0",
            "timestamp": 1640995200000,
            "score_version": "v2.1.0",
            "orb_score": 85.5,
            "responsiveness_score": 90.0,
            "reliability_score": 88.0,
            "speed_score": 80.0,
            "speed_age_ms": 300000,
            "lag_avg_us": 25000.5,
            "download_avg_kbps": 100000,
            "upload_avg_kbps": 50000,
            "unresponsive_ms": 150.0,
            "measured_ms": 59850.0,
            "lag_count": 120,
            "speed_count": 2,
            "network_type": 1,
            "country_code": "US",
        }

        record = Scores1mRecord(**data)
        assert record.orb_score == 85.5
        assert record.responsiveness_score == 90.0
        assert record.speed_score == 80.0
        assert record.lag_avg_us == 25000.5
        assert record.download_avg_kbps == 100000
        assert record.upload_avg_kbps == 50000
        assert record.lag_count == 120


class TestResponsivenessRecord:
    """Test cases for ResponsivenessRecord model."""

    def test_responsiveness_minimal(self):
        """Test ResponsivenessRecord with minimal required fields."""
        record = ResponsivenessRecord(
            orb_id="test123",
            orb_name="TestOrb",
            device_name="test-device",
            orb_version="v1.3.0",
            timestamp=1640995200000,
        )
        assert record.orb_id == "test123"
        assert record.lag_avg_us is None
        assert record.packet_loss_pct is None

    def test_responsiveness_full(self):
        """Test ResponsivenessRecord with all fields."""
        data = {
            "orb_id": "test123",
            "orb_name": "TestOrb",
            "device_name": "test-device",
            "orb_version": "v1.3.0",
            "timestamp": 1640995200000,
            "network_name": "MyWiFi",
            "lag_avg_us": 25000,
            "latency_avg_us": 15000,
            "jitter_avg_us": 5000,
            "latency_count": 100.0,
            "latency_lost_count": 5,
            "packet_loss_pct": 4.8,
            "lag_count": 120,
            "router_lag_avg_us": 20000,
            "router_latency_avg_us": 12000,
            "router_packet_loss_pct": 2.0,
            "pingers": "icmp|8.8.8.8|4,udp|1.1.1.1|4",
        }

        record = ResponsivenessRecord(**data)
        assert record.network_name == "MyWiFi"
        assert record.lag_avg_us == 25000
        assert record.latency_avg_us == 15000
        assert record.packet_loss_pct == 4.8
        assert record.router_lag_avg_us == 20000
        assert record.pingers == "icmp|8.8.8.8|4,udp|1.1.1.1|4"


class TestSpeedRecord:
    """Test cases for SpeedRecord model."""

    def test_speed_minimal(self):
        """Test SpeedRecord with minimal required fields."""
        record = SpeedRecord(
            orb_id="test123",
            orb_name="TestOrb",
            device_name="test-device",
            orb_version="v1.3.0",
            timestamp=1640995200000,
        )
        assert record.orb_id == "test123"
        assert record.download_kbps is None
        assert record.upload_kbps is None

    def test_speed_full(self):
        """Test SpeedRecord with all fields."""
        data = {
            "orb_id": "test123",
            "orb_name": "TestOrb",
            "device_name": "test-device",
            "orb_version": "v1.3.0",
            "timestamp": 1640995200000,
            "network_name": "MyWiFi",
            "download_kbps": 100000,
            "upload_kbps": 50000,
            "speed_test_engine": 0,
            "speed_test_server": "https://speed.cloudflare.com/",
            "network_type": 1,
            "country_code": "US",
        }

        record = SpeedRecord(**data)
        assert record.download_kbps == 100000
        assert record.upload_kbps == 50000
        assert record.speed_test_engine == 0
        assert record.speed_test_server == "https://speed.cloudflare.com/"
        assert record.network_name == "MyWiFi"


class TestWebResponsivenessRecord:
    """Test cases for WebResponsivenessRecord model."""

    def test_web_responsiveness_minimal(self):
        """Test WebResponsivenessRecord with minimal required fields."""
        record = WebResponsivenessRecord(
            orb_id="test123",
            orb_name="TestOrb",
            device_name="test-device",
            orb_version="v1.3.0",
            timestamp=1640995200000,
        )
        assert record.orb_id == "test123"
        assert record.ttfb_us is None
        assert record.dns_us is None

    def test_web_responsiveness_full(self):
        """Test WebResponsivenessRecord with all fields."""
        data = {
            "orb_id": "test123",
            "orb_name": "TestOrb",
            "device_name": "test-device",
            "orb_version": "v1.3.0",
            "timestamp": 1640995200000,
            "network_name": "MyWiFi",
            "ttfb_us": 150000,
            "dns_us": 25000,
            "web_url": "https://www.google.com/",
            "network_type": 1,
            "country_code": "US",
        }

        record = WebResponsivenessRecord(**data)
        assert record.ttfb_us == 150000
        assert record.dns_us == 25000
        assert record.web_url == "https://www.google.com/"
        assert record.network_name == "MyWiFi"
