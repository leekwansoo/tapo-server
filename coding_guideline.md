# FastMCP Integration Guideline

The following example shows the basic structure of an IoT FastMCP server. It is
documentation only; the dashboard does not execute Python embedded in HTML.

```python
from fastmcp import FastMCP
from zigbee import ZigbeeController
from tapo import TapoP115
from camera import CameraStream

mcp = FastMCP("IoT Gateway")

@mcp.tool()
def set_light_state(id: str, on: bool, brightness: int = 100):
    return zigbee.set_state(id, on, brightness)

@mcp.tool()
def get_sensor_data():
    return {"temp": dht.read_temp(), "hum": dht.read_hum()}

@mcp.resource("camera://{cam_id}/snapshot")
def cam_snapshot(cam_id: str):
    return camera.get_frame(cam_id)

if __name__ == "__main__":
    mcp.run(port=8000)
```

## Integration notes

- `FastMCP` creates the MCP server.
- `@mcp.tool()` exposes a Python function as an MCP action.
- `@mcp.resource()` exposes read-only data through a URI template.
- Hardware clients such as `zigbee`, `dht`, and `camera` must be initialized
  before the registered functions call them.
- The browser dashboard should communicate with FastAPI over HTTP or
  WebSockets. It should not execute Python code directly.
- Keep shared hardware logic in service functions so both FastAPI routes and
  MCP tools can call the same implementation.
