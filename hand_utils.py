import cv2
import mediapipe as mp
import math
import numpy as np

class HandProcessor:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(max_num_hands = 2, min_detection_confidence = 0.7)
    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        keypoints = np.zeros(42)
        hand_found = False
        cursor_x, cursor_y = 0.5, 0.5
        
        if results.multi_hand_landmarks:
            hand_found = True
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                cursor_x = hand_landmarks.landmark[8].x
                cursor_y = hand_landmarks.landmark[8].y
    
                base_x = hand_landmarks.landmark[0].x
                base_y = hand_landmarks.landmark[0].y
                middle_mcp_x = hand_landmarks.landmark[9].x
                middle_mcp_y = hand_landmarks.landmark[9].y
                
                hand_size = math.sqrt((middle_mcp_x - base_x)**2 + (middle_mcp_y - base_y)**2)
                hand_size = hand_size if hand_size > 0 else 1.0
                
                row_data = []
                for lm in hand_landmarks.landmark:
                    row_data.append((lm.x - base_x) / hand_size)
                    row_data.append((lm.y - base_y) / hand_size)

                keypoints = np.array(row_data)
        return frame, keypoints, hand_found, cursor_x, cursor_y