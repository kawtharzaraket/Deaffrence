from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import mediapipe as mp
import numpy as np
import cv2
import tempfile
import joblib
import os


# Load k-NN classifier
KNN_MODEL_PATH = os.path.join('..', 'models', 'knn_sign_classifier.joblib')
if os.path.exists(KNN_MODEL_PATH):
    knn = joblib.load(KNN_MODEL_PATH)
else:
    knn = None

app = FastAPI()
@app.post("/predict-gloss")
async def predict_gloss(file: UploadFile = File(...)):
    if knn is None:
        return {"error": "Classifier model not found. Train the model first."}
    # Save uploaded file to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    cap = cv2.VideoCapture(tmp_path)
    if not cap.isOpened():
        return {"error": "Could not open video file."}

    # Extract first frame with hand landmarks
    frame_landmarks = None
    with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                hand = []
                for lm in results.multi_hand_landmarks[0].landmark:
                    hand.append([lm.x, lm.y, lm.z])
                frame_landmarks = hand
                break  # Use only the first frame with a detected hand
    cap.release()

    if frame_landmarks is None:
        return {"result": "No hand detected"}

    # Flatten landmarks and predict
    flat = np.array(frame_landmarks).flatten().reshape(1, -1)
    gloss_pred = knn.predict(flat)[0]
    return {"result": {"gloss": gloss_pred}}

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Sign ↔ Text Translation API (MVP)"}


# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

@app.post("/sign-to-text")
async def sign_to_text(file: UploadFile = File(...)):
    # Save uploaded file to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Try to open as video
    cap = cv2.VideoCapture(tmp_path)
    if not cap.isOpened():
        return {"error": "Could not open video file."}

    frame_results = []
    frame_count = 0
    with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                hands_data = []
                for hand_landmarks in results.multi_hand_landmarks:
                    hand = []
                    for lm in hand_landmarks.landmark:
                        hand.append({'x': lm.x, 'y': lm.y, 'z': lm.z})
                    hands_data.append(hand)
                frame_results.append(hands_data)
            else:
                frame_results.append([])
    cap.release()

    # Simple rule: if any frame has a hand with y < 0.5, gloss = 'HELLO'
    gloss = 'NO_HAND_DETECTED'
    for hands_data in frame_results:
        if len(hands_data) > 0 and len(hands_data[0]) > 0:
            if hands_data[0][0]['y'] < 0.5:
                gloss = 'HELLO'
                break
            else:
                gloss = 'UNKNOWN'

    gloss_to_text = {'HELLO': 'Hello!', 'UNKNOWN': 'Unrecognized sign', 'NO_HAND_DETECTED': 'No hand detected'}
    text = gloss_to_text.get(gloss, 'No mapping found')
    return {"result": {"frames": len(frame_results), "gloss": gloss, "text": text}}

@app.post("/text-to-sign")
async def text_to_sign(text: str = Form(...)):
    # TODO: Generate sign language output from text using your ML model
    # Example: sign_output = model.generate(text)
    # For now, return a placeholder
    return {"result": f"[MVP] Received text: '{text}'. (Sign output coming soon)"}
