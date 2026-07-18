"""Exporter stage for final dataset output creation."""

import csv
from pathlib import Path
from typing import List

from ..models.dataset_record import MetadataRecord
from ..models.processing_result import StageResult
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class ExporterStage:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def run(
        self,
        records: List[MetadataRecord],
        dataset_path: Path,
    ) -> StageResult:
        approved_folder = dataset_path / "approved"
        rejected_folder = dataset_path / "rejected"
        needs_review_folder = dataset_path / "needs_review"

        approved_folder.mkdir(parents=True, exist_ok=True)
        rejected_folder.mkdir(parents=True, exist_ok=True)
        needs_review_folder.mkdir(parents=True, exist_ok=True)

        for record in records:
            if record.extracted_frame.output_path.exists():
                if record.kept:
                    approved_folder.joinpath(record.extracted_frame.filename)
                elif record.is_duplicate:
                    rejected_folder.joinpath(record.extracted_frame.filename)
                else:
                    needs_review_folder.joinpath(record.extracted_frame.filename)

        report_path = dataset_path / "metadata.csv"
        summary_path = dataset_path / "summary.json"
        processed_rows = []

        for record in records:
            processed_rows.append(
                {
                    "filename": record.extracted_frame.filename,
                    "status": "approved" if record.kept else "rejected",
                    "blur_score": record.blur_score,
                    "brightness": record.brightness,
                    "notes": "",
                }
            )

        with open(report_path, "w", newline="") as csv_file:
            writer = csv.DictWriter(report_path.open("w", newline=""), fieldnames=["filename", "status", "blur_score", "brightness", "notes"])
            writer.writeheader()
            writer.writerows(processed_rows)

        try:
            import json
            dataset_summary = {
                "total_frames": len(records),
                "approved": sum(1 for r in records if r.kept),
                "rejected": sum(1 for r in records if not r.kept),
                "average_blur": sum((r.blur_score or 0) for r in records) / len(records) if records else 0,
            }
            with open(summary_path, "w") as summary_file:
                json.dump(dataset_summary, summary_file, indent=2)
        except Exception as e:
            logger.error(f"Failed to write summary.json: {e}")

        log_path = dataset_path / "processing.log"
        log_path.write_text("Pipeline export complete")

        return StageResult(
            stage_name="Export Dataset",
            success=True,
            data={
                "dataset_path": dataset_path,
                "report_path": report_path,
                "summary_path": summary_path,
                "log_path": log_path,
            },
        )
