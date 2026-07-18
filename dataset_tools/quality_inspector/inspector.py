"""Core dataset quality inspection logic."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..utils.file_utils import format_file_size
from .filters import QualityFilter, filter_records
from .image_metrics import (
    calculate_blur_score,
    calculate_brightness,
    calculate_contrast,
    calculate_sharpness,
    calculate_similarity,
    resolution_from_image,
)

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


@dataclass
class QualityRecord:
    filename: str
    image_path: Path
    status: str = "not_reviewed"
    blur_score: Optional[float] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    sharpness: Optional[float] = None
    similarity_score: Optional[float] = None
    resolution: Optional[Tuple[int, int]] = None
    file_size_bytes: Optional[int] = None
    notes: str = ""
    selected: bool = False
    frame_number: Optional[int] = None
    time_seconds: Optional[float] = None


class QualityInspectorManager:
    """Loads image records and computes quality metrics for inspection."""

    def __init__(self) -> None:
        self.records: List[QualityRecord] = []
        self.filter_type: QualityFilter = QualityFilter.ALL
        self.blur_threshold: float = 100.0

    def load_dataset(self, folder_path: Path) -> List[QualityRecord]:
        images = sorted(
            [path for path in folder_path.iterdir() if path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS]
        )
        self.records = [self._create_record(path) for path in images]
        self._compute_metrics()
        self._compute_similarities()
        return self.records

    def _create_record(self, image_path: Path) -> QualityRecord:
        filename = image_path.name
        resolution = resolution_from_image(image_path)
        file_size = image_path.stat().st_size if image_path.exists() else None
        frame_number = self._parse_frame_number(filename)

        time_seconds = None
        if frame_number is not None:
            time_seconds = float(frame_number)

        return QualityRecord(
            filename=filename,
            image_path=image_path,
            resolution=resolution,
            file_size_bytes=file_size,
            frame_number=frame_number,
            time_seconds=time_seconds,
        )

    def _parse_frame_number(self, filename: str) -> Optional[int]:
        digits = "".join(ch for ch in filename if ch.isdigit())
        return int(digits) if digits else None

    def _compute_metrics(self) -> None:
        for record in self.records:
            record.blur_score = calculate_blur_score(record.image_path)
            record.brightness = calculate_brightness(record.image_path)
            record.contrast = calculate_contrast(record.image_path)
            record.sharpness = calculate_sharpness(record.image_path)

    def _compute_similarities(self) -> None:
        previous = None
        for record in self.records:
            if previous is not None:
                record.similarity_score = calculate_similarity(previous.image_path, record.image_path)
            previous = record

    def get_filtered_records(self) -> List[QualityRecord]:
        return filter_records(
            self.records,
            filter_type=self.filter_type,
            brightness_threshold=100.0,
            resolution_threshold=1280 * 720,
            blur_threshold=self.blur_threshold,
        )

    def set_filter(self, filter_name: str) -> None:
        try:
            self.filter_type = QualityFilter(filter_name)
        except ValueError:
            self.filter_type = QualityFilter.ALL

    def update_status(self, record: QualityRecord, status: str, note: str = "") -> None:
        record.status = status
        if note:
            record.notes = note

    def batch_update_status(self, records: List[QualityRecord], status: str, note: str = "") -> None:
        for record in records:
            self.update_status(record, status, note)

    def restore_deleted(self, records: List[QualityRecord]) -> None:
        for record in records:
            if record.status == "deleted":
                record.status = "not_reviewed"

    def get_health_summary(self) -> Dict[str, int]:
        total = len(self.records)
        approved = sum(1 for r in self.records if r.status == "approved")
        rejected = sum(1 for r in self.records if r.status == "rejected")
        needs_review = sum(1 for r in self.records if r.status == "needs_review")
        blurred = sum(1 for r in self.records if r.blur_score is not None and r.blur_score < self.blur_threshold)
        duplicates = sum(1 for r in self.records if r.similarity_score is not None and r.similarity_score >= 0.90)
        return {
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "needs_review": needs_review,
            "blurred": blurred,
            "duplicates": duplicates,
        }

    def get_quality_score(self) -> int:
        summary = self.get_health_summary()
        if summary["total"] == 0:
            return 0
        reviewed = summary["approved"] + summary["rejected"] + summary["needs_review"]
        score = (reviewed / summary["total"]) * 100
        return int(score)

    def get_dataset_stats(self) -> Dict[str, Optional[float]]:
        total = len(self.records)
        brightness_values = [r.brightness for r in self.records if r.brightness is not None]
        blur_values = [r.blur_score for r in self.records if r.blur_score is not None]
        resolution_values = [r.resolution[0] * r.resolution[1] for r in self.records if r.resolution]

        return {
            "total_images": total,
            "average_blur": round(sum(blur_values) / len(blur_values), 2) if blur_values else 0.0,
            "average_brightness": round(sum(brightness_values) / len(brightness_values), 2) if brightness_values else 0.0,
            "average_resolution": int(sum(resolution_values) / len(resolution_values)) if resolution_values else 0,
            "quality_score": self.get_quality_score(),
        }

    def describe_record(self, record: QualityRecord) -> Dict[str, str]:
        return {
            "Filename": record.filename,
            "Resolution": f"{record.resolution[0]}x{record.resolution[1]}" if record.resolution else "N/A",
            "Blur Score": f"{record.blur_score:.2f}" if record.blur_score is not None else "N/A",
            "Brightness": f"{record.brightness:.2f}" if record.brightness is not None else "N/A",
            "Contrast": f"{record.contrast:.2f}" if record.contrast is not None else "N/A",
            "Sharpness": f"{record.sharpness:.2f}" if record.sharpness is not None else "N/A",
            "Similarity": f"{record.similarity_score:.3f}" if record.similarity_score is not None else "N/A",
            "File Size": format_file_size(record.file_size_bytes) if record.file_size_bytes else "N/A",
            "Status": record.status.replace("_", " ").title(),
            "Notes": record.notes or "",
        }
