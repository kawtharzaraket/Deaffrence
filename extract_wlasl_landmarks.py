import mediapipe as mp
import cv2
import json
import os

# List of glosses to extract
GLOSSES = ['hello', 'eat', 'thank you']

# Path to WLASL annotation file and videos folder
ANNOTATION_PATH = 'datasets/WLASL_v0.3.json'
VIDEOS_DIR = 'datasets/WLASL_videos/'
OUTPUT_PATH = 'datasets/wlasl_landmarks.json'

mp_hands = mp.solutions.hands

# Load WLASL annotation
with open(ANNOTATION_PATH, 'r') as f:
    annotations = json.load(f)

# Filter videos for selected glosses
selected_videos = []
for entry in annotations:
    gloss = entry['gloss'].lower()
    if gloss in GLOSSES:
        for idx, instance in enumerate(entry['instances']):
            selected_videos.append({
                'gloss': gloss,
                'idx': idx,
                'url': instance.get('url')
            })

# Extract landmarks for each video
results = []
for vid in selected_videos:
    video_path = os.path.join(VIDEOS_DIR, f"{vid['gloss']}_{vid['idx']}.mp4")
    if not os.path.exists(video_path):
        continue
    cap = cv2.VideoCapture(video_path)
    video_landmarks = []
    with mp_hands.Hands(static_image_mode=False) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results_mp = hands.process(frame_rgb)
            if results_mp.multi_hand_landmarks:
                hand = []
                for lm in results_mp.multi_hand_landmarks[0].landmark:
                    hand.append([lm.x, lm.y, lm.z])
                video_landmarks.append(hand)
    cap.release()
    results.append({
        'gloss': vid['gloss'],
        'video_file': f"{vid['gloss']}_{vid['idx']}.mp4",
        'landmarks': video_landmarks
    })

# Save extracted landmarks
with open(OUTPUT_PATH, 'w') as f:
    json.dump(results, f)

print(f"Extracted landmarks for {len(results)} videos.")
