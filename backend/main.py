from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from gemini_service import GeminiService
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)

app.mount("/processed", StaticFiles(directory="processed"), name="processed")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialize service globally for now
gemini_service = None

@app.on_event("startup")
async def startup_event():
    global gemini_service
    gemini_service = GeminiService()

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process image using Gemini API for 3D grayscale conversion
    depth_map_path = gemini_service.process_image(file_location)
    
    return {
        "original_url": f"http://localhost:8000/{file_location}",
        "depth_map_url": f"http://localhost:8000/{depth_map_path}"
    }
