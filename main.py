import cv2
import math
import joblib
import socket
import json
from collections import deque
from hand_utils import HandProcessor

model = joblib.load("hand_gesture_model.pkl")
processor = HandProcessor()

udp_ip = "127.0.0.1"
udp_port = 5051
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0)
prediction_history = deque(maxlen = 5)


while True:
    success, frame = cap.read()
    if not success or frame is None:
        continue
    
    frame = cv2.flip(frame, 1)

    frame, keypoints, hand_found, cursor_x, cursor_y = processor.process_frame(frame)
    smooth_prediction = 0
    
    if hand_found:
        prediction = model.predict([keypoints])[0]
        prediction_history.append(prediction)
        smooth_prediction = 1 if sum(prediction_history) >= 3 else 0
        
        if smooth_prediction == 1:
            cv2.putText(frame, "Pinch", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Open Hand", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        data_packet = {
            "gesture": int(smooth_prediction),
            "x": float(cursor_x),
            "y": float(cursor_y)
        }

        try:
            sock.sendto(json.dumps(data_packet).encode("utf-8"), (udp_ip, udp_port))
        except Exception:
            pass

    cv2.imshow("Test camera", frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    
cap.release()
cv2.destroyAllWindows()