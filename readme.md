## Zigbee vs Tapo, Both-Way 관점
```text
------------------------------------------------------------------------------------------------------------
구분             Zigbee (MQTT)                                      Tapo Wi-Fi (TCP)
------------------------------------------------------------------------------------------------------------
Both-Way 구현  MQTT publish/subscribe(브로커 필요)   TCP request/response + Push 로 직접 구현, 코드가 더 직관적

시연 시각화     zigbee2mqtt 로그 보기 애매      current_power가 0.1W 단위로 실시간으로 변해서 그래프 시연이 매우 화려함
```

## Tapo Wi-Fi로 가면 MCP Tool 3개로 Both-Way를 완벽하게 구현할 수 있습니다:

control_terminal : Server→Terminal
get_telemetry : Terminal→Server
subscribe_alarm : Terminal이 자발적으로 Server→Client로 Push
이 3개만 있으면 "양방향 데이터 통신을 갖는 IoT 게이트웨이" 라는 프로젝트 제목이 성립됩니다.


# Tapo Wi-Fi Both-Way 구조

```text
                        [FastMCP Server - PC]
                        / \
         (Downlink: Command) (Uplink: Telemetry)
        Server → Terminal Terminal → Server
              | |
     turn_on/off, schedule, power(W), voltage,
     child_lock, power_limit energy(kWh), overheat_alarm,
                                           on/off_status, wifi_rssi
                        \ /
                         [Tapo P115 Terminal]
```
# 시연용 DASH BOARD
```text
[Client] turn_on(192.168.0.123) ------> [Server] ------> [Tapo P115] ON (Downlink)

[Tapo P115] power=125.3W --------> [Server] --------> [Client] Chart Update (Uplink)

[Tapo P115] OVERHEAT! -----------> [Server] notify() ---> [Client] 🔥 알람 팝업 (Uplink Event)
```

# 테이블 구성
```text
Device	       Uplink(Terminal → Server)	 Status	      Downlink(Server → Terminal)
Temp Sensor	   온도/습도 실시간 그래프	        Normal	     - (Telemetry Only)
Door 1, 2	   Open/Close 상태	             배지로 표시	[OPEN] [CLOSE] 버튼 → 누르면 Status 즉시 변경
Light 1, 2	   ON/OFF + 전력(W)	             배지	       토글 스위치 → Server→Terminal 명령 시연
```

#  Both-Way 시연 방법:
```text
Door 1 [OPEN] 버튼 클릭 → 아래 로그에 [DOWNLINK] Server → Door1: OPEN → 0.3초 후 [UPLINK] Door1 → Server: OPENED ACK (양방향!)
Light 1 스위치 토글 → 전력 0W ↔️ 12W 변경 + 로그 Both-Way 표시
Temp 센서는 2초마다 자동으로 Uplink (Terminal→Server) 그래프 업데이트
tool 호출할 때마다 이 테이블이 실시간으로 업데이트 됨
```

# 이 화면에 모든 기초 기능이 들어가 있음:
```text
센서: Temp/Humidity 실시간 그래프 (Uplink)
Door 1/2: Open/Close 버튼 + 상태 배지 (Both-Way)
Light 1/2: 토글 스위치 + 전력 W
Smart Switch 1/2 (Tapo P115): ON/OFF + 에너지 kWh
Home Camera: 2채널 LIVE + 모션 감지 + 스냅샷
Both-Way 로그: 파란색=Downlink, 초록색=Uplink
```

#   mcp.json 설명
```text
"mcpServers": {
      "iot-gateway": {
        "command": "python",   # 서버 실행 명령
        "args": ["C:\\Users\\user2\\Desktop\\tapo-server\\server.py"], # 실행할 파일 경로
        "env": {
          "TAPO_EMAIL": "your_tapo@email.com",
          "TAPO_PASSWORD": "your_password"
        },  # 서버에 전달할 비밀키Tapo 계정 (코드에 하드코딩 금지)
        "transport": "stdio"  #통신 방식 stdio = Claude Desktop용, sse = 웹 대시보드용 (위 server.py는 sse:8000)
      }
    }
```
#   웹 대시보드(위 아티팩트)와 연결할 때:

대시보드는 http://localhost:8000/sse 로 FastMCP Server에 붙습니다.
버튼 클릭 → control_light Tool 호출 → Server가 Tapo/Zigbee로 Downlink → 결과가 Uplink로 다시 테이블 업데이트

## 다음 단계:

이 server.py를 PC에 저장
pip install fastmcp tapo python-kasa paho-mqtt 설치
python server.py 실행
위 대시보드 HTML을 브라우저로 열면 바로 Both-Way 제어 가능

## Run client program
```text
Invoke-Item .\Integrated-Iot-Control-Dashboard.html
```
OR
```text
start .\Integrated-Iot-Control-Dashboard.html
```