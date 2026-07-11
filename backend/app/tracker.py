from __future__ import annotations
import math
from dataclasses import dataclass, field


def centroid(bbox: list[float]) -> tuple[float, float]:
    x, y, w, h = bbox
    return (x + w / 2, y + h / 2)


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


@dataclass
class Track:
    id: int
    type: str
    bbox: list[float]
    centroid: tuple[float, float]
    prev_centroid: tuple[float, float]
    last_seen: float
    prev_time: float
    first_seen: float
    history: list[tuple[float, float, float]] = field(default_factory=list)
    score: float = 0.0  # latest detector confidence for this track

    # violation bookkeeping (mirrors the JS track object)
    flagged: set[str] = field(default_factory=set)
    stationary_since: dict[str, float] = field(default_factory=dict)
    wrong_way_streak: dict[str, int] = field(default_factory=dict)
    gate_entry: dict[str, float] = field(default_factory=dict)
    speeding_streak: int = 0
    approx_speed: float | None = None
    gate_speed: float | None = None
    gate_speed_at: float = 0.0

    # motorcycle rider/helmet bookkeeping
    rider_counts: list[tuple[int, float]] = field(default_factory=list)
    rider_estimate: int = 0
    last_compliance_check: float = 0.0
    compliance_checking: bool = False

    # supabase bookkeeping
    db_synced: bool = False  # whether a `vehicles` row has been written yet


class CentroidTracker:
    """Greedy nearest-centroid tracker, same matching rule as the JS version
    (max match distance 120px, tracks expire after 1.2s unseen)."""

    MATCH_DIST = 120.0
    EXPIRE_SEC = 1.2

    def __init__(self):
        self.tracks: dict[int, Track] = {}
        self._next_id = 1

    def update(self, detections: list[dict], now: float) -> list[Track]:
        unmatched = set(self.tracks.keys())

        for det in detections:
            if det["class"] not in ("car", "truck", "bus", "motorcycle"):
                continue
            c = centroid(det["bbox"])

            best_id, best_dist = None, self.MATCH_DIST
            for tid in unmatched:
                d = dist(self.tracks[tid].centroid, c)
                if d < best_dist:
                    best_dist, best_id = d, tid

            if best_id is not None:
                t = self.tracks[best_id]
                t.prev_centroid = t.centroid
                t.prev_time = t.last_seen
                t.centroid = c
                t.bbox = det["bbox"]
                t.last_seen = now
                t.type = det["class"]
                t.score = det.get("score", t.score)
                t.history.append((c[0], c[1], now))
                if len(t.history) > 40:
                    t.history.pop(0)
                unmatched.discard(best_id)
            else:
                t = Track(
                    id=self._next_id,
                    type=det["class"],
                    bbox=det["bbox"],
                    centroid=c,
                    prev_centroid=c,
                    last_seen=now,
                    prev_time=now,
                    first_seen=now,
                    history=[(c[0], c[1], now)],
                    score=det.get("score", 0.0),
                )
                self.tracks[self._next_id] = t
                self._next_id += 1

        stale = [tid for tid, t in self.tracks.items() if now - t.last_seen > self.EXPIRE_SEC]
        for tid in stale:
            del self.tracks[tid]

        return list(self.tracks.values())

    @property
    def total_seen(self) -> int:
        return self._next_id - 1