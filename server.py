# server.py
from xmlrpc import client

from fastmcp import FastMCP
from tapo import ApiClient
import asyncio
import random

mcp = FastMCP("IoT-Gateway")
# Tapo 계정 (환경변수로 관리)
TAPO_EMAIL = "your_tapo@email.com"
TAPO_PW = "your_password"
TAPO_IPS = {"Light1": "192.168.0.101", "Light2": "192.168.0.102", "Switch1": "192.168.0.103"}

# --- Downlink: Server -> Terminal ---
@mcp.tool()
async def terminal_control(ip: str, action: str):
    """Server -> Terminal"""
    device = await client.p115(ip)
    if action == "on": await device.on()
    if action == "off": await device.off()
    return f"Command {action} sent to {ip}"

# --- < Both-way: Server <-> Terminal > ---
@mcp.tool()
async def monitor_bothway(ip: str):
    """Both-way: Terminal이 Server로 자발적으로 보고"""
    device = await client.p115(ip)
    while True:
        energy = await device.get_energy_usage()
        if energy.current_power > 1500: # 1500W 넘으면
            # Terminal -> Server -> Client 로 Push
            await mcp.notify(f"ALARM from {ip}: Overpower {energy.current_power}W!")
        await asyncio.sleep(2)
        
# --- Uplink: Terminal -> Server ---
@mcp.tool()
async def get_temperature():
    """온도 센서 데이터 Uplink"""
    # 실제로는 zigbee2mqtt MQTT 구독, 여기선 시뮬레이션
    return {"temperature": round(22 + random.random()*4, 1), "humidity": random.randint(50,65), "battery": 87}

@mcp.tool()
async def get_door_status(door_id: str):
    """Door 상태 Uplink"""
    # zigbee2mqtt/Door1 토픽에서 가져옴
    return {"door_id": door_id, "status": "CLOSED", "last_open": "2026-05-13T10:20:00"}

@mcp.tool()
async def get_camera_snapshot(camera_id: str):
    """카메라 스냅샷 Uplink - RTSP에서 캡처"""
    return {"camera_id": camera_id, "snapshot_url": f"/snapshots/{camera_id}.jpg", "motion": False}

# --- Downlink: Server -> Terminal ---
@mcp.tool()
async def control_door(door_id: str, command: str):
    """Server -> Terminal: Door OPEN/CLOSE"""
    # Zigbee 액추에이터 또는 Tapo 플러그로 릴레이 제어
    print(f"[DOWNLINK] {door_id} -> {command}")
    return {"result": "OK", "door_id": door_id, "command": command}

@mcp.tool()
async def control_light(light_id: str, state: str):
    """Server -> Terminal: Light ON/OFF"""
    ip = TAPO_IPS[light_id]
    client = ApiClient(TAPO_EMAIL, TAPO_PW)
    device = await client.p115(ip)
    if state == "ON": await device.on()
    else: await device.off()
    return {"result": "OK", "light_id": light_id, "state": state, "power_w": 12.5 if state=="ON" else 0}

@mcp.resource("config://devices")
def device_list():
    return list(TAPO_IPS.keys()) + ["Door1", "Door2", "Temp1", "Camera1", "Camera2"]

if __name__ == "__main__":
    mcp.run(transport="sse", port=8000) # 대시보드가 이 포트에 연결