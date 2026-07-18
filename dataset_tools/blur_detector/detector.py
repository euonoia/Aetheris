"""
Blur detection module using Laplacian variance method.

Detects blurry frames and optionally filters them out during extraction.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import concurrent.futures

from config import BLUR_THRESHOLD, NUM_WORKER_THREADS
from utils.logging_utils import get_logger

logger = get_logger(__name__)


class BlurDetector:
    """
    Blur detection using Laplacian variance method.

    Lower variance = blurrier image
    Higher variance = sharper image
    """

    def __init__(self, threshold: float = BLUR_THRESHOLD) -> None:
        """
        Initialize blur detector.

        Args:
            threshold: Laplacian variance threshold
        """
        self.threshold = threshold
        self.logger = get_logger(__name__)

    def calculate_blur_score(self, image_path: Path) -> Optional[float]:
        """
        Calculate blur score for an image using Laplacian variance.

        Args:
            image_path: Path to image file

        Returns:
            Blur score (float) or None if failed
        """
        try:
            # Read image in grayscale
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

            if image is None:
                self.logger.warning(f"Failed to read image: {image_path}")
                return None

            # Calculate Laplacian variance
            laplacian = cv2.Laplacian(image, cv2.CV_64F)
            variance = laplacian.var()

            return float(variance)

        except Exception as e:
            self.logger.error(f"Error calculating blur score for {image_path}: {str(e)}")
            return None

    def is_blurry(self, blur_score: float) -> bool:
        """
        Determine if image is blurry based on score.

        Args:
            blur_score: Laplacian variance score

        Returns:
            True if image is blurry (should be removed), False otherwise
        """
        return blur_score < self.threshold

    def process_frames(
        self,
        frame_metadata_list: List[Dict],
        output_folder: Path,
        threshold: Optional[float] = None,
    ) -> Tuple[int, int, List[Dict]]:
        """
        Process frames and mark blurry ones for removal.

        Args:
            frame_metadata_list: List of frame metadata dictionaries
            output_folder: Path to folder containing frames
            threshold: Override blur threshold (if None, uses instance threshold)

        Returns:
            Tuple of (kept_count, removed_count, updated_metadata_list)
        """
        if threshold is not None:
            self.threshold = threshold

        kept_count = 0
        removed_count = 0
        updated_metadata = []

        self.logger.info(f"Starting blur detection on {len(frame_metadata_list)} frames")

        for metadata in frame_metadata_list:
            filename = metadata["filename"]
            image_path = output_folder / filename

            # Calculate blur score
            blur_score = self.calculate_blur_score(image_path)

            if blur_score is None:
                # If we can't read the image, keep it
                metadata["kept"] = True
                metadata["blur_score"] = None
                kept_count += 1
            elif self.is_blurry(blur_score):
                # Image is blurry, mark for removal
                metadata["kept"] = False
                metadata["blur_score"] = blur_score
                removed_count += 1
                self.logger.debug(f"Blurry frame detected: {filename} (score: {blur_score:.2f})")
            else:
                # Image is sharp, keep it
                metadata["kept"] = True
                metadata["blur_score"] = blur_score
                kept_count += 1

            updated_metadata.append(metadata)

        self.logger.info(
            f"Blur detection complete: {kept_count} kept, {removed_count} removed "
            f"(threshold: {self.threshold:.1f})"
        )

        return kept_count, removed_count, updated_metadata

    def cleanup_blurry_frames(self, frame_metadata_list: List[Dict], output_folder: Path) -> int:
        """
        Delete blurry frames from disk.

        Args:
            frame_metadata_list: List of frame metadata with 'kept' field
            output_folder: Path to folder containing frames

        Returns:
            Number of frames deleted
        """
        deleted_count = 0

        for metadata in frame_metadata_list:
            if not metadata.get("kept", True):
                filename = metadata["filename"]
                image_path = output_folder / filename

                try:
                    if image_path.exists():
                        image_path.unlink()
                        deleted_count += 1
                        self.logger.debug(f"Deleted blurry frame: {filename}")
                except Exception as e:
                    self.logger.error(f"Error deleting {filename}: {str(e)}")

        self.logger.info(f"Deleted {deleted_count} blurry frames")
        return deleted_count
