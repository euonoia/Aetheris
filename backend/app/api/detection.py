from fastapi import APIRouter, File, Form, UploadFile, HTTPException
import os

from app.services.detector import (
    detect_image as run_yolo_detection,
    detect_video as run_yolo_video_detection,
)
from app.utils.file_utils import save_uploaded_file

router = APIRouter()


@router.post("/detect-image")
async def detect_image(file: UploadFile = File(...), threshold: float = Form(0.25)):
    filename = save_uploaded_file(file, ["image/"], "Only image files are supported")
    uploaded_path = os.path.join("uploads", filename) if not os.path.isabs(filename) else filename

    detections, output_path = run_yolo_detection(uploaded_path, confidence_threshold=threshold)

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


@router.post("/detect-video")
async def detect_video(file: UploadFile = File(...), threshold: float = Form(0.25)):
    filename = save_uploaded_file(file, ["video/"], "Only video files are supported")
    uploaded_path = filename

    metadata, output_path = run_yolo_video_detection(uploaded_path, confidence_threshold=threshold)

    return metadata
