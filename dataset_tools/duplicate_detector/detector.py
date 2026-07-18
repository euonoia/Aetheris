"""
Duplicate detection module for Dataset Engineering Toolkit.

Detects duplicate or near-duplicate frames using image comparison.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from itertools import combinations

from config import DUPLICATE_THRESHOLD
from utils.logging_utils import get_logger

logger = get_logger(__name__)


class DuplicateDetector:
    """
    Duplicate frame detection using image similarity comparison.

    Uses structural similarity index (SSIM) or histogram comparison.
    """

    def __init__(self, threshold: float = DUPLICATE_THRESHOLD) -> None:
        """
        Initialize duplicate detector.

        Args:
            threshold: Similarity threshold (0-1, higher = stricter)
        """
        self.threshold = threshold
        self.logger = get_logger(__name__)

    def calculate_similarity(self, image1: np.ndarray, image2: np.ndarray) -> float:
        """
        Calculate similarity between two images using histogram comparison.

        Args:
            image1: First image (numpy array)
            image2: Second image (numpy array)

        Returns:
            Similarity score (0-1, where 1 = identical)
        """
        try:
            # Convert to grayscale if needed
            if len(image1.shape) == 3:
                image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            if len(image2.shape) == 3:
                image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

            # Ensure same size
            if image1.shape != image2.shape:
                image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

            # Calculate histogram
            hist1 = cv2.calcHist([image1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([image2], [0], None, [256], [0, 256])

            # Normalize histograms
            hist1 = cv2.normalize(hist1, hist1).flatten()
            hist2 = cv2.normalize(hist2, hist2).flatten()

            # Compare histograms using correlation
            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

            return float(similarity)

        except Exception as e:
            self.logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0

    def load_image(self, image_path: Path) -> Optional[np.ndarray]:
        """
        Load image from file.

        Args:
            image_path: Path to image

        Returns:
            Image array or None if failed
        """
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                self.logger.warning(f"Failed to load image: {image_path}")
                return None
            return image
        except Exception as e:
            self.logger.error(f"Error loading image {image_path}: {str(e)}")
            return None

    def process_frames(
        self,
        frame_metadata_list: List[Dict],
        output_folder: Path,
        threshold: Optional[float] = None,
    ) -> Tuple[int, int, List[Dict]]:
        """
        Detect and mark duplicate frames.

        Uses sequential comparison (each frame compared to previous frame).
        This is more efficient than comparing all pairs.

        Args:
            frame_metadata_list: List of frame metadata dictionaries
            output_folder: Path to folder containing frames
            threshold: Override duplicate threshold (if None, uses instance threshold)

        Returns:
            Tuple of (kept_count, duplicates_count, updated_metadata_list)
        """
        if threshold is not None:
            self.threshold = threshold

        kept_count = 0
        duplicates_count = 0
        updated_metadata = []

        self.logger.info(
            f"Starting duplicate detection on {len(frame_metadata_list)} frames "
            f"(threshold: {self.threshold:.2f})"
        )

        prev_image = None
        prev_kept = False

        for idx, metadata in enumerate(frame_metadata_list):
            filename = metadata["filename"]
            image_path = output_folder / filename

            # Load current image
            current_image = self.load_image(image_path)

            if current_image is None:
                # If can't load, assume not duplicate and keep
                metadata["is_duplicate"] = False
                kept_count += 1
                prev_image = current_image
                prev_kept = True
                updated_metadata.append(metadata)
                continue

            # Check if duplicate of previous frame
            is_duplicate = False
            if prev_image is not None and prev_kept:
                similarity = self.calculate_similarity(prev_image, current_image)

                if similarity >= self.threshold:
                    is_duplicate = True
                    duplicates_count += 1
                    self.logger.debug(
                        f"Duplicate detected: {filename} "
                        f"(similarity: {similarity:.4f} >= {self.threshold:.4f})"
                    )
                else:
                    kept_count += 1
            else:
                kept_count += 1

            metadata["is_duplicate"] = is_duplicate

            # Set kept status based on duplicate
            if metadata.get("kept", True):
                metadata["kept"] = not is_duplicate
                if is_duplicate:
                    # Update kept count if this was previously marked as kept
                    if not metadata.get("is_duplicate", False):
                        kept_count -= 1

            updated_metadata.append(metadata)

            prev_image = current_image
            prev_kept = not is_duplicate

        self.logger.info(
            f"Duplicate detection complete: {len(frame_metadata_list) - duplicates_count} "
            f"unique frames, {duplicates_count} duplicates removed"
        )

        return len(frame_metadata_list) - duplicates_count, duplicates_count, updated_metadata

    def cleanup_duplicate_frames(self, frame_metadata_list: List[Dict], output_folder: Path) -> int:
        """
        Delete duplicate frames from disk.

        Args:
            frame_metadata_list: List of frame metadata with 'is_duplicate' field
            output_folder: Path to folder containing frames

        Returns:
            Number of frames deleted
        """
        deleted_count = 0

        for metadata in frame_metadata_list:
            if metadata.get("is_duplicate", False):
                filename = metadata["filename"]
                image_path = output_folder / filename

                try:
                    if image_path.exists():
                        image_path.unlink()
                        deleted_count += 1
                        self.logger.debug(f"Deleted duplicate frame: {filename}")
                except Exception as e:
                    self.logger.error(f"Error deleting {filename}: {str(e)}")

        self.logger.info(f"Deleted {deleted_count} duplicate frames")
        return deleted_count
