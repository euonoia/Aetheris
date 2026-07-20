"""Video processing service for dataset pipeline."""

from pathlib import Path
from typing import Callable, List, Optional

from ..frame_extractor.extractor import ExtractionConfig, FrameExtractor
from ..models.dataset_record import ExtractedFrame, VideoInfo
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class VideoService:
    def __init__(self, extractor: Optional[FrameExtractor] = None) -> None:
        self.extractor = extractor or FrameExtractor()
        self.logger = get_logger(__name__)

    def get_video_info(self, video_path: Path) -> Optional[VideoInfo]:
        metadata = self.extractor.get_video_metadata(video_path)
        if not metadata:
            return None
        return VideoInfo(
            video_path=video_path,
            total_frames=metadata.total_frames,
            fps=metadata.fps,
            width=metadata.width,
            height=metadata.height,
            duration=metadata.duration,
            codec=metadata.codec,
        )

    def extract_frames(
        self,
        video_path: Path,
        output_folder: Path,
        interval_type: str,
        interval_value: float,
        on_progress: Optional[Callable[[int, int], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> List[ExtractedFrame]:
        video_info = self.get_video_info(video_path)
        if video_info is None:
            raise RuntimeError("Unable to read video metadata")

        config = ExtractionConfig(
            output_folder=output_folder,
            interval_type=interval_type,
            interval_value=interval_value,
        )

        output_folder.mkdir(parents=True, exist_ok=True)
        extracted_count, frame_metadata = self.extractor.extract_frames(
            video_path,
            config,
            on_progress=on_progress,
            on_error=on_error,
        )

        frames: List[ExtractedFrame] = []
        for metadata in frame_metadata:
            frames.append(
                ExtractedFrame(
                    filename=metadata["filename"],
                    frame_index=metadata["frame_index"],
                    frame_number=metadata["frame_number"],
                    time_seconds=metadata["time_seconds"],
                    output_path=output_folder / metadata["filename"],
                )
            )

        self.logger.info(f"Extracted {len(frames)} frames to {output_folder}")
        return frames
