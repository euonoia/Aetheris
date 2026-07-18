"""
Frame extraction module for Dataset Engineering Toolkit.

Handles video frame extraction with configurable intervals and output options.
"""

import cv2
import time
from pathlib import Path
from typing import Optional, Callable, Tuple
from dataclasses import dataclass

from config import OUTPUT_IMAGE_FORMAT, JPEG_QUALITY
from utils.logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class ExtractionConfig:
    """Configuration for frame extraction."""

    output_folder: Path
    interval_type: str  # 'frames' or 'seconds'
    interval_value: float
    blur_threshold: Optional[float] = None
    remove_duplicates: bool = False
    duplicate_threshold: float = 0.95


@dataclass
class VideoMetadata:
    """Metadata extracted from video file."""

    total_frames: int
    fps: float
    width: int
    height: int
    duration: float
    codec: str

    @property
    def resolution(self) -> Tuple[int, int]:
        """Get video resolution as tuple."""
        return (self.width, self.height)


class FrameExtractor:
    """
    Main frame extraction engine.

    Handles video loading, frame extraction, and coordinate calculations.
    """

    def __init__(self) -> None:
        """Initialize frame extractor."""
        self.logger = get_logger(__name__)

    def get_video_metadata(self, video_path: Path) -> Optional[VideoMetadata]:
        """
        Extract metadata from video file.

        Args:
            video_path: Path to video file

        Returns:
            VideoMetadata object or None if failed
        """
        try:
            cap = cv2.VideoCapture(str(video_path))

            if not cap.isOpened():
                self.logger.error(f"Failed to open video: {video_path}")
                return None

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))

            cap.release()

            # Convert fourcc code to string
            codec = "".join([chr((fourcc >> (8 * i)) & 0xFF) for i in range(4)])

            duration = total_frames / fps if fps > 0 else 0

            metadata = VideoMetadata(
                total_frames=total_frames,
                fps=fps,
                width=width,
                height=height,
                duration=duration,
                codec=codec,
            )

            self.logger.info(
                f"Video metadata extracted: {total_frames} frames, "
                f"{fps} fps, {width}x{height}, duration {duration:.2f}s"
            )

            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting video metadata: {str(e)}")
            return None

    def calculate_extraction_indices(
        self,
        total_frames: int,
        fps: float,
        interval_type: str,
        interval_value: float,
    ) -> list:
        """
        Calculate frame indices to extract based on interval.

        Args:
            total_frames: Total number of frames in video
            fps: Frames per second
            interval_type: 'frames' or 'seconds'
            interval_value: Interval value

        Returns:
            List of frame indices to extract
        """
        if interval_type == "frames":
            interval = int(interval_value)
        elif interval_type == "seconds":
            interval = int(interval_value * fps)
        else:
            raise ValueError(f"Unknown interval type: {interval_type}")

        if interval <= 0:
            interval = 1

        indices = list(range(0, total_frames, interval))
        self.logger.info(
            f"Calculated {len(indices)} frames to extract "
            f"(interval: {interval_value} {interval_type})"
        )

        return indices

    def extract_frames(
        self,
        video_path: Path,
        config: ExtractionConfig,
        on_progress: Optional[Callable[[int, int], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> Tuple[int, list]:
        """
        Extract frames from video.

        Args:
            video_path: Path to video file
            config: ExtractionConfig with extraction settings
            on_progress: Callback function(current_frame, total_frames)
            on_error: Callback function(error_message)

        Returns:
            Tuple of (frames_extracted, frame_metadata_list)
        """
        try:
            # Get video metadata
            metadata = self.get_video_metadata(video_path)
            if not metadata:
                error_msg = "Failed to read video metadata"
                if on_error:
                    on_error(error_msg)
                return 0, []

            # Create output folder
            config.output_folder.mkdir(parents=True, exist_ok=True)

            # Calculate frame indices
            frame_indices = self.calculate_extraction_indices(
                metadata.total_frames,
                metadata.fps,
                config.interval_type,
                config.interval_value,
            )

            cap = cv2.VideoCapture(str(video_path))
            extracted_frames = 0
            frame_metadata_list = []
            video_stem = video_path.stem

            self.logger.info(f"Starting frame extraction from {video_path}")

            for idx, frame_idx in enumerate(frame_indices):
                # Set frame position
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

                # Read frame
                ret, frame = cap.read()
                if not ret:
                    self.logger.warning(f"Failed to read frame {frame_idx}")
                    continue

                # Calculate output filename
                frame_number = extracted_frames + 1
                output_filename = f"{video_stem}_{frame_number:06d}.{OUTPUT_IMAGE_FORMAT}"
                output_path = config.output_folder / output_filename

                # Save frame
                try:
                    cv2.imwrite(
                        str(output_path),
                        frame,
                        [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY],
                    )

                    # Record metadata
                    time_seconds = frame_idx / metadata.fps
                    frame_metadata_list.append(
                        {
                            "filename": output_filename,
                            "frame_index": frame_idx,
                            "time_seconds": time_seconds,
                            "frame_number": frame_number,
                            "kept": True,
                            "blur_score": None,
                            "is_duplicate": False,
                        }
                    )

                    extracted_frames += 1

                    # Call progress callback
                    if on_progress:
                        on_progress(idx + 1, len(frame_indices))

                    self.logger.debug(
                        f"Extracted frame {frame_number}: {output_filename}"
                    )

                except Exception as e:
                    error_msg = f"Error saving frame {frame_idx}: {str(e)}"
                    self.logger.error(error_msg)
                    if on_error:
                        on_error(error_msg)

            cap.release()

            self.logger.info(
                f"Frame extraction complete: {extracted_frames} frames extracted"
            )

            return extracted_frames, frame_metadata_list

        except Exception as e:
            error_msg = f"Error during frame extraction: {str(e)}"
            self.logger.error(error_msg)
            if on_error:
                on_error(error_msg)
            return 0, []
