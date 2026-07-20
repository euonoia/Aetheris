"""Metadata generation stage for the dataset processing pipeline."""

from pathlib import Path
from typing import List, Optional, Tuple

from ..metadata.generator import MetadataGenerator
from ..models.dataset_record import FilteredFrame, MetadataRecord
from ..models.processing_result import StageResult
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class MetadataStage:
    def __init__(self, generator: MetadataGenerator) -> None:
        self.generator = generator
        self.logger = get_logger(__name__)

    def run(
        self,
        frames: List[FilteredFrame],
        output_folder: Path,
    ) -> StageResult:
        metadata_records: List[MetadataRecord] = []
        total_blur = 0.0
        total_brightness = 0.0
        count_quality = 0

        for filtered in frames:
            if not filtered.kept:
                continue

            frame_path = filtered.extracted_frame.output_path
            resolution = (0, 0)
            file_size = 0

            if frame_path.exists():
                image = frame_path
                resolution = (0, 0)
                try:
                    import cv2
                    img = cv2.imread(str(frame_path))
                    if img is not None:
                        resolution = (int(img.shape[1]), int(img.shape[0]))
                    file_size = frame_path.stat().st_size
                except Exception:
                    pass

            brightness = self._estimate_brightness(frame_path)
            contrast = self._estimate_contrast(frame_path)
            sharpness = self._estimate_sharpness(frame_path)

            metadata_records.append(
                MetadataRecord(
                    extracted_frame=filtered.extracted_frame,
                    blur_score=filtered.blur_score,
                    is_duplicate=filtered.is_duplicate,
                    kept=filtered.kept,
                    brightness=brightness,
                    contrast=contrast,
                    sharpness=sharpness,
                    resolution=resolution,
                    file_size_bytes=file_size,
                )
            )

            if brightness is not None:
                total_brightness += brightness
                count_quality += 1
            if filtered.blur_score is not None:
                total_blur += filtered.blur_score

        self.generator.generate_csv(
            [
                {
                    "filename": record.extracted_frame.filename,
                    "frame_index": record.extracted_frame.frame_index,
                    "frame_number": record.extracted_frame.frame_number,
                    "time_seconds": record.extracted_frame.time_seconds,
                    "blur_score": record.blur_score,
                    "is_duplicate": record.is_duplicate,
                    "kept": record.kept,
                }
                for record in metadata_records
            ],
            output_folder,
        )

        self.generator.generate_report(
            [
                {
                    "filename": record.extracted_frame.filename,
                    "frame_index": record.extracted_frame.frame_index,
                    "frame_number": record.extracted_frame.frame_number,
                    "time_seconds": record.extracted_frame.time_seconds,
                    "blur_score": record.blur_score,
                    "is_duplicate": record.is_duplicate,
                    "kept": record.kept,
                }
                for record in metadata_records
            ],
            output_folder,
            total_extraction_time=0.0,
            video_filename=output_folder.name,
        )

        average_blur = total_blur / len(metadata_records) if metadata_records else 0.0
        average_brightness = total_brightness / count_quality if count_quality else 0.0

        return StageResult(
            stage_name="Metadata Generation",
            success=True,
            data={
                "metadata_records": metadata_records,
                "average_blur": average_blur,
                "average_brightness": average_brightness,
            },
        )

    def _estimate_brightness(self, image_path: Path) -> Optional[float]:
        try:
            import cv2
            img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            return float(img.mean()) if img is not None else None
        except Exception:
            return None

    def _estimate_contrast(self, image_path: Path) -> Optional[float]:
        try:
            import cv2
            img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            return float(img.std()) if img is not None else None
        except Exception:
            return None

    def _estimate_sharpness(self, image_path: Path) -> Optional[float]:
        try:
            import cv2
            img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                return None
            gx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
            return float((gx**2 + gy**2).mean())
        except Exception:
            return None
