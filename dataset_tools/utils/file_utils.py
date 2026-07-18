"""
File utilities for Dataset Engineering Toolkit.

Provides file validation, handling, and utility functions.
"""

from pathlib import Path
from typing import Optional, Tuple
import os

from config import (
    SUPPORTED_VIDEO_FORMATS,
    MAX_VIDEO_FILE_SIZE_GB,
)


def validate_video_file(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate if file is a supported video format.

    Args:
        file_path: Path to the video file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    if not file_path.is_file():
        return False, f"Path is not a file: {file_path}"

    # Check file extension
    if file_path.suffix.lower() not in SUPPORTED_VIDEO_FORMATS:
        formats = ", ".join(SUPPORTED_VIDEO_FORMATS)
        return False, f"Unsupported format. Supported: {formats}"

    # Check file size
    file_size_gb = file_path.stat().st_size / (1024 ** 3)
    if file_size_gb > MAX_VIDEO_FILE_SIZE_GB:
        return False, f"File too large: {file_size_gb:.2f}GB (max: {MAX_VIDEO_FILE_SIZE_GB}GB)"

    return True, None


def validate_output_folder(folder_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate output folder is writable.

    Args:
        folder_path: Path to output folder

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)

        if not os.access(folder_path, os.W_OK):
            return False, f"No write permission for: {folder_path}"

        return True, None
    except Exception as e:
        return False, f"Error validating folder: {str(e)}"


def ensure_folder_exists(folder_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Ensure folder exists and is writable.

    Args:
        folder_path: Path to folder

    Returns:
        Tuple of (success, error_message)
    """
    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        return True, None
    except Exception as e:
        return False, f"Failed to create folder: {str(e)}"


def get_safe_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"|?*\\/'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')

    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Format byte size to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_time(seconds: float) -> str:
    """
    Format seconds to HH:MM:SS format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
