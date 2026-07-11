from __future__ import annotations
import base64
import cv2
import numpy as np


def data_url_to_bgr(data_url: str) -> np.ndarray:
    """Decodes a 'data:image/jpeg;base64,....' string to a BGR ndarray."""
    header, b64data = data_url.split(",", 1) if "," in data_url else ("", data_url)
    raw = base64.b64decode(b64data)
    arr = np.frombuffer(raw, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Could not decode incoming frame")
    return frame


def bgr_to_data_url(frame: np.ndarray, quality: int = 75) -> str:
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        raise ValueError("Could not encode frame")
    b64 = base64.b64encode(buf.tobytes()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def crop_snapshot(frame: np.ndarray, bbox: list[float], top_pad_factor: float | None = None, quality: int = 75) -> str:
    """Mirrors cropSnapshot() from the original JS: pads around the bbox
    (extra headroom above for motorcycle rider/helmet crops) and re-encodes."""
    h_img, w_img = frame.shape[:2]
    x, y, w, h = bbox
    pad_side = 20
    pad_top = h * top_pad_factor if top_pad_factor else 20

    x0 = max(0, int(x - pad_side))
    y0 = max(0, int(y - pad_top))
    x1 = min(w_img, int(x + w + pad_side))
    y1 = min(h_img, int(y + h + pad_top + 20))

    if x1 <= x0 or y1 <= y0:
        crop = frame
    else:
        crop = frame[y0:y1, x0:x1]

    return bgr_to_data_url(crop, quality=quality)
