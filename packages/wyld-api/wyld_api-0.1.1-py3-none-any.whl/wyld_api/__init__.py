"""
Wyld API Client
===============

A Python client for interacting with Wyld Network's Satellite IoT API 
with support for custom payload schemas.

Basic Usage:
    >>> from wyld_api import WyldAPIClient
    >>> client = WyldAPIClient(org_id="your_org", api_token="your_token")
    >>> data = client.get_device_data("device_id", start_ts, end_ts)

With Schema Validation:
    >>> from wyld_api import WyldAPIClient
    >>> from wyld_api.schemas import BasePayload
    >>> 
    >>> class MyDevicePayload(BasePayload):
    ...     temperature: float
    ...     battery: int
    >>> 
    >>> data = client.get_device_data(
    ...     "device_id", start_ts, end_ts,
    ...     payload_schema=MyDevicePayload
    ... )
"""

from wyld_api.client import WyldAPIClient, get_message_signature
from wyld_api.schemas import (
    BasePayload,
    Measurement,
    DataArray,
    DeviceData,
    ObjectJSON,
    DeviceRecord,
    TemperatureSensorPayload,
    GPSTrackerPayload,
)

__version__ = "0.1.1"
__author__ = "Your Name"
__all__ = [
    "WyldAPIClient",
    "get_message_signature",
    "BasePayload",
    "Measurement",
    "DataArray",
    "DeviceData",
    "ObjectJSON",
    "DeviceRecord",
    "TemperatureSensorPayload",
    "GPSTrackerPayload",
]
