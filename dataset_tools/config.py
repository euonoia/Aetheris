"""
Configuration module for Dataset Engineering Toolkit.

Centralized configuration for all toolkit components including:
- Default paths and formats
- Quality thresholds
- Processing parameters
- Output settings
"""

from pathlib import Path
from typing import List

# Project root
PROJECT_ROOT = Path(__file__).parent.absolute()

# ==================== PATHS ====================
DEFAULT_OUTPUT_FOLDER = Path.home() / "Aetheris" / "datasets"
DEFAULT_LOGS_FOLDER = PROJECT_ROOT / "logs"

# Supported video formats
SUPPORTED_VIDEO_FORMATS: List[str] = [".mp4", ".avi", ".mov", ".mkv"]

# ==================== BLUR DETECTION ====================
# Laplacian variance threshold
# Lower values = more permissive (more blurry images kept)
# Higher values = more strict (only very sharp images kept)
BLUR_THRESHOLD: float = 100.0

# Minimum blur threshold (user cannot go below)
BLUR_THRESHOLD_MIN: float = 50.0

# Maximum blur threshold (user cannot go above)
BLUR_THRESHOLD_MAX: float = 500.0

# ==================== DUPLICATE DETECTION ====================
# Image similarity threshold (0-1, where 1 = identical)
# If similarity >= threshold, frame is considered a duplicate
DUPLICATE_THRESHOLD: float = 0.95

# Minimum duplicate threshold (user cannot go below)
DUPLICATE_THRESHOLD_MIN: float = 0.80

# Maximum duplicate threshold (user cannot go above)
DUPLICATE_THRESHOLD_MAX: float = 1.00

# ==================== FRAME EXTRACTION ====================
# Default extraction interval (frames)
DEFAULT_EXTRACTION_INTERVAL_FRAMES: int = 30

# Default extraction interval (seconds)
DEFAULT_EXTRACTION_INTERVAL_SECONDS: float = 1.0

# JPEG compression quality (0-100, higher = better quality, larger file)
JPEG_QUALITY: int = 95

# Image format for output
OUTPUT_IMAGE_FORMAT: str = "jpg"

# ==================== DATASET ORGANIZATION ====================
# Default dataset categories
DEFAULT_CATEGORIES: List[str] = ["morning", "afternoon", "rain", "night"]

# ==================== LOGGING ====================
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_NAME = "extraction.log"

# ==================== UI ====================
# Dark theme colors
COLORS = {
    "bg_primary": "#1e1e1e",      # Main background
    "bg_secondary": "#2d2d2d",    # Secondary background (cards, panels)
    "bg_tertiary": "#3d3d3d",     # Tertiary background (hover)
    "fg_primary": "#ffffff",       # Primary foreground (text)
    "fg_secondary": "#b0b0b0",    # Secondary foreground (dim text)
    "accent": "#0078d4",           # Accent color (buttons)
    "accent_hover": "#1084d7",    # Accent hover
    "success": "#27ae60",          # Success (green)
    "warning": "#f39c12",          # Warning (orange)
    "error": "#e74c3c",            # Error (red)
}

# Window dimensions
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800

# Default window size
WINDOW_DEFAULT_WIDTH = 1400
WINDOW_DEFAULT_HEIGHT = 900

# ==================== PERFORMANCE ====================
# Number of threads for blur/duplicate detection
NUM_WORKER_THREADS: int = 4

# Batch size for processing frames
BATCH_SIZE: int = 32

# Maximum video resolution to handle (width, height)
MAX_VIDEO_RESOLUTION: tuple = (4096, 2160)  # 4K

# ==================== VALIDATION ====================
# Maximum file size in GB
MAX_VIDEO_FILE_SIZE_GB: float = 10.0

# Minimum video duration in seconds
MIN_VIDEO_DURATION: float = 1.0
