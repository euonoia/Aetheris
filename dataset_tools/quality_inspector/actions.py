"""Actions for updating dataset quality inspection status and exporting reports."""

import csv
from pathlib import Path
from typing import Dict, Iterable, List

from .inspector import QualityRecord
from ..utils.file_utils import ensure_folder_exists


def export_inspection_report(
    records: List[QualityRecord],
    destination_folder: Path,
    report_name: str = "inspection_report.csv",
) -> Path:
    destination_folder.mkdir(parents=True, exist_ok=True)
    report_path = destination_folder / report_name

    fieldnames = [
        "filename",
        "status",
        "blur_score",
        "brightness",
        "contrast",
        "sharpness",
        "similarity_score",
        "notes",
    ]

    with open(report_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "filename": record.filename,
                    "status": record.status,
                    "blur_score": f"{record.blur_score:.2f}" if record.blur_score is not None else "",
                    "brightness": f"{record.brightness:.2f}" if record.brightness is not None else "",
                    "contrast": f"{record.contrast:.2f}" if record.contrast is not None else "",
                    "sharpness": f"{record.sharpness:.2f}" if record.sharpness is not None else "",
                    "similarity_score": f"{record.similarity_score:.3f}" if record.similarity_score is not None else "",
                    "notes": record.notes,
                }
            )

    return report_path


def move_records(
    records: Iterable[QualityRecord],
    destination_folder: Path,
    update_status: str,
) -> List[QualityRecord]:
    destination_folder.mkdir(parents=True, exist_ok=True)
    moved: List[QualityRecord] = []

    for record in records:
        if not record.image_path.exists():
            continue
        target_path = destination_folder / record.filename
        try:
            record.image_path.replace(target_path)
            record.image_path = target_path
            record.status = update_status
            moved.append(record)
        except Exception:
            continue

    return moved


def restore_deleted_images(
    records: Iterable[QualityRecord],
    destination_folder: Path,
) -> List[QualityRecord]:
    destination_folder.mkdir(parents=True, exist_ok=True)
    restored: List[QualityRecord] = []

    for record in records:
        if not record.image_path.exists():
            continue
        target_path = destination_folder / record.filename
        try:
            record.image_path.replace(target_path)
            record.image_path = target_path
            record.status = "not_reviewed"
            restored.append(record)
        except Exception:
            continue

    return restored
