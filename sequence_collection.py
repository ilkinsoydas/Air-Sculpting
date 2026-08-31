import cv2
import numpy as np
import os
from hand_utils import HandProcessor

actions = np.array(["Extrude", "Rotate"])

no_sequences = 30
sequence_length = 30

data_path = os.path.join("MP_Data")

for action in actions:
    for sequence in range(no_sequences):
        try:
            os.makedirs(os.path.join(data_path, action, str(sequence)))
        except:
            pass
        
print("Starting data collection.")

processor = HandProcessor()
cap = cv2.VideoCapture(0)

for action in actions:
    for sequence in range(no_sequences):
        for frame_num in range(sequence_length):
            success, frame = cap.read()
            if not success: 
                break
            
            frame = cv2.flip(frame, 1)
            
            frame, keypoints, hand_found, _, _ = processor.process_frame(frame)
            
            if frame_num == 0:
                for _ in range(20):
                    cv2.putText(frame, f"Starting: {action}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 3)
                    cv2.imshow("Data Collection", frame)
                    if cv2.waitKey(100) & 0xFF == ord("q") :
                        cap.release()
                        cv2.destroyAllWindows()
                        break

            cv2.imshow("Data Collection", frame)

            npy_path = os.path.join(data_path, action, str(sequence), str(frame_num))
            np.save(npy_path, keypoints)
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            
cap.release()
cv2.destroyAllWindows()