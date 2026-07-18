"""Duplicate detection stage for the dataset processing pipeline."""

from pathlib import Path
from typing import List, Optional

from ..duplicate_detector.detector import DuplicateDetector
from ..models.dataset_record import FilteredFrame, ExtractedFrame
from ..models.processing_result import StageResult
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class DuplicateFilterStage:
    def __init__(self, detector: DuplicateDetector) -> None:
        self.detector = detector
        self.logger = get_logger(__name__)

    def run(
        self,
        frames: List[FilteredFrame],
        threshold: float,
    ) -> StageResult:
        processed: List[FilteredFrame] = []
        duplicate_count = 0
        previous_image = None

        for filtered in frames:
            if not filtered.kept:
                processed.append(filtered)
                continue

            current_image = self.detector.load_image(filtered.extracted_frame.output_path)
            is_duplicate = False

            if previous_image is not None and current_image is not None:
                similarity = self.detector.calculate_similarity(previous_image, current_image)
                if similarity >= threshold:
                    is_duplicate = True
                    duplicate_count += 1

            current_filtered = FilteredFrame(
                extracted_frame=filtered.extracted_frame,
                blur_score=filtered.blur_score,
                is_duplicate=is_duplicate,
                kept=not is_duplicate,
            )

            processed.append(current_filtered)
            if not is_duplicate and current_image is not None:
                previous_image = current_image

        return StageResult(
            stage_name="Duplicate Detection",
            success=True,
            data={
                "filtered_frames": processed,
                "duplicate_count": duplicate_count,
            },
        )
