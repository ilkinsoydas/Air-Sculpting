import cv2
import numpy as np
from tensorflow.keras.models import load_model
from hand_utils import HandProcessor

model = load_model("action.keras")
actions = np.array(["Extrude", "Rotate", "Idle", "Pinch"])
processor = HandProcessor()

sequence = []
predictions = []
threshold = 0.6

cap = cv2.VideoCapture(0)
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Camera not found")
        break
    frame = cv2.flip(frame, 1)

    processed_frame, keypoints, hand_found, _, _ = processor.process_frame(frame)

    if hand_found and keypoints is not None:
        sequence.append(keypoints)
        sequence = sequence[-30:]
        
        if len(sequence) == 30:
            input_data = np.expand_dims(sequence, axis=0)
            res = model(input_data, training = False)[0].numpy()
            if res[np.argmax(res)] > threshold:
                action_name = actions[np.argmax(res)]
                confidence = res[np.argmax(res)] * 100
                
                text = f"{action_name}: ({confidence:.1f}%)"
                cv2.putText(processed_frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        sequence = []
        
    cv2.imshow("Real-time Action Recognition", processed_frame)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()