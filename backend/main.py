from fastapi import FastAPI, File, HTTPException, UploadFile, Form, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid
import uvicorn

from app.services.detector import (
    detect_image as run_yolo_detection,
    detect_video as run_yolo_video_detection,
    track_video as run_yolo_video_tracking,
)
from app.services import job_store
from app.services.websocket_manager import ws_manager

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


def save_uploaded_file(file: UploadFile, allowed_prefixes: list[str], error_detail: str) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if not file.content_type or not any(file.content_type.startswith(prefix) for prefix in allowed_prefixes):
        raise HTTPException(status_code=400, detail=error_detail)

    extension = os.path.splitext(file.filename)[1] or ".bin"
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename


def run_tracking_job(job_id: str, video_path: str, confidence_threshold: float) -> None:
    """
    Background worker for a tracking job.

    Job lifecycle:
    1. queued   -> job created, waiting to start
    2. processing -> frames are being tracked
    3. completed -> output video is ready
    4. failed    -> an error stopped processing
    """
    job_store.update_job(job_id, status="processing")

    def on_progress(progress: dict) -> None:
        job_store.update_job(job_id, **progress)

    try:
        metadata, _output_path = run_yolo_video_tracking(
            video_path,
            confidence_threshold=confidence_threshold,
            job_id=job_id,
            on_progress=on_progress,
        )

        job_store.update_job(
            job_id,
            status="completed",
            progress_percentage=100.0,
            current_frame=metadata["total_frames"],
            total_frames=metadata["total_frames"],
            elapsed_processing_time=metadata["processing_time"],
            unique_tracked_vehicle_ids=metadata["tracked_vehicle_ids"],
            vehicle_statistics=metadata["vehicle_statistics"],
            video_url=metadata["video_url"],
            active_tracked_vehicles=[],
            active_tracked_vehicle_details=[],
        )
    except Exception as exc:
        job_store.update_job(job_id, status="failed", error=str(exc))


@app.post("/detect-image")
async def detect_image(file: UploadFile = File(...), threshold: float = Form(0.25)):
    """Accept an uploaded image and return annotated vehicle detections."""
    filename = save_uploaded_file(file, ["image/"], "Only image files are supported")
    uploaded_path = os.path.join(UPLOAD_DIR, filename)

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


@app.post("/detect-video")
async def detect_video(file: UploadFile = File(...), threshold: float = Form(0.25)):
    """Accept an uploaded video and return annotated vehicle statistics."""
    filename = save_uploaded_file(file, ["video/"], "Only video files are supported")
    uploaded_path = os.path.join(UPLOAD_DIR, filename)

    metadata, output_path = run_yolo_video_detection(uploaded_path, confidence_threshold=threshold)

    return metadata


@app.post("/track-video")
async def track_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    threshold: float = Form(0.25),
):
    """
    Accept an uploaded video and start background vehicle tracking.

    Returns a job ID immediately. Poll GET /tracking-status/{job_id} for progress.
    """
    filename = save_uploaded_file(file, ["video/"], "Only video files are supported")
    uploaded_path = os.path.join(UPLOAD_DIR, filename)

    job_id = uuid.uuid4().hex
    job_store.create_job(job_id, filename)
    background_tasks.add_task(run_tracking_job, job_id, uploaded_path, threshold)

    return {"job_id": job_id}


@app.get("/tracking-status/{job_id}")
def get_tracking_status(job_id: str):
    """Return live tracking progress and statistics for a background job."""
    job = job_store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Tracking job not found")

    return job


@app.websocket("/ws/tracking/{job_id}")
async def websocket_tracking(job_id: str, websocket: WebSocket):
    """Accept a WebSocket connection for live frame updates while a tracking job runs."""
    if job_store.get_job(job_id) is None:
        await websocket.close(code=1008)
        return

    await ws_manager.connect(job_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(job_id, websocket)


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
