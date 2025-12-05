Walkthrough - Real-Time 3D Scene Reconstruction
Overview
This application allows users to upload top-view drone imagery and instantly visualize it as a 3D model. It uses a FastAPI backend with MiDaS for depth estimation and a Next.js frontend with React Three Fiber for 3D rendering.

Prerequisites
Python 3.8+
Node.js 18+
How to Run
1. Start the Backend
Open a terminal in the backend directory:

cd backend
# Activate virtual environment
.\venv\Scripts\activate
# Start the server
uvicorn main:app --reload
The backend will run on http://localhost:8000. Note: The first run will download the MiDaS model (approx. 80MB).

2. Start the Frontend
Open a new terminal in the frontend directory:

cd frontend
npm run dev
The frontend will run on http://localhost:3000.

Usage Guide
Open your browser and navigate to http://localhost:3000.
Click Choose File and select a top-down drone image (JPG/PNG).
Click Generate 3D Model.
Wait for the processing to complete.
Interact with the 3D view:
Left Click + Drag: Rotate the view.
Right Click + Drag: Pan the view.
Scroll: Zoom in/out.
Verification Results
 Backend starts and serves API endpoints.
 Frontend starts and renders UI.
 Image upload triggers depth estimation.
 3D Viewer renders texture and displacement.
Troubleshooting
"Failed to fetch" or Network Error
If you encounter a network error when uploading:

Ensure the backend is running (uvicorn main:app --reload).
The frontend is configured to use http://127.0.0.1:8000 instead of localhost to avoid resolution issues on Windows.
Check the browser console (F12) for specific error messages.