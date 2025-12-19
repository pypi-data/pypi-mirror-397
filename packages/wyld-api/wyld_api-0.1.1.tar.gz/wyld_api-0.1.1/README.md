# Wyld API Client

A Python client for interacting with Wyld Network's Satellite IoT API with support for custom payload schemas.

## Features

- 🔐 HMAC-SHA256 authentication
- 📡 Fetch device data from satellite IoT network
- 🎯 **Custom payload schema validation** - Define schemas for different device codecs
- ✅ Type-safe data access with Pydantic models
- 🔄 Flexible response parsing for varying device types

## Installation

```bash
# Using uv
uv add pydantic requests

# Or using pip
pip install pydantic requests
```

## Quick Start

### Basic Usage (Raw Data)

```python
from wyld_api_client import WyldAPIClient
import time

client = WyldAPIClient(
    org_id="your_org_id",
    api_token="your_api_token"
)

# Get raw data without validation
end_ts = int(time.time() * 1000)
start_ts = end_ts - (24 * 60 * 60 * 1000)  # 24 hours ago

data = client.get_device_data("device_id", start_ts, end_ts)
print(data)
```

### Advanced Usage with Schemas

The API returns different payload structures based on the device's codec. You can define schemas to validate and type-check the response data:

```python
from wyld_api_client import WyldAPIClient
from schemas import BasePayload
from pydantic import Field
from typing import Optional

# Define a schema for your device's codec
class TemperatureSensorPayload(BasePayload):
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: Optional[float] = None
    battery: Optional[int] = None

# Use the schema to get validated, typed data
client = WyldAPIClient(org_id="your_org", api_token="your_token")

temperature_data = client.get_device_data(
    dev_id="temp_sensor_001",
    start_ts=start_ts,
    end_ts=end_ts,
    payload_schema=TemperatureSensorPayload,  # Pass your schema
    validate=True
)

# Now you get typed objects with auto-completion!
for reading in temperature_data:
    print(f"Temperature: {reading.temperature}°C")
    if reading.humidity:
        print(f"Humidity: {reading.humidity}%")
```

## Custom Schemas for Different Device Types

Since the satellite IoT network uses different codecs per device type, you can create schemas for each:

### Example: GPS Tracker

```python
from schemas import BasePayload

class GPSTrackerPayload(BasePayload):
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    satellites: Optional[int] = None

# Use it
gps_data = client.get_device_data(
    dev_id="gps_tracker_123",
    start_ts=start_ts,
    end_ts=end_ts,
    payload_schema=GPSTrackerPayload
)

for location in gps_data:
    print(f"Position: {location.latitude}, {location.longitude}")
```

### Example: Water Level Sensor

```python
class WaterLevelSensorPayload(BasePayload):
    water_level_cm: float
    pressure_kpa: float
    battery_voltage: Optional[float] = None

water_data = client.get_device_data(
    dev_id="water_sensor_456",
    start_ts=start_ts,
    end_ts=end_ts,
    payload_schema=WaterLevelSensorPayload
)

for reading in water_data:
    print(f"Water Level: {reading.water_level_cm} cm")
```

## Dynamic Schema Selection

Handle multiple device types with a schema registry:

```python
# Create a mapping of device types to schemas
DEVICE_SCHEMAS = {
    "temperature": TemperatureSensorPayload,
    "gps": GPSTrackerPayload,
    "water_level": WaterLevelSensorPayload,
}

def get_device_data_with_schema(device_id, device_type, start_ts, end_ts):
    schema = DEVICE_SCHEMAS.get(device_type)
    return client.get_device_data(
        dev_id=device_id,
        start_ts=start_ts,
        end_ts=end_ts,
        payload_schema=schema,
        validate=True if schema else False
    )
```

## Error Handling

The client includes validation error handling:

```python
from pydantic import ValidationError

try:
    data = client.get_device_data(
        dev_id="device_123",
        start_ts=start_ts,
        end_ts=end_ts,
        payload_schema=TemperatureSensorPayload,
        validate=True
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Fall back to raw data
    raw_data = client.get_device_data(
        dev_id="device_123",
        start_ts=start_ts,
        end_ts=end_ts,
        payload_schema=None
    )
```

## API Reference

### `WyldAPIClient.get_device_data()`

Fetch device data with optional schema validation.

**Parameters:**
- `dev_id` (str): The device ID
- `start_ts` (int): Start timestamp in milliseconds since epoch
- `end_ts` (int): End timestamp in milliseconds since epoch
- `payload_schema` (Optional[Type[BasePayload]]): Pydantic model class for validation
- `validate` (bool): Enable/disable validation (default: True)

**Returns:**
- If `payload_schema` is None: Raw dict response
- If `payload_schema` provided: List of validated payload objects

## Schema Definition Guidelines

1. **Inherit from `BasePayload`**: All custom schemas should inherit from `BasePayload`
2. **Use Pydantic Field validators**: Leverage Pydantic's validation features
3. **Make fields Optional**: Use `Optional[]` for fields that may not always be present
4. **Add descriptions**: Use `Field(..., description="...")` for better documentation

```python
from schemas import BasePayload
from pydantic import Field, field_validator
from typing import Optional

class CustomPayload(BasePayload):
    # Required field
    sensor_value: float = Field(..., description="Primary sensor reading")
    
    # Optional field with default
    status: Optional[str] = Field(None, description="Device status")
    
    # Field with validation
    battery_level: int = Field(..., ge=0, le=100, description="Battery 0-100%")
    
    @field_validator('battery_level')
    def validate_battery(cls, v):
        if v < 10:
            print(f"Warning: Low battery ({v}%)")
        return v
```

## Benefits of Using Schemas

1. **Type Safety**: IDE auto-completion and type checking
2. **Validation**: Automatic data validation against your schema
3. **Documentation**: Self-documenting code with field descriptions
4. **Searchability**: Easier to search and filter data with typed objects
5. **Flexibility**: Support for varying codecs across device types
6. **Error Detection**: Catch data issues early in development

## Examples

See [usage_examples.py](usage_examples.py) for comprehensive examples of all features.

## License

[Your License Here]
