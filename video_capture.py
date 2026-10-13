import asyncio
import datetime
from random import random
from random import choice, randint
import bs4
import cv2
from dotenv import load_dotenv
import os

from fastapi import WebSocketDisconnect, WebSocket
from kasa import json

from server import STATE
load_dotenv()
def camera_play(url):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print("Failed to open camera")
        exit()
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        # automatically resize the frame to 640x360 for display
        frame = cv2.resize(frame, (640, 360))
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

async def websocket_bothway(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Simulate spontaneous UPLINK every 10 sec
            data = {
                "type": "UPLINK",
                "timestamp": datetime.datetime.now().isoformat(),
                "Temp1": {"temperature": round(22.5 + random.random()*3.5, 1)},
                "Camera1": {"motion": random.choice([True, False])},
                "Camera2": {"motion": random.choice([True, False])},
                "Switch1": {"power_w": random.randint(800,1500) if STATE["Switch1"]["state"]=="ON" else 0}
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        pass
if __name__ == "__main__":
    url = os.getenv("CAMERA1_RTSP", "")
    print(f"Using camera URL: {url}")
    camera_play(url)