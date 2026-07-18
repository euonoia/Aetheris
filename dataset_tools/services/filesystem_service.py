"""Filesystem helper service for the dataset pipeline."""

from pathlib import Path
from typing import Tuple

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class FilesystemService:
    def create_folder(self, path: Path) -> Tuple[bool, str]:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True, ""
        except Exception as e:
            logger.error(f"Failed to create folder {path}: {e}")
            return False, str(e)

    def clear_folder(self, path: Path) -> None:
        if path.exists() and path.is_dir():
            for item in path.iterdir():
                if item.is_dir():
                    self._remove_directory(item)
                else:
                    item.unlink()

    def _remove_directory(self, folder: Path) -> None:
        for item in folder.iterdir():
            if item.is_dir():
                self._remove_directory(item)
            else:
                item.unlink()
        folder.rmdir()
