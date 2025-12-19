from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, List
from datetime import datetime


class BasePayload(BaseModel):
    """Base class for all payload schemas. Users should inherit from this."""
    
    model_config = ConfigDict(extra="allow")  # Allow extra fields not defined in schema


class Measurement(BaseModel):
    """Base measurement structure."""
    date: str
    value: Optional[Any] = None
    
    model_config = ConfigDict(extra="allow")


class DataArray(BaseModel):
    """Base data array structure."""
    measurements: List[Measurement]
    
    model_config = ConfigDict(extra="allow")


class DeviceData(BaseModel):
    """Base device data structure."""
    data_array: List[DataArray]
    
    model_config = ConfigDict(extra="allow")


class ObjectJSON(BaseModel):
    """Base objectJSON structure."""
    data: DeviceData
    
    model_config = ConfigDict(extra="allow")


class DeviceRecord(BaseModel):
    """Base device record structure."""
    objectJSON: ObjectJSON
    
    model_config = ConfigDict(extra="allow")


# Example custom payload schemas for different device types
class TemperatureSensorPayload(BasePayload):
    """Example schema for temperature sensor codec."""
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    battery: Optional[int] = Field(None, description="Battery level")


class GPSTrackerPayload(BasePayload):
    """Example schema for GPS tracker codec."""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    satellites: Optional[int] = None
