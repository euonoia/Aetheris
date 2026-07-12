from __future__ import annotations
import time
from dataclasses import dataclass, field

import numpy as np

from .tracker import Track, centroid, dist
from .models import Zones


# ---------- geometry helpers (ported 1:1 from segCross / pointInRect) ----------

def _ccw(a, b, c) -> bool:
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])


def seg_cross(p1, p2, a, b) -> bool:
    return _ccw(p1, a, b) != _ccw(p2, a, b) and _ccw(p1, p2, a) != _ccw(p1, p2, b)


def point_in_rect(p, a, b) -> bool:
    min_x, max_x = min(a[0], b[0]), max(a[0], b[0])
    min_y, max_y = min(a[1], b[1]), max(a[1], b[1])
    return min_x <= p[0] <= max_x and min_y <= p[1] <= max_y


# ---------- signal color sampling from a traffic-light crop ----------

def classify_signal(frame_bgr: np.ndarray, bbox: list[float]) -> str:
    x, y, w, h = [int(round(v)) for v in bbox]
    x, y = max(0, x), max(0, y)
    crop = frame_bgr[y : y + max(1, h), x : x + max(1, w)]
    if crop.size == 0:
        return "unknown"
    # BGR -> average channels
    b = float(crop[:, :, 0].mean())
    g = float(crop[:, :, 1].mean())
    r = float(crop[:, :, 2].mean())
    if r > 140 and r - g > 35:
        return "red"
    if r > 130 and g > 110 and abs(r - g) < 40:
        return "amber"
    if g > 130 and g - r > 25:
        return "green"
    return "unknown"


@dataclass
class Violation:
    local_id: str
    track_id: int
    vehicle_type: str
    violation_type: str
    zone_name: str
    detected_speed: float | None
    speed_limit: float | None
    occurred_at: str
    snapshot: str
    confidence: float | None = None
    verdict: str = "pending"
    reasoning: str = ""
    db_id: str | None = None  # Supabase row id, set once the insert completes


def update_approx_speed(t: Track, now: float, meters_per_100px: float) -> None:
    dt = now - t.prev_time
    if dt <= 0:
        return
    meters_per_px = meters_per_100px / 100.0
    px_dist = dist(t.centroid, t.prev_centroid)
    mps = (px_dist * meters_per_px) / dt
    kmh = mps * 3.6
    t.approx_speed = kmh if t.approx_speed is None else (t.approx_speed * 0.7 + kmh * 0.3)


def current_speed(t: Track) -> tuple[float, str] | None:
    if t.gate_speed is not None and time.time() - t.gate_speed_at < 3.0:
        return (t.gate_speed, "measured")
    if t.approx_speed is not None:
        return (t.approx_speed, "est")
    return None


class ViolationEngine:
    """Stateful per-session violation checker; mirrors checkViolations() in the
    original JS but keyed off of Track objects that persist across frames."""

    def __init__(self):
        self._next_local_id = 0

    def _local_id(self, track_id: int, vtype: str) -> str:
        self._next_local_id += 1
        return f"v_{int(time.time()*1000)}_{track_id}_{vtype}_{self._next_local_id}"

    def check(
        self,
        tracks: list[Track],
        zones: Zones,
        settings,
        signal_state: str,
        now: float,
        snapshot_fn,
    ) -> list[Violation]:
        """snapshot_fn(bbox, pad_top_factor=None) -> data-url jpeg string"""
        new_violations: list[Violation] = []
        limit = settings.speed_limit_kmh
        dwell_sec = settings.dwell_seconds

        for t in tracks:
            update_approx_speed(t, now, settings.meters_per_100px)
            p1, p2 = t.prev_centroid, t.centroid

            # --- stop lines / red-light & stop-line running ---
            for i, line in enumerate(zones.stoplines):
                key = f"line_{i}"
                if key in t.flagged:
                    continue
                a, b = (line[0].x, line[0].y), (line[1].x, line[1].y)
                if seg_cross(p1, p2, a, b):
                    t.flagged.add(key)
                    spd = current_speed(t)
                    if signal_state == "red":
                        new_violations.append(
                            self._flag(t, "red_light", f"stop line #{i}", spd, limit, snapshot_fn)
                        )
                    elif signal_state == "unknown" and spd and spd[0] > 8:
                        new_violations.append(
                            self._flag(t, "stop_line", f"stop line #{i}", spd, limit, snapshot_fn)
                        )

            # --- allowed direction / wrong-way ---
            for i, line in enumerate(zones.directions):
                allowed = (line[1].x - line[0].x, line[1].y - line[0].y)
                move_vec = (p2[0] - p1[0], p2[1] - p1[1])
                mag1 = (allowed[0] ** 2 + allowed[1] ** 2) ** 0.5
                mag2 = (move_vec[0] ** 2 + move_vec[1] ** 2) ** 0.5
                if mag1 == 0 or mag2 < 1.5:
                    continue
                cos = (allowed[0] * move_vec[0] + allowed[1] * move_vec[1]) / (mag1 * mag2)
                skey = f"dir_{i}"
                if cos < -0.4:
                    t.wrong_way_streak[skey] = t.wrong_way_streak.get(skey, 0) + 1
                    if t.wrong_way_streak[skey] > 6 and skey not in t.flagged:
                        t.flagged.add(skey)
                        new_violations.append(
                            self._flag(t, "wrong_way", f"direction zone #{i}", None, limit, snapshot_fn)
                        )
                else:
                    t.wrong_way_streak[skey] = 0

            # --- no-parking dwell ---
            for i, rect in enumerate(zones.noparkings):
                key = f"park_{i}"
                a, b = (rect[0].x, rect[0].y), (rect[1].x, rect[1].y)
                inside = point_in_rect(t.centroid, a, b)
                if inside:
                    if key not in t.stationary_since:
                        t.stationary_since[key] = now
                    ref_idx = max(0, len(t.history) - 6)
                    ref = t.history[ref_idx]
                    moved = dist(t.centroid, (ref[0], ref[1]))
                    if now - t.stationary_since[key] > dwell_sec and moved < 12 and key not in t.flagged:
                        t.flagged.add(key)
                        new_violations.append(
                            self._flag(t, "no_parking", f"no-parking zone #{i}", None, limit, snapshot_fn)
                        )
                else:
                    t.stationary_since.pop(key, None)

            # --- speed gate pairs ---
            for i, pair in enumerate(zones.gate_pairs):
                key = f"gate_{i}"
                aA, bA = (pair.a[0].x, pair.a[0].y), (pair.a[1].x, pair.a[1].y)
                aB, bB = (pair.b[0].x, pair.b[0].y), (pair.b[1].x, pair.b[1].y)
                if seg_cross(p1, p2, aA, bA):
                    t.gate_entry[key] = now
                if key in t.gate_entry and seg_cross(p1, p2, aB, bB):
                    seconds = now - t.gate_entry[key]
                    if seconds > 0.05:
                        kmh = (pair.distance_m / seconds) * 3.6
                        t.gate_speed, t.gate_speed_at = kmh, time.time()
                        if kmh > limit and key not in t.flagged:
                            t.flagged.add(key)
                            new_violations.append(
                                self._flag(t, "speeding", f"gate pair #{i}", (kmh, "measured"), limit, snapshot_fn)
                            )
                    t.gate_entry.pop(key, None)

            # --- fallback continuous speeding when no gates drawn ---
            if not zones.gate_pairs and t.approx_speed is not None:
                if t.approx_speed > limit:
                    t.speeding_streak += 1
                    if t.speeding_streak > 6 and "speed_est" not in t.flagged:
                        t.flagged.add("speed_est")
                        new_violations.append(
                            self._flag(
                                t,
                                "speeding",
                                "estimated (no gate drawn)",
                                (t.approx_speed, "est"),
                                limit,
                                snapshot_fn,
                            )
                        )
                else:
                    t.speeding_streak = 0

        return new_violations

    def _flag(self, t: Track, vtype: str, zone_name: str, spd, limit, snapshot_fn) -> Violation:
        from datetime import datetime, timezone

        speed_val = spd[0] if spd else None
        return Violation(
            local_id=self._local_id(t.id, vtype),
            track_id=t.id,
            vehicle_type=t.type,
            violation_type=vtype,
            zone_name=zone_name,
            detected_speed=speed_val,
            speed_limit=limit,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            snapshot=snapshot_fn(t.bbox),
            confidence=t.score,
        )


def update_motorcycle_riders(motorcycles: list[Track], persons: list[dict], now: float) -> None:
    """Mirrors updateMotorcycleRiders: counts person detections in a padded
    zone above/around each motorcycle bbox."""
    for t in motorcycles:
        x, y, w, h = t.bbox
        pad_x, pad_top = w * 0.5, h * 1.6
        min_x, max_x = x - pad_x, x + w + pad_x
        min_y, max_y = y - pad_top, y + h
        count = 0
        for p in persons:
            cx, cy = centroid(p["bbox"])
            if min_x <= cx <= max_x and min_y <= cy <= max_y:
                count += 1
        t.rider_counts.append((max(count, 1), now))
        t.rider_counts = [rc for rc in t.rider_counts if now - rc[1] < 2.0]
        t.rider_estimate = max((rc[0] for rc in t.rider_counts), default=0)