"""Dataset organization stage for the processing pipeline."""

from pathlib import Path
from typing import List, Tuple

from ..dataset_organizer.organizer import DatasetOrganizer
from ..models.dataset_record import MetadataRecord
from ..models.processing_result import StageResult
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class OrganizerStage:
    def __init__(self, organizer: DatasetOrganizer) -> None:
        self.organizer = organizer
        self.logger = get_logger(__name__)

    def run(
        self,
        records: List[MetadataRecord],
        base_folder: Path,
        dataset_name: str,
        categories: List[str],
    ) -> StageResult:
        success, error, dataset_path = self.organizer.create_dataset_structure(
            base_folder, dataset_name, categories
        )
        if not success or dataset_path is None:
            return StageResult(
                stage_name="Dataset Organization",
                success=False,
                error_message=error or "Failed to create dataset structure",
            )

        organized_count = 0
        for category in categories:
            count, error = self.organizer.organize_frames(
                [r.__dict__ for r in records],
                base_folder,
                category,
                dataset_path,
                move=False,
            )
            if error:
                self.logger.warning(f"Category organization warning: {error}")
            organized_count += count

        return StageResult(
            stage_name="Dataset Organization",
            success=True,
            data={
                "dataset_path": dataset_path,
                "organized_count": organized_count,
            },
        )
