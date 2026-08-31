import numpy as np
import os
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

actions = np.array(["Extrude", "Rotate"])
no_sequences = 30
sequence_length = 30

data_path = os.path.join("MP_Data")

label_map = {label: num for num, label in enumerate(actions)}

sequences, labels = [], []

for action in actions:
    for sequence in range(no_sequences):
        window = []
        for frame_num in range(sequence_length):
            res = np.load(os.path.join(data_path, action, str(sequence), f"{frame_num}.npy"))
            window.append(res)
        sequences.append(window)
        labels.append(label_map[action])
x = np.array(sequences)
y = to_categorical(labels).astype(int)

print(f"x shape: {x.shape}, y shape: {y.shape}")

model = Sequential()
model.add(LSTM(64, return_sequences = True, activation = "relu", input_shape = (30,42)))
model.add(LSTM(128, return_sequences = False, activation = "relu"))
model.add(Dense(64, activation = "relu"))
model.add(Dense(actions.shape[0], activation = "softmax"))

model.compile(optimizer = "Adam", loss = "categorical_crossentropy", metrics = ["categorical_accuracy"])
model.fit(x, y, epochs = 50)

model.save("action.keras")


