from __future__ import annotations
import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone

from .detector import get_detector
from .imaging import data_url_to_bgr, crop_snapshot
from .tracker import CentroidTracker
from .violations import ViolationEngine, Violation, classify_signal, update_motorcycle_riders
from .groq_client import ai_enabled, review_violation, inspect_motorcycle
from .models import FrameMessage, FrameResult, TrackOut, ViolationOut, Zones, Settings
from . import supabase_client as sb

log = logging.getLogger("roadwatch")


def _violation_to_out(v: Violation) -> ViolationOut:
    return ViolationOut(
        local_id=v.local_id,
        track_id=v.track_id,
        vehicle_type=v.vehicle_type,
        violation_type=v.violation_type,
        zone_name=v.zone_name,
        detected_speed=v.detected_speed,
        speed_limit=v.speed_limit,
        confidence=v.confidence,
        occurred_at=v.occurred_at,
        snapshot=v.snapshot,
        verdict=v.verdict,
        reasoning=v.reasoning,
    )


class Session:
    """Holds all mutable state for one connected camera feed (one browser tab)."""

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.tracker = CentroidTracker()
        self.engine = ViolationEngine()
        self.signal_state = "unknown"
        self.violation_count = 0
        self.confirmed_count = 0
        self.dismissed_count = 0
        self.violations: dict[str, Violation] = {}
        self._pending_ai_updates: list[str] = []  # local_ids updated since last poll
        self._lock = asyncio.Lock()

    def stats(self) -> dict:
        return {
            "tracked": self.tracker.total_seen,
            "flagged": self.violation_count,
            "confirmed": self.confirmed_count,
            "dismissed": self.dismissed_count,
        }

    async def process_frame(self, msg: FrameMessage) -> FrameResult:
        now = time.time()
        frame = data_url_to_bgr(msg.image)
        detector = get_detector()
        dets = await asyncio.to_thread(detector.detect, frame)

        vdets = [d for d in dets if d["class"] in ("car", "truck", "bus", "motorcycle")]
        lights = [d for d in dets if d["class"] == "traffic light"]
        persons = [d for d in dets if d["class"] == "person" and d["score"] > 0.4]

        # signal color
        if lights:
            best_light = max(lights, key=lambda d: d["score"])
            self.signal_state = classify_signal(frame, best_light["bbox"])
        else:
            self.signal_state = "unknown"

        tracks = self.tracker.update(vdets, now)

        # Persist a `vehicles` row the first time we see each track id.
        for t in tracks:
            if not t.db_synced:
                t.db_synced = True
                asyncio.create_task(self._sync_vehicle(t))

        def snapshot_fn(bbox, top_pad_factor=None):
            return crop_snapshot(frame, bbox, top_pad_factor=top_pad_factor)

        new_violations = self.engine.check(
            tracks, msg.zones, msg.settings, self.signal_state, now, snapshot_fn
        )

        for v in new_violations:
            self.violation_count += 1
            self.violations[v.local_id] = v
            if not ai_enabled():
                v.verdict = "unverified"
                v.reasoning = "Set GROQ_API_KEY on the server to auto-verify this."
            asyncio.create_task(self._insert_violation_row(v))
            if ai_enabled():
                asyncio.create_task(self._review_violation(v))

        # motorcycle rider/helmet inspection
        motos = [t for t in tracks if t.type == "motorcycle"]
        update_motorcycle_riders(motos, persons, now)
        if ai_enabled():
            for t in motos:
                due = now - t.last_compliance_check > 4.0
                needs_check = ("no_helmet" not in t.flagged) or ("overloading" not in t.flagged)
                if due and needs_check and not t.compliance_checking:
                    t.last_compliance_check = now
                    t.compliance_checking = True
                    snap = crop_snapshot(frame, t.bbox, top_pad_factor=1.6)
                    asyncio.create_task(self._inspect_motorcycle(t, snap))

        updates = await self._drain_updates()

        track_outs = []
        for t in tracks:
            speed = None
            source = None
            if t.gate_speed is not None and time.time() - t.gate_speed_at < 3.0:
                speed, source = t.gate_speed, "measured"
            elif t.approx_speed is not None:
                speed, source = t.approx_speed, "est"
            track_outs.append(
                TrackOut(
                    id=t.id,
                    type=t.type,
                    bbox=t.bbox,
                    speed_kmh=speed,
                    speed_source=source,
                    flagged=len(t.flagged) > 0,
                    rider_estimate=t.rider_estimate,
                )
            )

        return FrameResult(
            signal=self.signal_state,
            tracks=track_outs,
            new_violations=[_violation_to_out(v) for v in new_violations],
            violation_updates=updates,
            stats=self.stats(),
        )

    async def _sync_vehicle(self, t) -> None:
        try:
            await sb.insert(
                "vehicles",
                {
                    "track_id": t.id,
                    "vehicle_type": t.type,
                    "first_seen": datetime.now(timezone.utc).isoformat(),
                    "last_seen": datetime.now(timezone.utc).isoformat(),
                    "session_id": self.id,
                },
            )
        except Exception:  # noqa: BLE001
            log.exception("failed to sync vehicle row for track %s", t.id)

    async def _insert_violation_row(self, v: Violation) -> None:
        try:
            row = await sb.insert(
                "violations",
                {
                    "session_id": self.id,
                    "track_id": v.track_id,
                    "vehicle_type": v.vehicle_type,
                    "violation_type": v.violation_type,
                    "zone_name": v.zone_name,
                    "detected_speed": v.detected_speed,
                    "speed_limit": v.speed_limit,
                    "confidence": v.confidence,
                    "snapshot": v.snapshot,
                    "occurred_at": v.occurred_at,
                    "ai_review_status": v.verdict,
                    "ai_review_reason": v.reasoning,
                    "ai_review_conf": v.confidence,
                },
            )
            if row and "id" in row:
                v.db_id = row["id"]
        except Exception:  # noqa: BLE001
            log.exception("failed to insert violation row for %s", v.local_id)

    async def _sync_violation_verdict(self, v: Violation) -> None:
        if not v.db_id:
            return
        try:
            await sb.patch(
                "violations",
                {"id": v.db_id},
                {
                    "ai_review_status": v.verdict,
                    "ai_review_reason": v.reasoning,
                    "ai_review_conf": v.confidence,
                },
            )
        except Exception:  # noqa: BLE001
            log.exception("failed to patch violation row %s", v.db_id)

    async def _review_violation(self, v: Violation) -> None:
        result = await review_violation(
            v.snapshot, v.violation_type, v.zone_name, v.detected_speed, v.speed_limit, v.vehicle_type
        )
        async with self._lock:
            if result.get("ok") and result.get("data", {}).get("verdict"):
                verdict = "confirmed" if result["data"]["verdict"] == "confirmed" else "dismissed"
                v.verdict = verdict
                v.reasoning = result["data"].get("reasoning", "")
                if verdict == "confirmed":
                    self.confirmed_count += 1
                else:
                    self.dismissed_count += 1
            else:
                v.verdict = "error"
                v.reasoning = "AI review failed: " + result.get("error", "unknown error")
            self._pending_ai_updates.append(v.local_id)
        await self._sync_violation_verdict(v)

    async def _inspect_motorcycle(self, t, snapshot: str) -> None:
        result = await inspect_motorcycle(snapshot)
        t.compliance_checking = False
        if not result.get("ok"):
            return
        data = result.get("data") or {}

        if data.get("all_wearing_helmets") is False and "no_helmet" not in t.flagged:
            t.flagged.add("no_helmet")
            await self._record_confirmed(
                t, "no_helmet", "motorcycle inspection", data.get("reasoning") or "Rider without a helmet detected.", snapshot
            )

        riders = data.get("riders")
        if isinstance(riders, (int, float)) and "overloading" not in t.flagged:
            # max_riders threshold is enforced client-side in settings; server re-checks
            # against a generic default of 2 if this fires independently of the main loop.
            if riders > 2:
                t.flagged.add("overloading")
                await self._record_confirmed(
                    t,
                    "overloading",
                    "motorcycle inspection",
                    data.get("reasoning") or f"{riders} riders detected on one motorcycle.",
                    snapshot,
                )

    async def _record_confirmed(self, t, vtype: str, zone_name: str, reasoning: str, snapshot: str = "") -> None:
        v = Violation(
            local_id=f"v_{int(time.time()*1000)}_{t.id}_{vtype}",
            track_id=t.id,
            vehicle_type=t.type,
            violation_type=vtype,
            zone_name=zone_name,
            detected_speed=None,
            speed_limit=None,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            snapshot=snapshot,
            confidence=t.score,
            verdict="confirmed",
            reasoning=reasoning,
        )
        async with self._lock:
            self.violation_count += 1
            self.confirmed_count += 1
            self.violations[v.local_id] = v
            self._pending_ai_updates.append(v.local_id)
        await self._insert_violation_row(v)

    async def _drain_updates(self) -> list[ViolationOut]:
        async with self._lock:
            ids = self._pending_ai_updates
            self._pending_ai_updates = []
        return [_violation_to_out(self.violations[i]) for i in ids if i in self.violations]