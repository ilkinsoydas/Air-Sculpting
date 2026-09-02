import pandas as pd
import numpy as np
import os

label_map = {0: "Idle", 1: "Pinch"}
data_path = os.path.join("MP_Data")
sequence_length = 30
df = pd.read_csv("hand_gestures.csv")

for numeric_label, action_name in label_map.items():
    action_data = df[df["label"] == numeric_label].drop("label", axis=1).values
    
    action_path = os.path.join(data_path, action_name)
    os.makedirs(action_path, exist_ok=True)
    
    for sequence_id, row in enumerate(action_data):
        video_sequence = np.tile(row, (sequence_length, 1))
        npy_path = os.path.join(action_path, str(sequence_id))
        np.save(npy_path, video_sequence)

    print(f"Done: Created {len(action_data)} sequences of 30-frame .npy files for the '{action_name}' gesture.")