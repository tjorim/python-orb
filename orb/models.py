"""Mashumaro dataclass models for Orb Local API dataset records.

Based on the official Orb Datasets specification:
https://orb.net/docs/deploy-and-configure/datasets
"""

from dataclasses import dataclass
from typing import Optional

from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class BaseDatasetRecord(DataClassORJSONMixin):
    """Base model for all Orb dataset records."""

    # Common identifiers
    orb_id: str  # Orb Sensor identifier
    orb_name: str  # Current Orb friendly name
    device_name: str  # Hostname or device name
    orb_version: str  # Semantic version of collecting Orb
    timestamp: int  # Timestamp in epoch milliseconds

    # Common dimensions
    network_type: Optional[int] = None  # Network interface type (0=unknown, 1=wifi, 2=ethernet, 3=other)
    network_state: Optional[int] = None  # Speed test load state during interval
    country_code: Optional[str] = None  # Geocoded 2-digit ISO country code
    city_name: Optional[str] = None  # Geocoded city name
    isp_name: Optional[str] = None  # ISP name from GeoIP lookup
    public_ip: Optional[str] = None  # Public IP address
    latitude: Optional[float] = None  # Orb location latitude
    longitude: Optional[float] = None  # Orb location longitude
    location_source: Optional[int] = None  # Location Source (0=unknown, 1=geoip)


@dataclass
class Scores1mRecord(BaseDatasetRecord):
    """Model for scores_1m dataset records."""

    # Score-specific fields
    score_version: Optional[str] = None  # Semantic version of scoring methodology

    # Measures
    orb_score: Optional[float] = None  # Orb Score over interval (0-100)
    responsiveness_score: Optional[float] = None  # Responsiveness Score over interval (0-100)
    reliability_score: Optional[float] = None  # Reliability Score over interval (0-100)
    speed_score: Optional[float] = None  # Speed (Bandwidth) Score over interval (0-100)
    speed_age_ms: Optional[int] = None  # Age of speed used in milliseconds
    lag_avg_us: Optional[float] = None  # Lag in microseconds (avg if interval)
    download_avg_kbps: Optional[int] = None  # Content download speed in Kbps
    upload_avg_kbps: Optional[int] = None  # Content upload speed in Kbps
    unresponsive_ms: Optional[float] = None  # Time spent in unresponsive state in Milliseconds
    measured_ms: Optional[float] = None  # Time spent actively measuring in Milliseconds
    lag_count: Optional[int] = None  # Count of Lag samples included
    speed_count: Optional[int] = None  # Count of speed samples included


@dataclass
class ResponsivenessRecord(BaseDatasetRecord):
    """Model for responsiveness dataset records (1s, 15s, 1m)."""

    # Additional responsiveness-specific fields
    network_name: Optional[str] = None  # Network name (SSID, if available)

    # Measures
    lag_avg_us: Optional[int] = None  # Avg Lag in microseconds
    latency_avg_us: Optional[int] = None  # Avg round trip latency in microseconds
    jitter_avg_us: Optional[int] = None  # Avg Interpacket interarrival difference (jitter) in microseconds
    latency_count: Optional[float] = None  # Count of round trip latency measurements that succeeded
    latency_lost_count: Optional[int] = None  # Count of round trip latency measurements that were lost
    packet_loss_pct: Optional[float] = None  # Packet loss percentage
    lag_count: Optional[int] = None  # Lag sample count

    # Router measures
    router_lag_avg_us: Optional[int] = None  # Avg router lag in microseconds
    router_latency_avg_us: Optional[int] = None  # Avg router round trip latency in microseconds
    router_jitter_avg_us: Optional[int] = None  # Avg router jitter in microseconds
    router_latency_count: Optional[float] = None  # Count of router latency measurements that succeeded
    router_latency_lost_count: Optional[int] = None  # Count of router latency measurements that were lost
    router_packet_loss_pct: Optional[float] = None  # Router packet loss percentage
    router_lag_count: Optional[int] = None  # Router lag sample count

    # Pingers
    pingers: Optional[str] = None  # List (CSV) of active pingers


@dataclass
class WebResponsivenessRecord(BaseDatasetRecord):
    """Model for web_responsiveness_results dataset records."""

    # Additional web responsiveness fields
    network_name: Optional[str] = None  # Network name (SSID, if available)

    # Measures
    ttfb_us: Optional[int] = None  # Time to First Byte loading a web page in microseconds
    dns_us: Optional[int] = None  # DNS resolver response time in microseconds

    # Web-specific dimension
    web_url: Optional[str] = None  # URL endpoint for web test


@dataclass
class SpeedRecord(BaseDatasetRecord):
    """Model for speed_results dataset records."""

    # Additional speed-specific fields
    network_name: Optional[str] = None  # Network name (SSID, if available)

    # Measures
    download_kbps: Optional[int] = None  # Download speed in Kbps
    upload_kbps: Optional[int] = None  # Upload speed in Kbps

    # Speed-specific dimensions
    speed_test_engine: Optional[int] = None  # Testing engine (0=orb, 1=iperf)
    speed_test_server: Optional[str] = None  # Server URL or identifier
