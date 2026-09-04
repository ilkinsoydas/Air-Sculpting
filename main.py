import cv2
import math
import socket
import json
from hand_utils import HandProcessor
import numpy as np
from tensorflow.keras.models import load_model

model = load_model("action.keras")
actions = np.array(["Extrude", "Rotate", "Idle", "Pinch"])

sequence = []
threshold = 0.6

processor = HandProcessor()

udp_ip = "127.0.0.1"
udp_port = 5051
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0)


while True:
    success, frame = cap.read()
    if not success or frame is None:
        continue
    
    frame = cv2.flip(frame, 1)

    frame, keypoints, hand_found, cursor_x, cursor_y = processor.process_frame(frame)
    smooth_prediction = 0
    
    if hand_found and keypoints is not None:
        sequence.append(keypoints)
        sequence = sequence[-30:]
        
        if len(sequence) == 30:
            input_data = np.expand_dims(sequence, axis = 0)
            res = model(input_data, training = False)[0].numpy()
            
            if res[np.argmax(res)] > threshold:
                action_name = actions[np.argmax(res)]
                confidence = res[np.argmax(res)] * 100
                
                text = f"{action_name}:  ({confidence: .1f}%)"
                cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                
                data_packet = {
                    "gesture": action_name,
                    "x": float(cursor_x),
                    "y": float(cursor_y)
                }
                
                try:
                    sock.sendto(json.dumps(data_packet).encode("utf-8"), (udp_ip, udp_port))
                except Exception:
                    pass
    else:
        sequence = []

    cv2.imshow("Test camera", frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    
cap.release()
cv2.destroyAllWindows()