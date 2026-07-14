from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
import os
import uuid

from app.services.detector import track_video as run_yolo_video_tracking
from app.jobs import job_store
from app.utils.file_utils import save_uploaded_file
from app.services.websocket_manager import ws_manager

router = APIRouter()


def run_tracking_job(job_id: str, video_path: str, confidence_threshold: float) -> None:
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


@router.post("/track-video")
async def track_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    threshold: float = Form(0.25),
):
    filename = save_uploaded_file(file, ["video/"], "Only video files are supported")
    uploaded_path = os.path.join("uploads", filename) if not os.path.isabs(filename) else filename

    job_id = uuid.uuid4().hex
    job_store.create_job(job_id, filename)
    background_tasks.add_task(run_tracking_job, job_id, uploaded_path, threshold)

    return {"job_id": job_id}


@router.get("/tracking-status/{job_id}")
def get_tracking_status(job_id: str):
    job = job_store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Tracking job not found")

    return job


@router.websocket("/ws/tracking/{job_id}")
async def websocket_tracking(job_id: str, websocket: WebSocket):
    if job_store.get_job(job_id) is None:
        await websocket.close(code=1008)
        return

    await ws_manager.connect(job_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(job_id, websocket)
