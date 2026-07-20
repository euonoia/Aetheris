"""Quality review stage integrated into the pipeline."""

from pathlib import Path
from typing import List

from ..models.dataset_record import MetadataRecord
from ..models.processing_result import StageResult
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class QualityReviewStage:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def run(self, records: List[MetadataRecord]) -> StageResult:
        reviewable = [record for record in records if record.kept]
        self.logger.info(f"Quality review stage received {len(reviewable)} records")

        return StageResult(
            stage_name="Quality Review",
            success=True,
            data={"review_records": reviewable},
        )
