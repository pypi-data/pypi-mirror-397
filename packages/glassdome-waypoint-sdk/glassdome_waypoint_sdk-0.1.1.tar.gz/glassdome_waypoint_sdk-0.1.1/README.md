# Glassdome Waypoint SDK

Python SDK for the Glassdome Waypoint API. This SDK provides a convenient interface for interacting with the [Waypoint API](https://developers.glassdome.dev/waypoint).

## Installation

```bash
pip install glassdome-waypoint-sdk
```

## Requirements

- Python >= 3.9
- requests >= 2.28.0
- protobuf >= 6.0.0
- googleapis-common-protos >= 1.60.0

## Quick Start

### Authentication

The SDK currently supports API key authentication.

```python
from glassdome_waypoint_sdk import WaypointClient, WaypointConfig

# Configure the client
config = WaypointConfig(base_url="https://waypoint.glassdome.dev")
client = WaypointClient.from_api_key(config, "your-api-key")
```

## Usage Examples

- [Listing Sites](https://developers.glassdome.dev/waypoint/sites#python-sdk)
- [Managing Products](https://developers.glassdome.dev/waypoint/products#python-sdk)
- [Running PCF Pipeline](https://developers.glassdome.dev/waypoint/pcf#python-sdk)

## API Reference

### WaypointClient

Main entrypoint for interacting with the Waypoint API.

**Attributes:**

- `client.operation`: long-running operations
- `client.site`: site APIs
- `client.product`: product APIs
- `client.pcf`: PCF APIs

**Factory method:**

```python
WaypointClient.from_api_key(config: WaypointConfig, api_key: str) -> WaypointClient
```

### WaypointConfig

```python
@dataclass
class WaypointConfig:
    base_url: str
    timeout_seconds: float = 60.0
```

### Long-Running Operations

Batch import operations return `Operation` object.

```python
op = client.product.create_products(requests=[...])

# Block until done or timeout
op.wait()

# With return options
op.wait(return_options=OperationReturnOptions(response=True))

# Check for error
if err := op.error():
    print(err.code, err.message)

# Access the response
if resp := op.response():
    # Process response
    pass
```

## Error Handling

The SDK defines these error classes:

- `WaypointError`: Base SDK error
- `WaypointHTTPError`: HTTP errors
- `AnyUnpackError`: Protobuf Any unpacking errors

```python
from glassdome_waypoint_sdk import WaypointError, WaypointHTTPError

try:
    # Your API call
    pass
except WaypointHTTPError as e:
    print(f"HTTP error: {e}")
except WaypointError as e:
    print(f"SDK error: {e}")
```

## License

This SDK is proprietary and may be used only under agreement with Glassdome Inc.

## Support

For questions or support, contact: <developer@glassdomeinc.com>
