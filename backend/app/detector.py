"""
Server-side object detection, replacing the browser-side
@tensorflow-models/coco-ssd model from the original app.

Uses YOLOv8n (COCO-pretrained) via ultralytics, which recognizes the same
classes we need: car, truck, bus, motorcycle, person, traffic light.
"""
from __future__ import annotations
import threading
import numpy as np
from ultralytics import YOLO

VEHICLE_CLASSES = {"car", "truck", "bus", "motorcycle"}
RELEVANT_CLASSES = VEHICLE_CLASSES | {"person", "traffic light"}


class Detector:
    """Thin, thread-safe wrapper around a single shared YOLO model instance."""

    def __init__(self, weights: str = "yolov8n.pt", conf: float = 0.4):
        self.model = YOLO(weights)
        self.names = self.model.names
        self.conf = conf
        self._lock = threading.Lock()

    def detect(self, frame_bgr: np.ndarray) -> list[dict]:
        """Returns a list of {class, score, bbox:[x,y,w,h]} for relevant classes."""
        with self._lock:
            results = self.model.predict(
                frame_bgr, verbose=False, conf=self.conf, imgsz=640
            )[0]

        dets = []
        if results.boxes is None:
            return dets
        for box in results.boxes:
            cls_name = self.names[int(box.cls[0])]
            if cls_name not in RELEVANT_CLASSES:
                continue
            score = float(box.conf[0])
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            dets.append(
                {"class": cls_name, "score": score, "bbox": [x1, y1, x2 - x1, y2 - y1]}
            )
        return dets


# Single shared model instance for the whole process (loaded lazily on first use).
_detector: Detector | None = None


def get_detector() -> Detector:
    global _detector
    if _detector is None:
        _detector = Detector()
    return _detector
