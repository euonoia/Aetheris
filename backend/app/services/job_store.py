import threading
from typing import Any

# In-memory store for tracking jobs.
# Each job moves through: queued -> processing -> completed (or failed).
_jobs: dict[str, dict[str, Any]] = {}
_lock = threading.Lock()

DEFAULT_VEHICLE_STATS = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}


def create_job(job_id: str, filename: str) -> None:
    """Register a new tracking job in queued state."""
    with _lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "filename": filename,
            "status": "queued",
            "progress_percentage": 0.0,
            "current_frame": 0,
            "total_frames": 0,
            "elapsed_processing_time": 0.0,
            "processing_fps": 0.0,
            "active_tracked_vehicles": [],
            "active_tracked_vehicle_details": [],
            "unique_tracked_vehicle_ids": [],
            "vehicle_statistics": DEFAULT_VEHICLE_STATS.copy(),
            "video_url": None,
            "error": None,
        }


def update_job(job_id: str, **fields: Any) -> None:
    """Update one or more fields on an existing job."""
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(fields)


def get_job(job_id: str) -> dict[str, Any] | None:
    """Return a snapshot of the current job state."""
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        return job.copy()
