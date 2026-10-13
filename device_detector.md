#   Tapo 장치의 Device ID / IP / MAC (to-link ID) 찾는 방법 4가지 

##  1. 가장 쉬운 방법 - Tapo 앱에서 찾기 (30초)
Tapo 앱 열기 → P115 장치 클릭
오른쪽 위 톱니바퀴(설정) → 기기 정보
여기서 확인:
```text
모델: Tapo P115
MAC 주소: A4:15:88:XX:XX:XX  ← 이게 to-link ID 중 하나
IP 주소: 192.168.0.103      ← 우리가 main.py에 넣는 IP
Device ID: 8006... (긴 문자열) ← 클라우드 ID
```
##  2. Python으로 자동 찾기 - python-kasa로 스캔 (추천!)
! pip install python-kasa

kasa discover

## Results
```text
Discovered 4 devices:
- Tapo P115 (Switch1) - IP: 192.168.0.103, MAC: A4:15:88:12:34:56, Device ID: 8006AABBCCDD..., Model: P115
- Tapo P115 (Switch2) - IP: 192.168.0.104, MAC: A4:15:88:12:34:57
- Tapo C200 (Camera1) - IP: 192.168.0.201
```

##  3.Python 코드로 찾기:
```code
# find_tapo_ids.py
import asyncio
from kasa import Discover

async def find_tapo():
    print("Scanning Tapo devices... (5초)")
    devices = await Discover.discover(timeout=5)
    for ip, dev in devices.items():
        await dev.update()
        print(f"\n--- {dev.alias} ---")
        print(f"IP: {ip}")
        print(f"MAC: {dev.mac}")
        print(f"Device ID: {dev.device_id}")  # ← to-link ID = device_id
        print(f"Model: {dev.model}")
        print(f"Device Type: {dev.device_type}")

asyncio.run(find_tapo())
```

## 4. 공유기 관리자 페이지에서 찾기
브라우저에서 192.168.0.1 접속 (공유기마다 다름, 192.168.1.1일 수도)
로그인 → DHCP 클라이언트 리스트 또는 연결된 장치
목록에서 Tapo_P115 또는 a4-15-88-xx-xx-xx로 시작하는 장치 찾기

```text
장치 이름: Tapo_P115_1234
IP: 192.168.0.103
MAC: A4:15:88:12:34:56  ← to-link ID
```
