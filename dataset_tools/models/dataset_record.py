"""Immutable data models for dataset processing."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


@dataclass(frozen=True)
class VideoInfo:
    video_path: Path
    total_frames: int
    fps: float
    width: int
    height: int
    duration: float
    codec: str


@dataclass(frozen=True)
class ExtractedFrame:
    filename: str
    frame_index: int
    frame_number: int
    time_seconds: float
    output_path: Path


@dataclass
class FilteredFrame:
    extracted_frame: ExtractedFrame
    blur_score: Optional[float]
    is_duplicate: bool
    kept: bool


@dataclass
class MetadataRecord:
    extracted_frame: ExtractedFrame
    blur_score: Optional[float]
    is_duplicate: bool
    kept: bool
    brightness: Optional[float]
    contrast: Optional[float]
    sharpness: Optional[float]
    resolution: Tuple[int, int]
    file_size_bytes: int
    status: str = "not_reviewed"
    notes: str = ""


@dataclass(frozen=True)
class DatasetRecord:
    video_info: VideoInfo
    frames: tuple[MetadataRecord, ...]
    dataset_folder: Path
    approved_folder: Path
    rejected_folder: Path
    needs_review_folder: Path
