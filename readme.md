# AeroMinds - Real-Time 3D Scene Reconstruction

## Overview
This application allows users to upload top-view drone imagery and instantly visualize it as a 3D model. It uses a FastAPI backend with **Google's Gemini API (Nano Banana Pro)** for advanced 2D to 3D grayscale conversion and a Next.js frontend with React Three Fiber for 3D rendering.

## Prerequisites
- Python 3.8+
- Node.js 18+
- **Gemini API Key** - Get one from [Google AI Studio](https://aistudio.google.com/app/apikey) or [Nano Banana API](https://nanobananaapi.ai)

## How to Run

### 1. Configure API Key

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

Edit the `.env` file and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 2. Start the Backend
Open a terminal in the backend directory:

```bash
cd backend
# Create and activate virtual environment (if not already done)
python -m venv venv
.\venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Start the server
uvicorn main:app --reload
```

The backend will run on http://localhost:8000.

### 3. Start the Frontend
Open a new terminal in the frontend directory:

```bash
cd frontend
npm run dev
```

The frontend will run on http://localhost:3000.

## Usage Guide

1. Open your browser and navigate to http://localhost:3000
2. Click **Choose File** and select a top-down drone image (JPG/PNG)
3. Click **Generate 3D Model**
4. Wait for the Gemini API processing to complete
5. Interact with the 3D view:
   - **Left Click + Drag**: Rotate the view
   - **Right Click + Drag**: Pan the view
   - **Scroll**: Zoom in/out

## How It Works

1. **Image Upload**: User uploads a drone-captured image
2. **Gemini Processing**: The backend sends the image to Google's Gemini API with a prompt for 2D to 3D grayscale conversion
3. **Depth Map Generation**: Gemini generates a high-quality grayscale depth map where lighter areas represent closer surfaces
4. **3D Visualization**: The frontend uses the depth map as a displacement texture in Three.js to create the 3D effect

## Verification Results
✅ Backend starts and serves API endpoints  
✅ Gemini API integration with fallback processing  
✅ Frontend starts and renders UI  
✅ Image upload triggers Gemini API processing  
✅ 3D Viewer renders texture with depth displacement  

## Troubleshooting

### "Failed to fetch" or Network Error
If you encounter a network error when uploading:
- Ensure the backend is running (`uvicorn main:app --reload`)
- The frontend is configured to use http://127.0.0.1:8000 instead of localhost to avoid resolution issues on Windows
- Check the browser console (F12) for specific error messages

### API Key Issues
If you see "GEMINI_API_KEY not found":
- Make sure you created the `.env` file in the `backend` directory
- Verify your API key is correctly set in the `.env` file
- Restart the backend server after adding the API key

### Fallback Processing
If the Gemini API is unavailable or fails, the system automatically falls back to basic depth estimation using OpenCV to ensure continuous operation.

## Project Structure

```
aerominds/
├── backend/
│   ├── gemini_service.py    # Gemini API integration
│   ├── main.py               # FastAPI server
│   ├── .env                  # API key configuration (create from .env.example)
│   ├── requirements.txt      # Python dependencies
│   ├── uploads/              # Uploaded images
│   └── processed/            # Generated depth maps
└── frontend/
    ├── src/
    │   ├── app/
    │   │   └── page.jsx      # Main UI
    │   └── components/
    │       └── Viewer3D.jsx  # 3D renderer
    └── package.json
```