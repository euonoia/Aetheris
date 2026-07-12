from fastapi import FastAPI, File, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid
import uvicorn

from app.services.detector import detect_image as run_yolo_detection

app = FastAPI(title="YOLO Vehicle Detector API")

# React Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "app", "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "app", "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


@app.get("/")
def root():
    return {"message": "Backend is running"}


def save_uploaded_image(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    extension = os.path.splitext(file.filename)[1] or ".bin"
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename


@app.post("/detect-image")
async def detect_image(file: UploadFile = File(...), threshold: float = Form(0.25)):
    """Endpoint accepts an image upload and an optional confidence `threshold` form field.

    The threshold defaults to 0.25 and is forwarded to the detector to filter vehicle detections.
    """
    filename = save_uploaded_image(file)

    uploaded_path = os.path.join(UPLOAD_DIR, filename)

    # Run detection with the provided confidence threshold
    detections, output_path = run_yolo_detection(uploaded_path, confidence_threshold=threshold)

    # Compute vehicle statistics
    vehicle_stats = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}
    for d in detections:
        key = d.get("class_name")
        if key in vehicle_stats:
            vehicle_stats[key] += 1

    total_vehicle_detections = sum(vehicle_stats.values())

    return {
        "filename": filename,
        "image_url": f"http://127.0.0.1:8000/outputs/{os.path.basename(output_path)}",
        "total_vehicle_detections": total_vehicle_detections,
        "vehicle_statistics": vehicle_stats,
        "detections": detections,
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return await detect_image(file)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )