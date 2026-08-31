import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

csv_file = "hand_gestures.csv"
df = pd.read_csv(csv_file)

print(f"Total data rows: {len(df)}")

x = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

print(f"The size of the x matrix: {x.shape}")
print(f"The size of the y matrix: {y.shape}")

model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(x_train, y_train)

y_pred = model.predict(x_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model accuracy: %{accuracy * 100:.2f}")

model_file = "hand_gesture_model.pkl"
joblib.dump(model, model_file)

