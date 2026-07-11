# Roadwatch (FastAPI edition)

A server-side port of the original single-file browser app. The original ran
object detection (TensorFlow.js `coco-ssd`) and all tracking/violation logic
entirely in the browser, and called Groq's API directly from client-side
JavaScript using a key typed into the page.

This version moves the heavy lifting to a FastAPI backend:

| Concern | Original (browser) | This version |
|---|---|---|
| Object detection | TensorFlow.js `coco-ssd` | YOLOv8n (`ultralytics`), server-side |
| Vehicle tracking | JS centroid tracker | Python centroid tracker (`app/tracker.py`) |
| Violation rules (stop line, wrong-way, no-parking, speed gates) | JS geometry checks | Ported 1:1 to Python (`app/violations.py`) |
| Traffic-light color sampling | `<canvas>` pixel sampling | OpenCV crop + pixel sampling |
| AI review (Groq vision) | Called directly from the browser with a user-supplied key | Called from the server using `GROQ_API_KEY`, key never reaches the browser |
| Frame transport | N/A (all local) | Browser captures JPEG frames and streams them to the server over a WebSocket (`/ws/track`) |

The browser still owns webcam/video capture, zone drawing (click-to-place
stop lines, direction arrows, no-parking rectangles, speed-gate pairs), and
rendering the overlay/violations list/telemetry — it just does so from JSON
the server sends back instead of computing it locally.

## Setup

### Windows (Python 3.13)

```powershell
py -3.13 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Notes specific to Windows + Python 3.13:

- `requirements.txt` uses version **floors** (`>=`) instead of exact pins, so
  pip resolves whatever current wheel actually supports your Python/OS
  combo, rather than an old pin that predates cp313 wheels. PyTorch (pulled
  in automatically by `ultralytics`), `opencv-python-headless`, and `numpy`
  all currently ship Windows wheels for Python 3.13.
- `uvicorn[standard]` normally includes `uvloop` for a faster event loop,
  but `uvloop` doesn't support Windows — pip skips it automatically via
  platform markers, so nothing to do; `uvicorn` falls back to the standard
  asyncio loop, which works fine here.
- If `pip install` tries to build anything from source instead of pulling a
  wheel, upgrade pip first (`python -m pip install --upgrade pip`) — that's
  almost always a stale-pip/wheel-resolution issue, not a real incompatibility.
- OpenCV wheels need the **Visual C++ 2015+ redistributable** (almost always
  already present on a modern Windows install); if `import cv2` fails with a
  `DLL load failed` error, install it from Microsoft's site.
- No GPU/CUDA setup is required — `ultralytics` will pull in a CPU build of
  PyTorch by default, which is enough for this app's detection workload.

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The first run (any OS) will download the YOLOv8n weights (~6MB) automatically
via `ultralytics`.

To enable AI review (violation confirm/dismiss, motorcycle helmet/overload
checks), set an environment variable before starting the server:

```bash
export GROQ_API_KEY=gsk_...       # Windows: set GROQ_API_KEY=gsk_...
```

Without it, the app still detects, tracks, and logs violations — they're
just marked "unverified" instead of AI-confirmed/dismissed.

## Run

```bash
uvicorn main:app --reload
```

Then open http://localhost:8000 — upload a traffic video or start your
webcam, draw zones the same way as before, and watch violations stream in.

## Project layout

```
main.py                 FastAPI app: routes + WebSocket handler
app/
  detector.py            YOLOv8 wrapper (replaces coco-ssd)
  tracker.py              Centroid tracker (ported from JS)
  violations.py            Zone geometry + violation rules + signal color
  groq_client.py            Server-side Groq vision API calls
  imaging.py                 base64 <-> OpenCV frame helpers, snapshot cropping
  session.py                  Per-connection orchestration (one Session per WS)
  models.py                    Pydantic request/response schemas
templates/index.html    Page shell (Jinja2)
static/style.css        Same visual design as the original
static/app.js           Capture loop, zone drawing UI, WebSocket client, rendering
```

## Notes / things you may want to change

- **State is in-memory per WebSocket connection.** Reconnecting (e.g. on a
  network hiccup) starts a fresh `Session`, so all track IDs and violation
  history reset. For production use you'd want to persist violations to a
  database (e.g. Postgres/SQLite via SQLAlchemy) as they're created in
  `Session._flag`/`Session._record_confirmed`.
- **One shared YOLO model, but detection is synchronous per request**,
  offloaded to a thread via `asyncio.to_thread` so it doesn't block the
  event loop. For higher throughput with multiple concurrent camera feeds,
  consider a small batching queue or running detection in a separate worker
  process.
- **`max_riders` is currently read from client settings for the main
  overload check, but the async Groq-driven `inspect_motorcycle` follow-up
  in `session.py` uses a hardcoded fallback of 2** — wire `settings` through
  if you want that to always match the UI's configured value.
- CORS isn't configured since the frontend is served by the same FastAPI app;
  add `fastapi.middleware.cors` if you split the frontend out.
