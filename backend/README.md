# FastAPI Backend for Sign ↔ Text Translation MVP

## Setup
1. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
2. Install dependencies:
   ```sh
   pip install fastapi uvicorn mediapipe
   ```
3. Run the server:
   ```sh
   uvicorn main:app --reload
   ```

## Endpoints
- `/` — Health check
- (To be added) `/sign-to-text` — Sign video to text
- (To be added) `/text-to-sign` — Text to sign animation

---
Add your ML/model code in the `models/` folder.
