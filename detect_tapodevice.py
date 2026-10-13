# find_tapo_ids.py
import asyncio
from tapo import ApiClient
import os
from kasa import Discover
from dotenv import load_dotenv
load_dotenv()

TAPO_EMAIL = os.getenv("TAPO_EMAIL")
TAPO_PASSWORD = os.getenv("TAPO_PASSWORD")

async def find_tapo(timeout):
    print(f"Scanning Tapo devices... ({timeout}초)")
    devices = await Discover.discover(timeout=timeout)
    for ip, dev in devices.items():
        await dev.update()
        print(f"\n--- {dev.alias} ---")
        print(f"IP: {ip}")
        print(f"MAC: {dev.mac}")
        print(f"Device ID: {dev.device_id}")  # ← to-link ID = device_id
        print(f"Model: {dev.model}")
        print(f"Device Type: {dev.device_type}")
        
# find_tapo_p110.py


TAPO_EMAIL = os.getenv("TAPO_EMAIL")
TAPO_PASSWORD = os.getenv("TAPO_PASSWORD")

async def get_tapo_info():
    # IP를 모르면 먼저 kasa discover로 IP 찾기
    ips = ["192.168.0.50", "192.168.0.51"]
    
    client = ApiClient(TAPO_EMAIL, TAPO_PASSWORD)
    
    for ip in ips:
        try:
            print(f"\nTrying {ip}...")
            device = await client.p115(ip)
            info = await device.get_device_info()
            d = info.to_dict()
            
            print(f"✅ Found!")
            print(f"  IP: {ip}")
            print(f"  Device ID: {d.get('device_id')}")  # ← to-link ID
            print(f"  MAC: {d.get('mac')}")
            print(f"  Model: {d.get('model')}")
            print(f"  Nickname: {d.get('nickname')}")
            print(f"  SSID: {d.get('ssid')}")
            
        except Exception as e:
            print(f"  ❌ Not found: {e}")

asyncio.run(get_tapo_info())

asyncio.run(find_tapo(10))