from dataclasses import dataclass
from typing import Dict, List, Tuple

from .zone_utils import Point, point_in_polygon

# COCO class ids that count as "vehicle" for parking purposes.
VEHICLE_CLASS_IDS = {2, 3, 5, 7}  # car, motorcycle, bus, truck

# How far (in pixels) a vehicle's center can drift between updates and still
# count as "not moving". Tune this relative to your video resolution.
STATIONARY_PIXEL_THRESHOLD = 12.0


@dataclass
class TrackState:
    track_id: int
    cls_name: str
    entered_zone_at: float
    last_center: Tuple[float, float]
    stationary_since: float
    last_seen: float
    violated: bool = False


class ParkingViolationTracker:
    """
    Stateful tracker for a single video/stream. Feed it detections frame by
    frame (each with a track_id from the model's tracker) and it flags any
    vehicle that sits inside the configured no-parking zone, roughly
    stationary, for longer than `dwell_seconds`.
    """

    def __init__(self, zone: List[Point], dwell_seconds: float = 10.0):
        if len(zone) < 3:
            raise ValueError("Zone must have at least 3 points")
        self.zone = zone
        self.dwell_seconds = dwell_seconds
        self.tracks: Dict[int, TrackState] = {}

    def update(self, detections: List[dict], timestamp: float) -> List[dict]:
        """
        detections: [{"track_id": int, "class": str, "center": (x, y)}, ...]
        Returns newly-triggered violation events (each track fires once).
        """
        new_violations: List[dict] = []
        seen_ids = set()

        for det in detections:
            tid = det["track_id"]
            center = det["center"]
            seen_ids.add(tid)

            if not point_in_polygon(center, self.zone):
                self.tracks.pop(tid, None)
                continue

            state = self.tracks.get(tid)
            if state is None:
                self.tracks[tid] = TrackState(
                    track_id=tid,
                    cls_name=det["class"],
                    entered_zone_at=timestamp,
                    last_center=center,
                    stationary_since=timestamp,
                    last_seen=timestamp,
                )
                continue

            moved = (
                (center[0] - state.last_center[0]) ** 2
                + (center[1] - state.last_center[1]) ** 2
            ) ** 0.5

            if moved > STATIONARY_PIXEL_THRESHOLD:
                state.stationary_since = timestamp  # it's still moving, reset the clock

            state.last_center = center
            state.last_seen = timestamp

            dwell = timestamp - state.stationary_since
            if dwell >= self.dwell_seconds and not state.violated:
                state.violated = True
                new_violations.append(
                    {
                        "track_id": tid,
                        "class": state.cls_name,
                        "dwell_seconds": round(dwell, 1),
                        "center": center,
                        "timestamp": round(timestamp, 2),
                    }
                )

        # Tracks not seen this frame are dropped. (A short grace period could
        # be added later to tolerate brief occlusion.)
        for tid in list(self.tracks.keys()):
            if tid not in seen_ids:
                self.tracks.pop(tid, None)

        return new_violations

    def violating_ids(self) -> set:
        return {t.track_id for t in self.tracks.values() if t.violated}