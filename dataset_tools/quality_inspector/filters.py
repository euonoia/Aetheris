"""Filter definitions and record filtering utilities for quality inspection."""

from enum import Enum
from typing import List, Optional

from .inspector import QualityRecord


class QualityFilter(Enum):
    ALL = "All"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    NEEDS_REVIEW = "Needs Review"
    BLURRED = "Blurred"
    DUPLICATES = "Duplicates"
    LARGE_IMAGES = "Large Images"
    SMALL_IMAGES = "Small Images"
    LOW_BRIGHTNESS = "Low Brightness"
    HIGH_BRIGHTNESS = "High Brightness"
    HIGH_RESOLUTION = "High Resolution"
    LOW_RESOLUTION = "Low Resolution"


def filter_records(
    records: List[QualityRecord],
    filter_type: QualityFilter = QualityFilter.ALL,
    brightness_threshold: float = 100.0,
    resolution_threshold: int = 1280 * 720,
    blur_threshold: float = 100.0,
) -> List[QualityRecord]:
    if filter_type == QualityFilter.ALL:
        return records

    result: List[QualityRecord] = []
    for record in records:
        if filter_type == QualityFilter.APPROVED and record.status == "approved":
            result.append(record)
        elif filter_type == QualityFilter.REJECTED and record.status == "rejected":
            result.append(record)
        elif filter_type == QualityFilter.NEEDS_REVIEW and record.status == "needs_review":
            result.append(record)
        elif filter_type == QualityFilter.BLURRED and record.blur_score is not None and record.blur_score < blur_threshold:
            result.append(record)
        elif filter_type == QualityFilter.DUPLICATES and record.similarity_score is not None and record.similarity_score >= 0.90:
            result.append(record)
        elif filter_type == QualityFilter.LARGE_IMAGES and record.file_size_bytes is not None and record.file_size_bytes > 1_000_000:
            result.append(record)
        elif filter_type == QualityFilter.SMALL_IMAGES and record.file_size_bytes is not None and record.file_size_bytes < 250_000:
            result.append(record)
        elif filter_type == QualityFilter.LOW_BRIGHTNESS and record.brightness is not None and record.brightness < brightness_threshold:
            result.append(record)
        elif filter_type == QualityFilter.HIGH_BRIGHTNESS and record.brightness is not None and record.brightness >= brightness_threshold:
            result.append(record)
        elif filter_type == QualityFilter.HIGH_RESOLUTION and record.resolution and record.resolution[0] * record.resolution[1] >= resolution_threshold:
            result.append(record)
        elif filter_type == QualityFilter.LOW_RESOLUTION and record.resolution and record.resolution[0] * record.resolution[1] < resolution_threshold:
            result.append(record)

    return result
