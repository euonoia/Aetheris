"""Blur detection stage for the dataset processing pipeline."""

from pathlib import Path
from typing import List, Optional

from ..blur_detector.detector import BlurDetector
from ..models.dataset_record import ExtractedFrame, FilteredFrame
from ..models.processing_result import StageResult
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class BlurFilterStage:
    def __init__(self, detector: BlurDetector) -> None:
        self.detector = detector
        self.logger = get_logger(__name__)

    def run(
        self,
        frames: List[ExtractedFrame],
        threshold: float,
        output_folder: Path,
    ) -> StageResult:
        filtered_frames: List[FilteredFrame] = []
        blurred_count = 0

        for extracted in frames:
            blur_score = self.detector.calculate_blur_score(extracted.output_path)
            is_blurry = blur_score is not None and blur_score < threshold
            kept = not is_blurry
            if is_blurry:
                blurred_count += 1

            filtered_frames.append(
                FilteredFrame(
                    extracted_frame=extracted,
                    blur_score=blur_score,
                    is_duplicate=False,
                    kept=kept,
                )
            )

        return StageResult(
            stage_name="Blur Detection",
            success=True,
            data={
                "filtered_frames": filtered_frames,
                "blurred_count": blurred_count,
            },
        )
