"""Frame extraction stage for the dataset processing pipeline."""

import time
from pathlib import Path
from typing import Callable, List, Optional

from ..frame_extractor.extractor import ExtractionConfig, FrameExtractor
from ..models.dataset_record import ExtractedFrame, VideoInfo
from ..models.processing_result import StageResult
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class ExtractionStage:
    def __init__(self, extractor: FrameExtractor) -> None:
        self.extractor = extractor
        self.logger = get_logger(__name__)

    def run(
        self,
        video_path: Path,
        output_folder: Path,
        interval_type: str,
        interval_value: float,
        on_progress: Optional[Callable[[int, int], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> StageResult:
        try:
            metadata = self.extractor.get_video_metadata(video_path)
            if not metadata:
                return StageResult(
                    stage_name="Video Metadata",
                    success=False,
                    error_message="Failed to read video metadata",
                )

            video_info = VideoInfo(
                video_path=video_path,
                total_frames=metadata.total_frames,
                fps=metadata.fps,
                width=metadata.width,
                height=metadata.height,
                duration=metadata.duration,
                codec=metadata.codec,
            )

            config = ExtractionConfig(
                output_folder=output_folder,
                interval_type=interval_type,
                interval_value=interval_value,
                blur_threshold=None,
                remove_duplicates=False,
            )

            output_folder.mkdir(parents=True, exist_ok=True)
            extracted, frame_metadata = self.extractor.extract_frames(
                video_path,
                config,
                on_progress=on_progress,
                on_error=on_error,
            )

            extracted_frames: List[ExtractedFrame] = []
            for metadata_item in frame_metadata:
                extracted_frames.append(
                    ExtractedFrame(
                        filename=metadata_item["filename"],
                        frame_index=metadata_item["frame_index"],
                        frame_number=metadata_item["frame_number"],
                        time_seconds=metadata_item["time_seconds"],
                        output_path=output_folder / metadata_item["filename"],
                    )
                )

            return StageResult(
                stage_name="Frame Extraction",
                success=True,
                data={
                    "video_info": video_info,
                    "extracted_frames": extracted_frames,
                },
            )

        except Exception as e:
            logger.error(f"ExtractionStage failed: {e}")
            return StageResult(
                stage_name="Frame Extraction",
                success=False,
                error_message=str(e),
            )
