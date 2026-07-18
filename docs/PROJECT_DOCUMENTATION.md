# Aetheris — Project Documentation (generated)

## 1. Project Overview

- **Project name:** Aetheris
- **Purpose:** Vehicle detection and tracking platform using YOLOv8 with a React frontend and FastAPI backend. Provides image/video detection, background tracking jobs with live WebSocket updates, and simple upload/output storage.
- **Goals:** Offer a lightweight toolset for running vehicle detection and tracking on uploaded media, stream live tracking frames to clients, and provide training utilities for custom models.
- **Main Features:**
  - Image detection (annotated image output)
  - Video detection (annotated video output)
  - Background video tracking jobs with progress and WebSocket live frames
  - React frontend dashboard and pages for uploads and monitoring
  - Training utilities under `training/` to fine-tune models
- **Current Version Summary:** Implementation is present in the repo; core runtime relies on FastAPI backend and a Vite React frontend. No database or external auth is implemented.

---

## 2. Root Directory Structure

Top-level layout (selected folders):

Aetheris/
│
├── backend/ — FastAPI application and services (see [backend/main.py](backend/main.py#L1-L200))
├── frontend/ — React + Vite UI (entry: [frontend/src/main.tsx](frontend/src/main.tsx#L1-L20), [frontend/src/App.tsx](frontend/src/App.tsx#L1-L40))
├── training/ — Training/evaluation/export/infer utilities ([training/train.py](training/train.py#L1-L200))
├── dataset_tools/ — Dataset utilities and pipelines for organizing and extracting frames
├── models/ — Pretrained/custom model artifacts (pretrained: `models/pretrained/yolov8n.pt`; custom models may appear in `models/custom/`)
├── docs/ — documentation files (this file will be added here)
├── tests/ — test files (e.g., [backend/tests/test_main.py](backend/tests/test_main.py#L1-L80))

For each folder:
- backend/: Purpose — API server, services that run detection/tracking. Contents — `main.py`, `app/` package with `api/`, `services/`, `jobs/`, `utils/`. Dependencies — `fastapi`, `uvicorn`, `ultralytics`, `opencv-python`. Interaction — serves HTTP endpoints and WebSocket connections to frontend; loads models from `models/`.
- frontend/: Purpose — user interface built with React + Vite. Contents — `src/` with pages and components. Dependencies — `axios`, `react-router-dom`, UI primitives. Interaction — calls backend API at `http://127.0.0.1:8000` and connects to `/ws/tracking/{job_id}`.
- training/: Purpose — create and evaluate custom models and configs. Contents — `train.py`, `evaluate.py`, `configs/`. Interaction — generates artifacts in `models/custom/` used by backend via `MODEL_PATH`.
- dataset_tools/: Purpose — utilities for dataset creation, organizing, filtering. Interaction — optional pre-processing used before training.

---

## 3. Backend Documentation

- API entrypoint: [backend/main.py](backend/main.py#L1-L200)
- Framework: FastAPI

Key routers (in `backend/app/api/`):
- `detection` ([backend/app/api/detection.py](backend/app/api/detection.py#L1-L200)) — `POST /detect-image`, `POST /detect-video`.
- `tracking` ([backend/app/api/tracking.py](backend/app/api/tracking.py#L1-L200)) — `POST /track-video`, `GET /tracking-status/{job_id}`, WebSocket `/ws/tracking/{job_id}`.
- `upload` ([backend/app/api/upload.py](backend/app/api/upload.py#L1-L200)) — `POST /upload` delegates to image detection.

Services and important modules:
- `app.services.detector` ([backend/app/services/detector.py](backend/app/services/detector.py#L1-L200))
  - Purpose: Integrates with `ultralytics.YOLO` to run detection, video detection, and tracking (ByteTrack via model.track()).
  - Important functions: `detect_image()`, `detect_video()`, `track_video()`.
  - Model loading: `model = YOLO(MODEL_PATH)` where `MODEL_PATH` is resolved in `app.core.config`.
  - Outputs saved to `app/outputs` and transcoded to H.264 via `ffmpeg` if available.
- `app.services.websocket_manager` ([backend/app/services/websocket_manager.py](backend/app/services/websocket_manager.py#L1-L200))
  - Manages WebSocket connections by job id and broadcasts JSON frames from tracking jobs.
- `app.jobs.job_store` ([backend/app/jobs/job_store.py](backend/app/jobs/job_store.py#L1-L200))
  - In-memory job store with `create_job()`, `update_job()`, `get_job()`.

Utilities:
- `app.utils.file_utils` handles file validation and saving for uploads ([backend/app/utils/file_utils.py](backend/app/utils/file_utils.py#L1-L200)).
- `app.core.config` ([backend/app/core/config.py](backend/app/core/config.py#L1-L200)) defines `UPLOAD_DIR`, `OUTPUT_DIR`, `MODEL_PATH`, and ensures directories exist.

Authentication & Database:
- Not implemented. There is no evidence of database models, persistent storage, or authentication middleware. Jobs are stored in-memory (see `job_store`).

File uploads and storage:
- Uploaded files are placed under `backend/app/uploads` and outputs under `backend/app/outputs` (see `UPLOAD_DIR`, `OUTPUT_DIR` in config).

AI integration:
- Uses `ultralytics` YOLO API (`YOLO(MODEL_PATH)`) and ByteTrack through `model.track(..., tracker="bytetrack.yaml")` in `track_video()`.

Environment variables / config:
- `MODEL_PATH` may be set to override the active model; otherwise the most recent custom model in `models/custom/` or `models/pretrained/yolov8n.pt` is used.

---

## 4. Frontend Documentation

- Entry points: [frontend/src/main.tsx](frontend/src/main.tsx#L1-L20), [frontend/src/App.tsx](frontend/src/App.tsx#L1-L40)
- Routing: React Router with routes `/` (Landing), `/dashboard`, `/old-dashboard`.
- API integration: `frontend/src/services/api.ts` provides `detectImage()`, `detectVideo()`, `trackVideo()`, `getTrackingStatus()` and constructs WebSocket URL via `getTrackingSocketUrl()`.
- WebSocket handling: `frontend/src/hooks/useTrackingSocket.ts` implements automatic reconnect, state tracking, and exposes the latest message.
- State management: Local component state and hooks; no global store (e.g., Redux) present.
- UI libraries: Project uses custom UI primitives under `src/components/ui/` (buttons, cards, dialogs) — appears to be a tailor-made component set.

---

## 5. AI Module

- YOLO version: The code imports `from ultralytics import YOLO`. The repository includes `yolov8n.pt` at repository root (lightweight pretrained backbone). The specific ultralytics release is determined by the Python environment (see `requirements.txt` files).
- Training pipeline: `training/train.py` is present; training configs are under `training/configs/` (e.g., `barangay178.yaml`). Training uses Ultralytics training scripts (not fully inspected here). See [training/train.py](training/train.py#L1-L200).
- Dataset format: Not enforced by backend; dataset tooling is in `dataset_tools/` and looks to produce records and processing results (`dataset_tools/models/*.py`).
- Tracking: `track_video()` uses `model.track(..., tracker="bytetrack.yaml", persist=True)` — ByteTrack integration via Ultralytics.
- Detection pipeline: `detect_image()` and `detect_video()` call `model(...)` and filter by vehicle class ids defined in `VEHICLE_CLASSES` in `detector.py`.
- Inference flow: Backend endpoints accept multipart uploads, save via `file_utils.save_uploaded_file()`, call detector functions, write annotated outputs into `app/outputs`, and return metadata or annotated file URLs.

---

## 6. Dataset Documentation

- Dataset utilities are in `dataset_tools/` with modules for frame extraction, duplicate detection, blur detection, organizer, exporter, and metadata generation. See [dataset_tools/README.md](dataset_tools/README.md) and [dataset_tools/organizer.py](dataset_tools/dataset_organizer/organizer.py).
- No single `data.yaml` observed at repo root for YOLO training — training configs live under `training/configs/` as YAML files.
- Annotation format: Not standardized visibly in the backend. The training utilities likely expect Ultralytics/YOLOv8-compatible labels; check `training/configs/*` and dataset_tools exporter for specifics.

---

## 7. Database Documentation

- Not implemented. The project uses an in-memory `_jobs` dictionary in `backend/app/jobs/job_store.py` for job state. There are no persistent tables, ORMs, or external DB integrations found.

---

## 8. System Architecture

Sequence:

User → Frontend (React) → Backend (FastAPI) → YOLO inference/tracker → Filesystem storage (uploads/outputs)

- Frontend sends HTTP requests to `http://127.0.0.1:8000` (see [frontend/src/services/api.ts](frontend/src/services/api.ts#L1-L40)).
- For tracking jobs, frontend calls `POST /track-video` which returns `job_id`. Frontend polls `GET /tracking-status/{job_id}` and opens WebSocket `ws://localhost:8000/ws/tracking/{job_id}` to receive live frames and updates.
- Backend runs YOLO inference synchronously for image/video detection; tracking is run in a BackgroundTasks worker and streams frames via `WebSocketManager`.

---

## 9. Configuration Files

- Backend dependencies: [backend/requirements.txt](backend/requirements.txt#L1-L40) — includes `fastapi`, `uvicorn`, `ultralytics`, etc.
- Training deps: [training/requirements.txt](training/requirements.txt#L1-L40).
- Frontend: [frontend/package.json](frontend/package.json#L1-L80) — contains Vite + React dependencies.
- `app.core.config` determines `MODEL_PATH`, `UPLOAD_DIR`, `OUTPUT_DIR`. `MODEL_PATH` may be overridden by the `MODEL_PATH` environment variable.
- `yolov8` model files: `models/pretrained/yolov8n.pt` and potential custom weights in `models/custom/` (most-recent `*best.pt` selected automatically).
- Docker, docker-compose, CI: None found in repository root. If you need Docker or Actions, they are not present and must be added.

---

## 10. External Dependencies

- Backend: `fastapi` (API server), `uvicorn` (ASGI server), `ultralytics` (YOLO API), `opencv-python` (frame I/O and drawing), `ffmpeg` (optional, external binary for H.264 transcoding).
- Frontend: `react`, `react-dom`, `react-router-dom`, `axios`, `vite`.
- Dataset tools: `opencv-python`, `polars`/`pandas` (depends on environment).

Possible alternatives:
- For tracking: SORT, DeepSort, or other trackers instead of ByteTrack.
- For model serving: TorchServe or Triton for production-scale inference.

---

## 11. Current Features

- Image detection: `POST /detect-image` — implemented (files: [backend/app/api/detection.py](backend/app/api/detection.py#L1-L200), [backend/app/services/detector.py](backend/app/services/detector.py#L1-L200)). Status: Completed.
- Video detection: `POST /detect-video` — implemented. Status: Completed.
- Background tracking jobs: `POST /track-video`, job management and WebSocket updates — implemented (jobs stored in-memory). Status: Completed.
- Live WebSocket frame streaming: Implemented via `WebSocketManager`. Status: Completed.
- Frontend dashboard: Pages and components exist for monitoring and uploads. Status: Completed.

---

## 12. API Documentation

Base URL: `http://127.0.0.1:8000`

- GET `/` — health check. Response: `{ "message": "Backend is running" }` (see [backend/main.py](backend/main.py#L1-L40)).
- POST `/detect-image` — multipart form; fields: `file` (image), `threshold` (float). Response: `{ filename, image_url, total_vehicle_detections, vehicle_statistics, detections }`.
- POST `/detect-video` — multipart form; fields: `file` (video), `threshold`. Response: metadata about processed video including `video_url`.
- POST `/track-video` — starts background tracking job; returns `{ job_id }`.
- GET `/tracking-status/{job_id}` — returns job state JSON from `job_store`.
- WebSocket `/ws/tracking/{job_id}` — open WS to receive JSON messages with live frame base64, progress, and active tracks. Frontend helper: `getTrackingSocketUrl(jobId)` in [frontend/src/services/api.ts](frontend/src/services/api.ts#L1-L40).

Errors:
- 404 from `/tracking-status/{job_id}` if job not found.
- Upload validation raises `HTTPException` in `file_utils` when content type mismatches.

---

## 13. Training Documentation

- Training scripts: [training/train.py](training/train.py#L1-L200)
- Configs: [training/configs/](training/configs/) — example YAMLs like `barangay178.yaml`.
- Hyperparameters and optimizer: controlled by Ultralytics `train.py` invocation inside `training/train.py`. Inspect file for flags.
- Model export: `training/export.py` exists for exporting weights; inference script `training/infer.py` available.

---

## 14. Deployment

- Local: Run backend with `python -m backend.main` or `uvicorn main:app --reload` from `backend/`.
- Frontend: `npm install` then `npm run dev` inside `frontend/` (Vite). Ensure backend is reachable at `http://127.0.0.1:8000` or update `frontend/src/services/api.ts`.
- Docker: Not provided. CI/CD: Not provided.

---

## 15. Development Workflow

- Backend startup: `python -m main` in `backend/` or `uvicorn main:app --reload` (host/port configured in `main.py`).
- Frontend startup: `cd frontend && npm install && npm run dev`.
- Training: `python training/train.py` (see training docs).
- Testing: Backend has a simple test at [backend/tests/test_main.py](backend/tests/test_main.py#L1-L80). Run with `pytest` from repo root or `backend/`.

---

## 16. Changelog

This documentation is generated against the current repository snapshot. I did not compare to prior versions automatically — there are some phase notes under `copilot/phases/` documenting previous design choices (e.g., "Do not implement databases").

---

## 17. Missing Documentation & Improvements

- No database or authentication docs — explicitly not implemented.
- No Dockerfile or deployment manifests.
- Production considerations: persistent job storage, rate limiting, authentication, model versioning, GPU configuration and memory limits.
- Suggest adding `README.md` at repo root summarizing quickstart and environment setup steps.

---

## 18. Where to look in the code (quick links)

- Backend main: [backend/main.py](backend/main.py#L1-L200)
- Detector: [backend/app/services/detector.py](backend/app/services/detector.py#L1-L200)
- Config: [backend/app/core/config.py](backend/app/core/config.py#L1-L200)
- WebSocket manager: [backend/app/services/websocket_manager.py](backend/app/services/websocket_manager.py#L1-L200)
- Job store: [backend/app/jobs/job_store.py](backend/app/jobs/job_store.py#L1-L200)
- Frontend API client: [frontend/src/services/api.ts](frontend/src/services/api.ts#L1-L80)
- Frontend WebSocket hook: [frontend/src/hooks/useTrackingSocket.ts](frontend/src/hooks/useTrackingSocket.ts#L1-L200)

---

If you want, I can expand any section into a longer detailed reference (per-file API, full endpoint examples, or diagrams). Which section should I expand next?
