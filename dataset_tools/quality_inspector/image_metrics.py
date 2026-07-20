"""Image quality metrics used by the Dataset Quality Inspector."""

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np


def load_image_gray(image_path: Path) -> Optional[np.ndarray]:
    try:
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        return image
    except Exception:
        return None


def calculate_blur_score(image_path: Path) -> Optional[float]:
    image = load_image_gray(image_path)
    if image is None:
        return None

    laplacian = cv2.Laplacian(image, cv2.CV_64F)
    return float(laplacian.var())


def calculate_brightness(image_path: Path) -> Optional[float]:
    image = load_image_gray(image_path)
    if image is None:
        return None

    return float(np.mean(image))


def calculate_contrast(image_path: Path) -> Optional[float]:
    image = load_image_gray(image_path)
    if image is None:
        return None

    return float(np.std(image))


def calculate_sharpness(image_path: Path) -> Optional[float]:
    image = load_image_gray(image_path)
    if image is None:
        return None

    gx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(gx**2 + gy**2)
    return float(np.mean(magnitude))


def calculate_histogram(image_path: Path) -> Optional[np.ndarray]:
    image = load_image_gray(image_path)
    if image is None:
        return None

    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist


def calculate_similarity(image_path_a: Path, image_path_b: Path) -> float:
    if image_path_a == image_path_b:
        return 1.0

    hist_a = calculate_histogram(image_path_a)
    hist_b = calculate_histogram(image_path_b)

    if hist_a is None or hist_b is None:
        return 0.0

    similarity = cv2.compareHist(hist_a.astype(np.float32), hist_b.astype(np.float32), cv2.HISTCMP_CORREL)
    return float(np.clip(similarity, -1.0, 1.0))


def resolution_from_image(image_path: Path) -> Optional[Tuple[int, int]]:
    try:
        image = cv2.imread(str(image_path))
        if image is None:
            return None
        return int(image.shape[1]), int(image.shape[0])
    except Exception:
        return None
