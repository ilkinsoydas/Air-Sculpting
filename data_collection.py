import cv2
import mediapipe as mp  
import csv
import os
import math

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands = 1, min_detection_confidence  = 0.7)

csv_file = "hand_gestures.csv"

if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        header = []
        for i in range(21):
            header.extend([f"x{i}", f"y{i}"])
            
        header.append("label")
        writer.writerow(header)
        
print("Starting data collection.")

cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break
    
    frame = cv2.flip(frame, 1)
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            base_x = hand_landmarks.landmark[0].x
            base_y = hand_landmarks.landmark[0].y
            
            middle_mcp_x = hand_landmarks.landmark[9].x
            middle_mcp_y = hand_landmarks.landmark[9].y
            
            hand_size = math.sqrt((middle_mcp_x - base_x)**2 + (middle_mcp_y - base_y)**2)

            row_data = []
            for landmark in hand_landmarks.landmark:
                scale_x = (landmark.x - base_x) / (hand_size if hand_size > 0 else 1)
                scale_y = (landmark.y - base_y) / (hand_size if hand_size > 0 else 1)

                row_data.append(scale_x)
                row_data.append(scale_y)

            print(f"Total landmarks: {len(row_data)}")
    
    cv2.imshow("Data Collection", frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord("1"):
        row_data.append(1)
        
        with open(csv_file, mode = "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row_data)
            print("Pinch")
    
    elif key == ord("0"):
        row_data.append(0)
        
        with open(csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row_data)
            print("Open hand")
    
    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()