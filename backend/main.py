from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from ultralytics import YOLO
from PIL import Image
import io
import base64
import json
import uuid
from pathlib import Path

import cv2
import numpy as np
import uvicorn

from violations.parking_tracker import ParkingViolationTracker, VEHICLE_CLASS_IDS

app = FastAPI(title="YOLOv8 Detection API")

# Allow the Vite dev server to call this API.
# Add your production frontend origin here too once deployed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loaded once at startup, reused for every request.
# Swap "yolov8n.pt" for yolov8s/m/l/x.pt, or the path to your own trained weights.
model = YOLO("yolov8n.pt")

# Where annotated violation videos get written so they can be downloaded/streamed back.
JOB_OUTPUT_DIR = Path(__file__).parent / "job_outputs"
JOB_OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {"status": "YOLOv8 API running", "model": model.model_name if hasattr(model, "model_name") else "yolov8n"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()

    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file")

    results = model.predict(source=np.array(image), conf=0.25, verbose=False)
    result = results[0]

    detections = []
    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        detections.append(
            {
                "class": model.names[int(box.cls[0])],
                "confidence": round(float(box.conf[0]), 4),
                "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            }
        )

    # result.plot() draws boxes/labels onto the image (returns BGR numpy array)
    annotated = result.plot()
    annotated_rgb = annotated[:, :, ::-1]
    annotated_img = Image.fromarray(annotated_rgb)

    buf = io.BytesIO()
    annotated_img.save(buf, format="JPEG", quality=90)
    annotated_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return JSONResponse(
        {
            "detections": detections,
            "annotated_image": f"data:image/jpeg;base64,{annotated_b64}",
            "image_size": {"width": image.width, "height": image.height},
        }
    )


# ---------------------------------------------------------------------------
# Illegal parking: upload a video + a no-parking zone polygon, get back an
# annotated video plus a list of violation events.
# ---------------------------------------------------------------------------


@app.post("/violations/parking/video")
async def detect_illegal_parking_video(
    file: UploadFile = File(...),
    zone: str = Form(...),  # JSON string: [[x1,y1],[x2,y2],[x3,y3], ...] in original video pixel coords
    dwell_seconds: float = Form(10.0),
):
    try:
        raw_points = json.loads(zone)
        zone_points = [(float(p[0]), float(p[1])) for p in raw_points]
    except Exception:
        raise HTTPException(status_code=400, detail="Zone must be a JSON array of [x, y] points")

    if len(zone_points) < 3:
        raise HTTPException(status_code=400, detail="Zone needs at least 3 points")

    job_id = uuid.uuid4().hex[:10]
    in_path = JOB_OUTPUT_DIR / f"{job_id}_in.mp4"
    out_path = JOB_OUTPUT_DIR / f"{job_id}_annotated.mp4"

    with open(in_path, "wb") as f:
        f.write(await file.read())

    cap = cv2.VideoCapture(str(in_path))
    if not cap.isOpened():
        in_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Could not open video file")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))

    tracker = ParkingViolationTracker(zone=zone_points, dwell_seconds=dwell_seconds)
    zone_np = np.array(zone_points, dtype=np.int32)

    all_violations = []
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        timestamp = frame_idx / fps

        results = model.track(
            frame,
            persist=True,
            classes=list(VEHICLE_CLASS_IDS),
            conf=0.3,
            verbose=False,
            tracker="bytetrack.yaml",
        )
        result = results[0]

        detections = []
        if result.boxes is not None and result.boxes.id is not None:
            for box, tid, cls in zip(result.boxes.xyxy, result.boxes.id, result.boxes.cls):
                x1, y1, x2, y2 = box.tolist()
                center = ((x1 + x2) / 2, (y1 + y2) / 2)
                detections.append(
                    {
                        "track_id": int(tid),
                        "class": model.names[int(cls)],
                        "box": (x1, y1, x2, y2),
                        "center": center,
                    }
                )

        new_violations = tracker.update(
            [{"track_id": d["track_id"], "class": d["class"], "center": d["center"]} for d in detections],
            timestamp,
        )
        for v in new_violations:
            v["frame"] = frame_idx
            all_violations.append(v)

        # Draw the zone outline.
        cv2.polylines(frame, [zone_np], isClosed=True, color=(0, 200, 255), thickness=2)

        violating_ids = tracker.violating_ids()
        for d in detections:
            x1, y1, x2, y2 = [int(v) for v in d["box"]]
            is_violating = d["track_id"] in violating_ids
            color = (0, 0, 255) if is_violating else (80, 220, 80)
            label = f"{d['class']} #{d['track_id']}"
            if is_violating:
                label += " ILLEGAL PARKING"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, max(y1 - 8, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        writer.write(frame)
        frame_idx += 1

    cap.release()
    writer.release()
    in_path.unlink(missing_ok=True)

    return JSONResponse(
        {
            "job_id": job_id,
            "violations": all_violations,
            "video_url": f"/violations/video/{job_id}",
            "fps": fps,
            "frame_count": frame_idx,
        }
    )


@app.get("/violations/video/{job_id}")
def get_annotated_video(job_id: str):
    path = JOB_OUTPUT_DIR / f"{job_id}_annotated.mp4"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Video not found or already cleaned up")
    return FileResponse(str(path), media_type="video/mp4")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)