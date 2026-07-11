from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel


class Point(BaseModel):
    x: float
    y: float


class GatePair(BaseModel):
    a: list[Point]
    b: list[Point]
    distance_m: float


class Zones(BaseModel):
    stoplines: list[list[Point]] = []
    directions: list[list[Point]] = []
    noparkings: list[list[Point]] = []
    gate_pairs: list[GatePair] = []


class Settings(BaseModel):
    speed_limit_kmh: float = 40
    meters_per_100px: float = 5
    dwell_seconds: float = 6
    max_riders: int = 2
    detect_interval_ms: int = 180


class FrameMessage(BaseModel):
    type: Literal["frame"] = "frame"
    image: str  # data URL, e.g. "data:image/jpeg;base64,...."
    zones: Zones
    settings: Settings


class ResetMessage(BaseModel):
    type: Literal["reset"] = "reset"


class TrackOut(BaseModel):
    id: int
    type: str
    bbox: list[float]
    speed_kmh: Optional[float] = None
    speed_source: Optional[str] = None
    flagged: bool = False
    rider_estimate: int = 0


class ViolationOut(BaseModel):
    local_id: str
    track_id: int
    vehicle_type: str
    violation_type: str
    zone_name: str
    detected_speed: Optional[float] = None
    speed_limit: Optional[float] = None
    confidence: Optional[float] = None
    occurred_at: str
    snapshot: str  # data URL jpeg
    verdict: str = "pending"  # pending | confirmed | dismissed | error | unverified
    reasoning: str = ""


class FrameResult(BaseModel):
    type: Literal["result"] = "result"
    signal: str
    tracks: list[TrackOut]
    new_violations: list[ViolationOut] = []
    violation_updates: list[ViolationOut] = []
    stats: dict