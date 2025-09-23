"""Pydantic models for Orb Local API dataset records.

Based on the official Orb Datasets specification:
https://orb.net/docs/deploy-and-configure/datasets
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class BaseDatasetRecord(BaseModel):
    """Base model for all Orb dataset records."""
    
    model_config = ConfigDict(extra="allow")
    
    # Common identifiers
    orb_id: str = Field(..., description="Orb Sensor identifier")
    orb_name: str = Field(..., description="Current Orb friendly name")
    device_name: str = Field(..., description="Hostname or device name") 
    orb_version: str = Field(..., description="Semantic version of collecting Orb")
    timestamp: int = Field(..., description="Timestamp in epoch milliseconds")
    
    # Common dimensions
    network_type: Optional[int] = Field(None, description="Network interface type (0=unknown, 1=wifi, 2=ethernet, 3=other)")
    network_state: Optional[int] = Field(None, description="Speed test load state during interval") 
    country_code: Optional[str] = Field(None, description="Geocoded 2-digit ISO country code")
    city_name: Optional[str] = Field(None, description="Geocoded city name")
    isp_name: Optional[str] = Field(None, description="ISP name from GeoIP lookup")
    public_ip: Optional[str] = Field(None, description="Public IP address")
    latitude: Optional[float] = Field(None, description="Orb location latitude")
    longitude: Optional[float] = Field(None, description="Orb location longitude")
    location_source: Optional[int] = Field(None, description="Location Source (0=unknown, 1=geoip)")


class Scores1mRecord(BaseDatasetRecord):
    """Model for scores_1m dataset records."""
    
    # Score-specific fields
    score_version: Optional[str] = Field(None, description="Semantic version of scoring methodology")
    
    # Measures
    orb_score: Optional[float] = Field(None, description="Orb Score over interval (0-100)")
    responsiveness_score: Optional[float] = Field(None, description="Responsiveness Score over interval (0-100)")
    reliability_score: Optional[float] = Field(None, description="Reliability Score over interval (0-100)")
    speed_score: Optional[float] = Field(None, description="Speed (Bandwidth) Score over interval (0-100)")
    speed_age_ms: Optional[int] = Field(None, description="Age of speed used in milliseconds")
    lag_avg_us: Optional[float] = Field(None, description="Lag in microseconds (avg if interval)")
    download_avg_kbps: Optional[int] = Field(None, description="Content download speed in Kbps")
    upload_avg_kbps: Optional[int] = Field(None, description="Content upload speed in Kbps")
    unresponsive_ms: Optional[float] = Field(None, description="Time spent in unresponsive state in Milliseconds")
    measured_ms: Optional[float] = Field(None, description="Time spent actively measuring in Milliseconds")
    lag_count: Optional[int] = Field(None, description="Count of Lag samples included")
    speed_count: Optional[int] = Field(None, description="Count of speed samples included")


class ResponsivenessRecord(BaseDatasetRecord):
    """Model for responsiveness dataset records (1s, 15s, 1m)."""
    
    # Additional responsiveness-specific fields
    network_name: Optional[str] = Field(None, description="Network name (SSID, if available)")
    
    # Measures
    lag_avg_us: Optional[int] = Field(None, description="Avg Lag in microseconds")
    latency_avg_us: Optional[int] = Field(None, description="Avg round trip latency in microseconds")
    jitter_avg_us: Optional[int] = Field(None, description="Avg Interpacket interarrival difference (jitter) in microseconds")
    latency_count: Optional[float] = Field(None, description="Count of round trip latency measurements that succeeded")
    latency_lost_count: Optional[int] = Field(None, description="Count of round trip latency measurements that were lost")
    packet_loss_pct: Optional[float] = Field(None, description="Packet loss percentage")
    lag_count: Optional[int] = Field(None, description="Lag sample count")
    
    # Router measures
    router_lag_avg_us: Optional[int] = Field(None, description="Avg router lag in microseconds")
    router_latency_avg_us: Optional[int] = Field(None, description="Avg router round trip latency in microseconds")
    router_jitter_avg_us: Optional[int] = Field(None, description="Avg router jitter in microseconds")
    router_latency_count: Optional[float] = Field(None, description="Count of router latency measurements that succeeded")
    router_latency_lost_count: Optional[int] = Field(None, description="Count of router latency measurements that were lost")
    router_packet_loss_pct: Optional[float] = Field(None, description="Router packet loss percentage")
    router_lag_count: Optional[int] = Field(None, description="Router lag sample count")
    
    # Pingers
    pingers: Optional[str] = Field(None, description="List (CSV) of active pingers")


class WebResponsivenessRecord(BaseDatasetRecord):
    """Model for web_responsiveness_results dataset records."""
    
    # Additional web responsiveness fields
    network_name: Optional[str] = Field(None, description="Network name (SSID, if available)")
    
    # Measures
    ttfb_us: Optional[int] = Field(None, description="Time to First Byte loading a web page in microseconds")
    dns_us: Optional[int] = Field(None, description="DNS resolver response time in microseconds")
    
    # Web-specific dimension
    web_url: Optional[str] = Field(None, description="URL endpoint for web test")


class SpeedRecord(BaseDatasetRecord):
    """Model for speed_results dataset records."""
    
    # Additional speed-specific fields  
    network_name: Optional[str] = Field(None, description="Network name (SSID, if available)")
    
    # Measures
    download_kbps: Optional[int] = Field(None, description="Download speed in Kbps")
    upload_kbps: Optional[int] = Field(None, description="Upload speed in Kbps")
    
    # Speed-specific dimensions
    speed_test_engine: Optional[int] = Field(None, description="Testing engine (0=orb, 1=iperf)")
    speed_test_server: Optional[str] = Field(None, description="Server URL or identifier")