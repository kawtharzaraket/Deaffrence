import json
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import joblib

# Load extracted landmarks
with open('datasets/wlasl_landmarks.json', 'r') as f:
    data = json.load(f)

X = []  # Features
y = []  # Labels

for item in data:
    # Each item['landmarks'] is a list of frames, each frame is a list of hand landmarks
    # We'll flatten all frames for each video into a single vector
    if not item['landmarks']:
        continue
    # Use only the first frame with detected hand for simplicity
    first_frame = item['landmarks'][0]
    # Flatten the list of [x, y, z] for all landmarks in the first frame
    flat = np.array(first_frame).flatten()
    X.append(flat)
    y.append(item['gloss'])

X = np.array(X)

# Train k-NN classifier
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X, y)

# Save the trained model
joblib.dump(knn, 'models/knn_sign_classifier.joblib')
print('k-NN classifier trained and saved to models/knn_sign_classifier.joblib')
