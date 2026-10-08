# IoT Gateway 시스템 사용자 메뉴얼

## Real Device 연결 방법 (Device 종류별)
Version: 1.0 | FastAPI + Jinja2 + FastMCP Gateway
Target: Tapo P115 Smart Plug, Zigbee Sensors, Tapo Camera

##  1. 공통 준비사항
### 1.1 네트워크 구성
```text
[공유기(AP)] 192.168.0.1
   ├─ PC (FastAPI Server) 192.168.0.100 (고정 IP 권장)
   ├─ Tapo P115 (Switch1) 192.168.0.103
   ├─ Tapo P115 (Switch2) 192.168.0.104
   ├─ Zigbee Dongle (USB) -> COM3 / /dev/ttyUSB0
   └─ Tapo Camera C200 192.168.0.201
```
모든 기기는 같은 공유기에 연결
공유기 AP Isolation (클라이언트 격리) OFF
PC 방화벽 8000 포트 허용

### 1.2 PC 소프트웨어 설치
```text
pip install -r requirements.txt
```
# fastapi uvicorn jinja2 fastmcp tapo python-kasa paho-mqtt opencv-python

##  2. Device 종류별 연결 방법

### 2.1 [Tapo P115] 에너지 모니터링 스마트 플러그 - Wi-Fi (Light1, Light2, Switch1, Switch2)
모델: Tapo P115, P110, P110M 모두 동일 방법. P115 권장 (원형, 간섭 없음)

### Step 1: 최초 Provisioning (1회만, 스마트폰 또는 PC)

**방법 A** - 스마트폰 Tapo 앱 (가장 쉬움, 2분)

Tapo 앱 설치 (iOS/Android) -> TP-Link 계정 생성
P115 전원 콘센트에 꽂기
앱에서 + -> 플러그 -> P115 선택
집 Wi-Fi SSID/비밀번호 입력 (예: IoT-Lab / 12345678)
연결 완료 후 앱에서 IP 확인: 기기 설정 -> 기기 정보 -> IP 주소

**방법 B** - PC에서 직접 (Original Scheme, 앱 없이)

```text
# provision_tapo.py
from tapo import ApiClient
import asyncio
async def provision():
    client = ApiClient("your_tapo@email.com", "your_password")
    # P115가 Setup 모드일 때 BLE로 Wi-Fi 정보 주입
    # (Tapo 앱 대신 PC가 직접)
    device = await client.p115("192.168.0.103")
    print(await device.get_device_info())
asyncio.run(provision())
```
### Step 2: main.py / server.py에 등록

# main.py 상단
```text
TAPO_EMAIL = "your_tapo@email.com"
TAPO_PASSWORD = "your_password"
DEVICE_IPS = {
    "Light1": "192.168.0.101",  # 실제 앱에서 확인한 IP
    "Light2": "192.168.0.102",
    "Switch1": "192.168.0.103", # P115
    "Switch2": "192.168.0.104", # P115
}
```
공유기에서 DHCP 고정 IP 설정 권장 (MAC 주소로 고정)

### Step 3: 테스트

**터미널에서**
python -c "from tapo import ApiClient; import asyncio; ..."

**또는**
curl -X POST http://localhost:8000/api/control/light -H "Content-Type: application/json" -d '{"light_id":"Switch1","state":"ON"}'
대시보드에서 Switch1 토글 -> 실제 플러그 딸깍 소리 + 파란 LED
Uplink: 전력 W가 0 -> 800W로 변경 확인


**문제 해결**

안 보일 때: kasa discover 로 스캔 python -m kasa discover
Tapo 계정 2FA 켜져 있으면 끄기
P115 측면 버튼 10초 눌러 공장 초기화 후 재시도
2.2 [Zigbee 센서] Temperature Sensor, Door1, Door2
필요: SONOFF Zigbee 3.0 USB Dongle Plus (ZBDongle-P) + zigbee2mqtt + Mosquitto MQTT

##  Step 1: 하드웨어 연결

ZBDongle-P를 PC USB에 꽂기
장치 관리자에서 COM 포트 확인 (Windows: COM3, Linux: /dev/ttyUSB0)
Step 2: MQTT Broker 설치

## Windows: Mosquitto 설치 https://mosquitto.org/download/

**설치 후 서비스 시작**
net start mosquitto
# 테스트: mosquitto_sub -h localhost -t zigbee2mqtt/#
Step 3: zigbee2mqtt 설치 및 설정

**Node.js 설치 후**
git clone https://github.com/Koenkk/zigbee2mqtt.git
cd zigbee2mqtt
npm install
# configuration.yaml 수정
homeassistant: false
permit_join: true
mqtt:
  base_topic: zigbee2mqtt
  server: mqtt://localhost
serial:
  port: COM3  # 또는 /dev/ttyUSB0
  adapter: zstack
Step 4: 센서 페어링

**npm start로 zigbee2mqtt 실행**
온도 센서 페어링 버튼 5초 누르기 -> 로그에 Device '0x...' joined 확인
Door 센서 자석 분리 -> Open/Close 로그 확인
Step 5: FastAPI Gateway와 연동

**main.py에 MQTT Subscriber 추가 (server.py에도 동일)**
```text
import paho.mqtt.client as mqtt
def on_message(client, userdata, msg):
    # 예: zigbee2mqtt/Temp1 -> {"temperature":23.5,"humidity":58,"battery":87}
    # 예: zigbee2mqtt/Door1 -> {"contact":false} (false=OPEN)
    topic = msg.topic
    payload = json.loads(msg.payload)
    if "Temp1" in topic:
        STATE["Temp1"]["temperature"] = payload["temperature"]
    if "Door1" in topic:
        STATE["Door1"] = "OPEN" if not payload["contact"] else "CLOSED"
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.subscribe("zigbee2mqtt/#")
mqtt_client.loop_start()
```

##  Step 6: 테스트

온도 센서에 입김 불기 -> 대시보드 그래프 23°C -> 26°C 상승 (Uplink)

Door 자석 분리 -> 테이블 Status OPEN으로 변경 + 로그 [UPLINK] Door1 -> Server: OPEN

##  2.3 [Home Camera] Tapo C200 / C320WS - RTSP 모니터링
### Step 1: 카메라 Tapo 앱에 등록
```text
Tapo 앱에서 C200/C320 추가 (P115와 동일 방법)
카메라 설정 -> 고급 설정 -> RTSP 활성화
RTSP 계정 생성: 사용자 camera_user / 비밀번호 1234abcd 생성
```

### Step 2: RTSP URL 확인
```text
rtsp://camera_user:1234abcd@192.168.0.201:554/stream1  # 고화질
rtsp://camera_user:1234abcd@192.168.0.201:554/stream2  # 저화질
Tapo 앱 -> 카메라 -> 설정 -> RTSP 주소에서 확인
```

### Step 3: main.py에 등록

# main.py 상단
```text
CAMERA_RTSP = {
    "Camera1": "rtsp://camera_user:1234abcd@192.168.0.201/stream1",
    "Camera2": "rtsp://camera_user:1234abcd@192.168.0.202/stream1",
}
```
### Step 4: VLC로 먼저 테스트

VLC -> 미디어 -> 네트워크 스트림 열기 -> RTSP URL 붙여넣기
화면 나오면 성공

### Step 5: FastAPI 연동 테스트
```text
curl http://localhost:8000/api/status
text

**Camera1 online:true 확인**

**스냅샷**
```text
curl -X POST http://localhost:8000/api/control/camera/Camera1 -H "Content-Type: application/json" -d '{"action":"SNAPSHOT"}'
```

대시보드 카메라 박스 LIVE 빨간 배지 확인
```text
[SNAPSHOT] 버튼 -> /static/snapshots/ 폴더에 jpg 저장
```

**문제 해결**

**RTSP 안 될 때**: 카메라 펌웨어 업데이트, Tapo 앱에서 타사 연동 허용 ON
**지연 심할 때**: stream2 (저화질) 사용, opencv 버퍼 사이즈 1로 설정
**방화벽**: 554 포트 허용

##  3. 전체 시스템 기동 순서 (매뉴얼)
**터미널 1: MQTT Broker**
```text
mosquitto -v
```
**터미널 2: zigbee2mqtt (Zigbee 센서용)**
```text
cd zigbee2mqtt
npm start
```
**터미널 3: FastAPI Gateway (메인)**
```text
cd C:/IoT-Project
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
**브라우저**
```text
http://localhost:8000/ -> 통합 대시보드
Both-way 시연 시나리오
```
[DOWNLINK] 대시보드 Light1 토글 ON -> 실제 P115 클릭 소리 (Server->Terminal)
[UPLINK] 전력 0W -> 1200W로 즉시 변경 (Terminal->Server)
[UPLINK] Door1 자석 분리 -> 테이블 OPEN 빨간 배지 (Terminal->Server)
[DOWNLINK] Door1 CLOSE 버튼 -> 릴레이 제어 (Server->Terminal)
[UPLINK-PUSH] 온도 센서 입김 -> 그래프 상승 (WebSocket 자동 Push)
[UPLINK] Camera1 Motion YES -> 로그에 모션 감지

##  4. 보안 및 유지보수
TAPO_EMAIL/PASSWORD는 .env 파일로 관리, git에 커밋 금지

공유기 DHCP 고정 IP로 P115, Camera IP 고정

카메라 RTSP 비밀번호 주기적 변경

zigbee2mqtt permit_join: 페어링 후 false로 변경 (보안)

##  5. 모델별 요약
Device	프로토콜	최초 연결	ON/OFF	에너지 모니터링	FastAPI 연결

Tapo P115	Wi-Fi TCP	Tapo 앱 1회	O (앱+버튼+Python)	O (W/kWh)	DEVICE_IPS에 IP 등록

Zigbee Temp	Zigbee+MQTT	페어링 버튼	X	X (온습도)	MQTT subscribe

Zigbee Door	Zigbee+MQTT	페어링 버튼	X (상태만)	X	MQTT subscribe

Tapo C200	Wi-Fi RTSP	Tapo 앱 + RTSP 활성화	X	X	CAMERA_RTSP에 URL 등록

**작성자: IoT Gateway Project Team**
**문의: FastAPI 로그 확인 - http://localhost:8000/api/health**
FastAPI Server에 문의 창 설계 필요