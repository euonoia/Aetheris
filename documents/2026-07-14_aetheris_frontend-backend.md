# Aetheris — Frontend & Backend Overview (2026-07-14)

## Summary
This document summarizes the frontend and backend responsibilities, key files, and integration points for the Aetheris project. It serves as a concise reference for developers who need to understand the architecture and typical workflows.

## Context
- Project name: Aetheris
- Date: 2026-07-14
- Feature/Task: Project architecture overview (frontend + backend)
- Type of change: Documentation

## Frontend Changes / Details
- Framework/library used: React, TypeScript, Vite
- Files/components affected:
  - frontend/src/App.tsx
  - frontend/src/pages/* (DashboardPage.tsx, Home.tsx, MonitoringPage.tsx)
  - frontend/src/components/* (VideoViewer.tsx, VideoPlayer.tsx, UploadCard.tsx, UploadArea.tsx, LiveFramePreview.tsx, DetectionTable.tsx)
  - frontend/src/hooks/* (useTrackingJob.ts, useTrackingSocket.ts)
  - frontend/src/services/api.ts
- What changed / responsibilities:
  - Provides UI for uploads, job monitoring, live previews, and results.
  - Manages API calls to backend and WebSocket connections for real-time updates.
  - Uses TypeScript types in `frontend/src/types` to model API responses and tracking data.

## Backend Changes / Details
- Language/framework used: Python (Flask-style application)
- Files/modules affected:
  - backend/main.py
  - backend/app/api/*.py (detection.py, tracking.py, upload.py)
  - backend/app/services/* (detector.py, websocket_manager.py, job_store.py)
  - backend/app/core/config.py
  - backend/app/jobs/*
- What changed / responsibilities:
  - Exposes REST endpoints for uploads, detection, and tracking control.
  - Executes YOLO-based detection (`yolov8n.pt` present) and tracking jobs.
  - Stores job metadata and outputs under `backend/app/jobs` and `backend/outputs`.
  - Emits progress and results via WebSockets to connected frontend clients.

## API Reference (summary)
| Method | Endpoint | Description | Request | Response |
|---|---:|---|---|---|
| POST | `/api/upload` | Upload media for processing | multipart/form-data (file) | job id, status |
| POST | `/api/detect` | Start detection on uploaded media | JSON (job options) | job id, queued |
| POST | `/api/track` | Start tracking job | JSON (job id, params) | job id, status |
| GET  | `/api/jobs/{id}` | Get job status/results | - | job metadata, progress, result URLs |

(Refer to `backend/app/api` for exact routes and payload shapes.)

## Database / Storage
- No external DB required by default; jobs and outputs are stored on disk under `backend/app/jobs` and `backend/outputs`.
- If configured, a job store service can be adapted to persist to a database (see `backend/app/services/job_store.py`).

## Testing
- How this was tested:
  - Manual local runs: `python main.py` to start backend; `npm run dev` in `frontend` to start frontend.
  - Unit tests location: `backend/tests/` contains test files (e.g., `test_main.py`).
- Known issues or edge cases: None recorded here; consult `backend/tests` and runtime logs for more details.

## Known Issues / TODOs
- Add explicit API payload examples and status codes to the API Reference.
- Document WebSocket message formats produced by the backend.

## Related Files
- frontend/src/App.tsx
- frontend/src/services/api.ts
- frontend/src/hooks/useTrackingSocket.ts
- backend/main.py
- backend/app/api/detection.py
- backend/app/services/detector.py

## How to Run (local)

Backend:

```bash
cd backend
python main.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

---

Generated from the provided documentation template and the current workspace layout. Save this file under `documents` for future reference.
