"""Standard result objects for pipeline stages."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class StageResult:
    stage_name: str
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    warnings: Optional[List[str]] = None


@dataclass(frozen=True)
class PipelineStatistics:
    total_frames: int
    extracted_frames: int
    kept_frames: int
    removed_frames: int
    blurred_frames: int
    duplicate_frames: int
    average_blur: float
    average_brightness: float
    average_resolution: float
    processing_time_seconds: float
