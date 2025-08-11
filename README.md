# Deafference MVP

A bidirectional sign language ↔ text translation application.

## Author
**Kawthar Zaraket**

## Features
- Sign language to text translation using hand landmark detection
- Real-time video recording and processing
- k-NN classifier for gesture recognition

## Tech Stack
- **Backend**: FastAPI, Python, MediaPipe, scikit-learn
- **Frontend**: React, Vite
- **ML**: OpenCV, MediaPipe hand landmarks, k-NN classification

## Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
npm install
npm run dev
```