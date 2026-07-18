"""
Dataset organizer module for Dataset Engineering Toolkit.

Organizes extracted frames into structured dataset directories.
"""

import shutil
from pathlib import Path
from typing import Optional, Tuple, List

from utils.logging_utils import get_logger

logger = get_logger(__name__)


class DatasetOrganizer:
    """Organizes extracted frames into categorized folders."""

    def __init__(self) -> None:
        """Initialize dataset organizer."""
        self.logger = get_logger(__name__)

    def create_dataset_structure(
        self,
        base_folder: Path,
        dataset_name: str,
        categories: List[str],
    ) -> Tuple[bool, Optional[str], Optional[Path]]:
        """
        Create dataset folder structure.

        Structure:
        base_folder/
            dataset_name/
                raw_frames/
                    category1/
                    category2/
                    ...
                train/
                    images/
                    labels/
                valid/
                    images/
                    labels/
                test/
                    images/
                    labels/

        Args:
            base_folder: Base folder path
            dataset_name: Dataset name
            categories: List of frame categories

        Returns:
            Tuple of (success, error_message, dataset_path)
        """
        try:
            dataset_path = base_folder / dataset_name
            raw_frames_path = dataset_path / "raw_frames"

            # Create base directories
            dataset_path.mkdir(parents=True, exist_ok=True)
            raw_frames_path.mkdir(parents=True, exist_ok=True)

            # Create category folders
            for category in categories:
                category_folder = raw_frames_path / category
                category_folder.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Created category folder: {category_folder}")

            # Create train/valid/test split folders
            for split in ["train", "valid", "test"]:
                split_path = dataset_path / split
                (split_path / "images").mkdir(parents=True, exist_ok=True)
                (split_path / "labels").mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Created split folder: {split_path}")

            self.logger.info(f"Dataset structure created at: {dataset_path}")
            return True, None, dataset_path

        except Exception as e:
            error_msg = f"Error creating dataset structure: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None

    def organize_frames(
        self,
        frame_metadata_list: List[dict],
        source_folder: Path,
        category: str,
        dataset_path: Path,
        move: bool = False,
    ) -> Tuple[int, Optional[str]]:
        """
        Organize extracted frames into category folder.

        Args:
            frame_metadata_list: List of frame metadata (only kept frames)
            source_folder: Source folder with extracted frames
            category: Category to organize into
            dataset_path: Path to dataset root
            move: If True, move files; if False, copy

        Returns:
            Tuple of (organized_count, error_message)
        """
        try:
            category_folder = dataset_path / "raw_frames" / category

            if not category_folder.exists():
                error_msg = f"Category folder not found: {category_folder}"
                self.logger.error(error_msg)
                return 0, error_msg

            organized_count = 0

            for metadata in frame_metadata_list:
                # Only organize kept frames
                if not metadata.get("kept", True):
                    continue

                filename = metadata.get("filename")
                if not filename:
                    continue

                source_path = source_folder / filename
                target_path = category_folder / filename

                if not source_path.exists():
                    self.logger.warning(f"Source file not found: {source_path}")
                    continue

                try:
                    if move:
                        shutil.move(str(source_path), str(target_path))
                        self.logger.debug(f"Moved: {filename} → {category}")
                    else:
                        shutil.copy2(str(source_path), str(target_path))
                        self.logger.debug(f"Copied: {filename} → {category}")

                    organized_count += 1

                except Exception as e:
                    self.logger.error(f"Error organizing {filename}: {str(e)}")

            self.logger.info(
                f"Organized {organized_count} frames into category: {category}"
            )
            return organized_count, None

        except Exception as e:
            error_msg = f"Error organizing frames: {str(e)}"
            self.logger.error(error_msg)
            return 0, error_msg

    def get_category_folders(
        self, dataset_path: Path
    ) -> Tuple[List[str], Optional[str]]:
        """
        Get list of available category folders.

        Args:
            dataset_path: Path to dataset root

        Returns:
            Tuple of (category_list, error_message)
        """
        try:
            raw_frames_path = dataset_path / "raw_frames"

            if not raw_frames_path.exists():
                return [], f"raw_frames folder not found: {raw_frames_path}"

            categories = sorted(
                [f.name for f in raw_frames_path.iterdir() if f.is_dir()]
            )

            self.logger.info(f"Found {len(categories)} categories: {categories}")
            return categories, None

        except Exception as e:
            error_msg = f"Error getting categories: {str(e)}"
            self.logger.error(error_msg)
            return [], error_msg

    def get_category_stats(
        self, dataset_path: Path
    ) -> Tuple[dict, Optional[str]]:
        """
        Get frame counts for each category.

        Args:
            dataset_path: Path to dataset root

        Returns:
            Tuple of (stats_dict, error_message)
        """
        try:
            raw_frames_path = dataset_path / "raw_frames"

            if not raw_frames_path.exists():
                return {}, f"raw_frames folder not found: {raw_frames_path}"

            stats = {}
            for category_folder in raw_frames_path.iterdir():
                if category_folder.is_dir():
                    frame_count = len(list(category_folder.glob("*")))
                    stats[category_folder.name] = frame_count

            self.logger.info(f"Category statistics: {stats}")
            return stats, None

        except Exception as e:
            error_msg = f"Error getting stats: {str(e)}"
            self.logger.error(error_msg)
            return {}, error_msg
