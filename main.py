import cv2
import math
import json
from core.hand_utils import HandProcessor
import numpy as np
from tensorflow.keras.models import load_model
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

model = load_model("action.keras")
actions = np.array(["Extrude", "Rotate", "Idle", "Pinch", "Fist"])

sequence = []
threshold = 0.80

processor = HandProcessor()

cap = cv2.VideoCapture(0)

@app.websocket("/ws")
async def process_camera(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")
    sequence = [] 
    predictions_history = []
    
    try:
        while True:
            success, frame = cap.read()
            if not success or frame is None:
                await asyncio.sleep(0.1)
                continue
            frame = cv2.flip(frame, 1)
            
            frame, keypoints, hand_found, cursor_x, cursor_y, pinch_distance = processor.process_frame(frame)
            
            if hand_found and keypoints is not None:
                sequence.append(keypoints)
                sequence = sequence[-30:]
                
                if len(sequence) == 30:
                    input_data = np.expand_dims(sequence, axis=0)
                    res = model(input_data, training = False)[0].numpy()
                    
                    if res[np.argmax(res)] > threshold:
                        action_name = actions[np.argmax(res)]
                        confidence = res[np.argmax(res)] * 100

                        predictions_history.append(action_name)
                        predictions_history = predictions_history[-5:]

                        if predictions_history.count(action_name) == 5:
                            final_gesture = action_name

                        else:
                            final_gesture = "Idle"
                        
                        text = f"FILTERED: {final_gesture}"
                        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 2, cv2.LINE_AA)
                        
                        data_packet = {
                            "gesture": final_gesture,
                            "x": float(cursor_x),
                            "y": float(cursor_y),
                            "pinch_distance": float(pinch_distance)
                        }
                        
                        await websocket.send_json(data_packet)
            else:
                sequence = []
            
            cv2.imshow("Test camera", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        print("WebSocket connection closed")
       
