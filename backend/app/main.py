import base64
from typing import Any, Dict
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from collections import deque

from .inference import run_inference, SEQ_LEN, FEATURE_SIZE
from .utils import PredictionSmoother, FPSCounter

app = FastAPI(title="ISL Gesture Web Backend")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "ISL Gesture API running"}


@app.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")

    seq_buffer = deque(maxlen=SEQ_LEN)
    smoother = PredictionSmoother(window_size=5, min_confidence=0.3)
    fps_counter = FPSCounter()

    try:
        while True:
            data: Dict[str, Any] = await websocket.receive_json()
            if data.get("type") != "frame":
                continue

            image_data = data.get("image")
            if not image_data:
                await websocket.send_json({
                    "type": "prediction",
                    "label": None,
                    "confidence": 0,
                    "landmarks": [],
                })
                continue

            # Decode base64 frame
            if "," in image_data:
                _, b64data = image_data.split(",", 1)
            else:
                b64data = image_data

            img_bytes = base64.b64decode(b64data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img_bgr is None:
                print("Decode failed")
                await websocket.send_json({
                    "type": "prediction",
                    "label": None,
                    "confidence": 0
                })
                continue

            # Predict gesture
            result = run_inference(img_bgr, seq_buffer)

            smoother.add(result["label"], result["confidence"])
            smooth_label, smooth_conf = smoother.get_smoothed()
            fps = fps_counter.tick()

            await websocket.send_json({
                "type": "prediction",
                "label": smooth_label,          # STRING label
                "confidence": float(smooth_conf),
                "fps": fps,
                "landmarks": []
            })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
