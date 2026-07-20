"""Image quality utility service for the dataset pipeline."""

from pathlib import Path
from typing import Optional, Tuple

import cv2

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class ImageService:
    def load_gray(self, image_path: Path) -> Optional[object]:
        try:
            return cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        except Exception as e:
            logger.warning(f"Failed to load image grayscale: {e}")
            return None

    def calculate_blur_score(self, image_path: Path) -> Optional[float]:
        image = self.load_gray(image_path)
        if image is None:
            return None
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        return float(laplacian.var())

    def calculate_brightness(self, image_path: Path) -> Optional[float]:
        image = self.load_gray(image_path)
        if image is None:
            return None
        return float(image.mean())

    def calculate_contrast(self, image_path: Path) -> Optional[float]:
        image = self.load_gray(image_path)
        if image is None:
            return None
        return float(image.std())

    def calculate_sharpness(self, image_path: Path) -> Optional[float]:
        image = self.load_gray(image_path)
        if image is None:
            return None
        gx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = (gx**2 + gy**2) ** 0.5
        return float(magnitude.mean())

    def get_resolution(self, image_path: Path) -> Optional[Tuple[int, int]]:
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            return int(image.shape[1]), int(image.shape[0])
        except Exception as e:
            logger.warning(f"Failed to load image resolution: {e}")
            return None

    def get_file_size(self, image_path: Path) -> Optional[int]:
        try:
            return image_path.stat().st_size
        except Exception as e:
            logger.warning(f"Failed to get file size: {e}")
            return None
