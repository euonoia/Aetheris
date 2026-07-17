from ultralytics import YOLO
import base64
import cv2
import os
import shutil
import subprocess
import time

from app.services.websocket_manager import ws_manager
from app.core.config import MODEL_PATH, OUTPUT_DIR, ensure_model_dirs

# Ensure model directories exist (creates models/pretrained and models/custom)
ensure_model_dirs()

# Load the model from configurable path. This allows swapping models without
# editing detector code or changing API endpoints.
model = YOLO(MODEL_PATH)

VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


def build_vehicle_statistics(track_id_to_class: dict[int, str]) -> dict[str, int]:
    """Count unique tracked vehicles per class."""
    vehicle_stats = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}
    for class_name in track_id_to_class.values():
        vehicle_stats[class_name] += 1
    return vehicle_stats


def transcode_to_h264(input_path: str) -> str:
    """
    Re-encode an OpenCV-written MP4 (mp4v/MPEG-4 Part 2) into H.264 so it
    plays back in browsers via <video> tags.

    Why this is needed:
    - cv2.VideoWriter with the 'mp4v' fourcc produces a valid MP4 container,
      but the video stream inside it is MPEG-4 Part 2, which desktop players
      like VLC decode fine but Chrome/Firefox/Safari do not support.
    - '-movflags +faststart' moves the moov atom (metadata index) to the
      front of the file so browsers can start playback before the whole
      file has downloaded.

    On failure, returns the original input_path unchanged so callers can
    still serve *something* rather than crash the whole job.
    """
    root, _ext = os.path.splitext(input_path)
    output_path = f"{root}_h264.mp4"

    if shutil.which("ffmpeg") is None:
        # Loud warning instead of a silent fallback -- if you're seeing the
        # "still corrupted" browser playback issue and this prints, ffmpeg
        # is the cause: it's not installed or not on PATH for this process.
        print(
            "[transcode_to_h264] WARNING: ffmpeg not found on PATH. "
            "Serving the raw mp4v file, which browsers cannot play. "
            "Install ffmpeg and make sure it's on PATH, then retry."
        )
        return input_path

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", input_path,
                "-vcodec", "libx264",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                output_path,
            ],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        # FileNotFoundError -> ffmpeg isn't installed / not on PATH.
        # CalledProcessError -> ffmpeg ran but failed (bad input, etc).
        print(f"[transcode_to_h264] Falling back to original file: {exc}")
        return input_path

    # Replace the intermediate mp4v file with the browser-friendly one so we
    # don't leave two copies of every video sitting in outputs/.
    try:
        os.remove(input_path)
    except OSError:
        pass

    return output_path


def detect_image(image_path: str, confidence_threshold: float = 0.25):
    """Run YOLO on `image_path` and return detections filtered by vehicle classes."""
    results = model(image_path)
    result = results[0]

    detections = []
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        if class_id not in VEHICLE_CLASSES or confidence < float(confidence_threshold):
            continue

        detections.append({
            "class_id": class_id,
            "class_name": VEHICLE_CLASSES[class_id],
            "confidence": round(confidence, 2),
            "bounding_box": [int(x) for x in box.xyxy[0].tolist()],
        })

    original_name = os.path.basename(image_path)
    name, ext = os.path.splitext(original_name)
    output_filename = f"{name}_detected{ext}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    result.save(filename=output_path)

    return detections, output_path


def draw_bounding_boxes(frame, detections):
    """Draw bounding boxes and labels for vehicle detections on a frame."""
    for x1, y1, x2, y2, confidence, class_id in detections:
        class_name = VEHICLE_CLASSES[int(class_id)]
        label = f"{class_name} {confidence:.2f}"
        color = (0, 255, 0)

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(
            frame,
            label,
            (int(x1), max(int(y1) - 10, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
            lineType=cv2.LINE_AA,
        )

    return frame


def detect_video(video_path: str, confidence_threshold: float = 0.25):
    """Run YOLO on each frame of a video and save an annotated output video."""
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise ValueError("Cannot open uploaded video file")

    writer = None
    try:
        fps = capture.get(cv2.CAP_PROP_FPS) or 25.0

        # Read the first frame BEFORE creating the writer, and size the
        # writer off the actual decoded frame array (frame.shape), not off
        # capture.get(CAP_PROP_FRAME_WIDTH/HEIGHT). Those metadata fields can
        # disagree with the real decoded dimensions -- most commonly on
        # phone/CCTV footage carrying a 90-degree rotation flag -- and any
        # such mismatch corrupts every subsequent writer.write() call.
        success, first_frame = capture.read()
        if not success:
            raise ValueError("Uploaded video contains no readable frames")

        frame_height, frame_width = first_frame.shape[:2]

        original_name = os.path.basename(video_path)
        name, _ = os.path.splitext(original_name)
        output_filename = f"{name}_detected.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        if not writer.isOpened():
            raise ValueError("Cannot initialize video writer for output MP4")

        total_vehicle_detections = 0
        vehicle_stats = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}
        frame_index = 0
        start_time = time.time()
        frame = first_frame

        while frame is not None:
            frame_index += 1

            # Defensive guard: if any decoded frame doesn't match the size
            # the writer was opened with, resize it rather than letting
            # writer.write() silently write a malformed frame into the file.
            h, w = frame.shape[:2]
            if (w, h) != (frame_width, frame_height):
                frame = cv2.resize(frame, (frame_width, frame_height))

            results = model(frame)
            result = results[0]

            detections = []
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                if class_id not in VEHICLE_CLASSES or confidence < float(confidence_threshold):
                    continue

                detections.append([*box.xyxy[0].tolist(), confidence, class_id])

            total_vehicle_detections += len(detections)
            for det in detections:
                vehicle_stats[VEHICLE_CLASSES[int(det[5])]] += 1

            if detections:
                frame = draw_bounding_boxes(frame, detections)

            writer.write(frame)

            success, frame = capture.read()
            if not success:
                frame = None
    finally:
        capture.release()
        if writer is not None:
            writer.release()

    processing_time = round(time.time() - start_time, 2)

    # Re-encode to H.264 so the output plays back in <video> tags in browsers.
    final_output_path = transcode_to_h264(output_path)
    final_output_filename = os.path.basename(final_output_path)

    metadata = {
        "filename": original_name,
        "video_url": f"http://127.0.0.1:8000/outputs/{final_output_filename}",
        "processing_time": processing_time,
        "total_frames": frame_index,
        "total_vehicle_detections": total_vehicle_detections,
        "vehicle_statistics": vehicle_stats,
    }

    return metadata, final_output_path


def draw_tracking_boxes(frame, tracks):
    """Draw bounding boxes with class name, tracking ID, and confidence."""
    for x1, y1, x2, y2, confidence, class_id, track_id in tracks:
        class_name = VEHICLE_CLASSES[int(class_id)]
        # Label shows class, persistent ID, and detection confidence.
        label = f"{class_name} ID:{int(track_id)} {confidence:.2f}"
        color = (0, 255, 0)

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(
            frame,
            label,
            (int(x1), max(int(y1) - 10, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
            lineType=cv2.LINE_AA,
        )

    return frame


def track_video(video_path: str, confidence_threshold: float = 0.25, job_id: str | None = None, on_progress=None):
    """
    Track vehicles across video frames using YOLOv8 + ByteTrack.

    Object detection vs object tracking:
    - Detection answers "what is in this frame?" on every frame independently.
    - Tracking answers "which detections belong to the same object over time?"

    What persist=True does:
    - Keeps the ByteTrack tracker state alive between frames in this video.
    - Without it, IDs would reset on every frame and tracking would not work.

    What ByteTrack is:
    - A multi-object tracker that links YOLO detections across frames using motion
      and appearance cues so each vehicle can keep a stable numeric ID.

    Why track IDs may change if an object disappears for a long time:
    - When a vehicle leaves the frame, the tracker eventually drops its track.
    - If it re-enters much later, ByteTrack treats it as a new object and assigns
      a fresh ID because it cannot reliably confirm it is the same vehicle.
    """
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise ValueError("Cannot open uploaded video file")

    writer = None
    try:
        frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
        estimated_total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

        success, first_frame = capture.read()
        if not success:
            raise ValueError("Uploaded video contains no readable frames")

        if frame_width == 0 or frame_height == 0:
            frame_height, frame_width = first_frame.shape[:2]

        original_name = os.path.basename(video_path)
        name, _ = os.path.splitext(original_name)
        output_filename = f"{name}_tracked.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        if not writer.isOpened():
            raise ValueError("Cannot initialize video writer for output MP4")

        unique_track_ids: set[int] = set()
        track_id_to_class: dict[int, str] = {}
        track_metadata: dict[int, dict[str, object]] = {}
        frame_index = 0
        start_time = time.time()
        frame = first_frame

        while frame is not None:
            frame_index += 1

            h, w = frame.shape[:2]
            if (w, h) != (frame_width, frame_height):
                frame = cv2.resize(frame, (frame_width, frame_height))

            results = model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                classes=list(VEHICLE_CLASSES.keys()),
                conf=confidence_threshold,
                verbose=False,
            )
            result = results[0]

            tracks = []
            if result.boxes is not None and result.boxes.id is not None:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    track_id = int(box.id[0])
                    bbox = [int(x) for x in box.xyxy[0].tolist()]

                    if track_id not in unique_track_ids:
                        unique_track_ids.add(track_id)
                        track_id_to_class[track_id] = VEHICLE_CLASSES[class_id]
                        track_metadata[track_id] = {
                            "track_id": track_id,
                            "class_name": VEHICLE_CLASSES[class_id],
                            "confidence": confidence,
                            "bbox": bbox,
                            "first_frame": frame_index,
                            "last_frame": frame_index,
                            "total_frames": 1,
                        }
                    else:
                        track_metadata[track_id]["confidence"] = confidence
                        track_metadata[track_id]["bbox"] = bbox
                        track_metadata[track_id]["last_frame"] = frame_index
                        track_metadata[track_id]["total_frames"] = int(track_metadata[track_id].get("total_frames", 0)) + 1

                    tracks.append([*bbox, confidence, class_id, track_id])

            if tracks:
                frame = draw_tracking_boxes(frame, tracks)

            writer.write(frame)

            elapsed = time.time() - start_time
            processing_fps = round(frame_index / elapsed, 2) if elapsed > 0 else 0.0
            total_frames = max(estimated_total_frames, frame_index)
            progress = round((frame_index / total_frames) * 100, 2) if total_frames > 0 else 0.0
            active_ids = [int(track[6]) for track in tracks]
            active_details = [track_metadata[int(track[6])] for track in tracks]

            if job_id is not None:
                success, jpeg = cv2.imencode(".jpg", frame)
                if success:
                    frame_base64 = base64.b64encode(jpeg.tobytes()).decode("utf-8")
                    active_tracks = [
                        {
                            "track_id": int(track[6]),
                            "class_name": VEHICLE_CLASSES[int(track[5])],
                            "confidence": float(track[4]),
                            "bbox": [
                                int(track[0]),
                                int(track[1]),
                                int(track[2]),
                                int(track[3]),
                            ],
                            "first_frame": active_details[idx]["first_frame"],
                            "last_frame": active_details[idx]["last_frame"],
                            "total_frames": active_details[idx]["total_frames"],
                        }
                        for idx, track in enumerate(tracks)
                    ]

                    ws_manager.send_frame(
                        job_id,
                        {
                            "frame": frame_base64,
                            "frame_number": frame_index,
                            "processing_fps": processing_fps,
                            "elapsed_time": round(elapsed, 2),
                            "active_tracks": active_tracks,
                            "vehicle_statistics": build_vehicle_statistics(track_id_to_class),
                            "progress": progress,
                        },
                    )

            if on_progress is not None:
                on_progress({
                    "current_frame": frame_index,
                    "total_frames": total_frames,
                    "progress_percentage": progress,
                    "elapsed_processing_time": round(elapsed, 2),
                    "processing_fps": processing_fps,
                    "active_tracked_vehicles": active_ids,
                    "active_tracked_vehicle_details": active_details,
                    "unique_tracked_vehicle_ids": sorted(unique_track_ids),
                    "vehicle_statistics": build_vehicle_statistics(track_id_to_class),
                })

            success, frame = capture.read()
            if not success:
                frame = None
    finally:
        capture.release()
        if writer is not None:
            writer.release()

    processing_time = round(time.time() - start_time, 2)
    vehicle_stats = build_vehicle_statistics(track_id_to_class)

    # Re-encode to H.264 so the output plays back in <video> tags in browsers.
    final_output_path = transcode_to_h264(output_path)
    final_output_filename = os.path.basename(final_output_path)

    metadata = {
        "filename": original_name,
        "video_url": f"http://127.0.0.1:8000/outputs/{final_output_filename}",
        "processing_time": processing_time,
        "total_frames": frame_index,
        "unique_vehicle_count": len(unique_track_ids),
        "tracked_vehicle_ids": sorted(unique_track_ids),
        "vehicle_statistics": vehicle_stats,
    }

    return metadata, final_output_path
