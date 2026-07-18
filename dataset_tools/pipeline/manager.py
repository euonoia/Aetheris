"""Pipeline manager orchestrating dataset preprocessing stages."""
import threading

import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Absolute imports based on Aetheris being in the sys.path
from dataset_tools.dataset_organizer.organizer import DatasetOrganizer
from dataset_tools.duplicate_detector.detector import DuplicateDetector
from dataset_tools.blur_detector.detector import BlurDetector
from dataset_tools.frame_extractor.extractor import FrameExtractor
from dataset_tools.metadata.generator import MetadataGenerator
from dataset_tools.models.dataset_record import DatasetRecord, MetadataRecord, VideoInfo, ExtractedFrame
from dataset_tools.models.processing_result import PipelineStatistics, StageResult
from dataset_tools.pipeline.blur_filter import BlurFilterStage
from dataset_tools.pipeline.duplicate_filter import DuplicateFilterStage
from dataset_tools.pipeline.extraction import ExtractionStage
from dataset_tools.pipeline.exporter import ExporterStage
from dataset_tools.pipeline.metadata import MetadataStage
from dataset_tools.pipeline.organizer import OrganizerStage
from dataset_tools.pipeline.quality_review import QualityReviewStage
from dataset_tools.services.image_service import ImageService
from dataset_tools.services.filesystem_service import FilesystemService
from dataset_tools.services.video_service import VideoService
from dataset_tools.utils.logging_utils import get_logger

logger = get_logger(__name__)


class PipelineManager:
    """Orchestrates a full dataset preprocessing pipeline."""

    def __init__(self) -> None:
        self.video_service = VideoService()
        self.extraction_stage = ExtractionStage(self.video_service.extractor)
        self.blur_stage = BlurFilterStage(BlurDetector())
        self.duplicate_stage = DuplicateFilterStage(DuplicateDetector())
        self.metadata_stage = MetadataStage(MetadataGenerator())
        self.organizer_stage = OrganizerStage(DatasetOrganizer())
        self.quality_stage = QualityReviewStage()
        self.export_stage = ExporterStage()
        self.image_service = ImageService()
        self.fs_service = FilesystemService()

        self.current_stage: str = "Idle"
        self.stage_status: Dict[str, str] = {}
        self.stage_results: Dict[str, StageResult] = {}
        self.error_message: Optional[str] = None
        self.paused: bool = False
        self.cancel_requested: bool = False
        self.checkpoint_index: int = 0
        self.pipeline_thread: Optional[threading.Thread] = None
        self.pipeline_data: Dict[str, object] = {}
        self.status_callbacks: List[Callable[[], None]] = []

        self.pipeline_steps = [
            "Video Loaded",
            "Metadata Read",
            "Frames Extracted",
            "Blur Removed",
            "Duplicates Removed",
            "Metadata Generated",
            "Dataset Organized",
            "Quality Review",
            "Export Complete",
        ]
        self._reset_statuses()

    def _reset_statuses(self) -> None:
        self.stage_status = {step: "pending" for step in self.pipeline_steps}
        self.stage_results.clear()
        self.error_message = None
        self.paused = False
        self.cancel_requested = False
        self.checkpoint_index = 0
        self.pipeline_data.clear()

    def add_status_callback(self, callback: Callable[[], None]) -> None:
        self.status_callbacks.append(callback)

    def _emit_status(self) -> None:
        for callback in self.status_callbacks:
            try:
                callback()
            except Exception as e:
                logger.warning(f"Status callback failed: {e}")

    def start(
        self,
        video_path: Path,
        output_folder: Path,
        interval_type: str,
        interval_value: float,
        blur_threshold: float,
        duplicate_threshold: float,
        dataset_name: str,
        categories: List[str],
        on_progress: Optional[Callable[[str, float], None]] = None,
    ) -> None:
        self._reset_statuses()
        self.current_stage = "Video Loaded"
        self.pipeline_data["video_path"] = video_path
        self.pipeline_data["output_folder"] = output_folder
        self.pipeline_data["interval_type"] = interval_type
        self.pipeline_data["interval_value"] = interval_value
        self.pipeline_data["blur_threshold"] = blur_threshold
        self.pipeline_data["duplicate_threshold"] = duplicate_threshold
        self.pipeline_data["dataset_name"] = dataset_name
        self.pipeline_data["categories"] = categories

        self.pipeline_thread = threading.Thread(
            target=self._run_pipeline,
            args=(on_progress,),
            daemon=True,
        )
        self.pipeline_thread.start()

    def _run_pipeline(self, on_progress: Optional[Callable[[str, float], None]]) -> None:
        try:
            self._set_stage("Video Loaded", "completed")
            video_info = self.video_service.get_video_info(self.pipeline_data["video_path"])
            if video_info is None:
                raise RuntimeError("Failed to read video metadata")
            self.pipeline_data["video_info"] = video_info
            self._set_stage("Metadata Read", "completed")

            extraction_result = self.extraction_stage.run(
                self.pipeline_data["video_path"],
                self.pipeline_data["output_folder"],
                self.pipeline_data["interval_type"],
                self.pipeline_data["interval_value"],
                on_progress=self._extract_progress(on_progress),
                on_error=self._stage_error,
            )
            if not extraction_result.success:
                raise RuntimeError(extraction_result.error_message or "Extraction failed")
            self._set_stage("Frames Extracted", "completed")
            self.pipeline_data["extracted_frames"] = extraction_result.data["extracted_frames"]

            blur_result = self.blur_stage.run(
                extraction_result.data["extracted_frames"],
                self.pipeline_data["blur_threshold"],
                self.pipeline_data["output_folder"],
            )
            if not blur_result.success:
                raise RuntimeError(blur_result.error_message or "Blur detection failed")
            self._set_stage("Blur Removed", "completed")
            self.pipeline_data["filtered_frames"] = blur_result.data["filtered_frames"]

            duplicate_result = self.duplicate_stage.run(
                self.pipeline_data["filtered_frames"],
                self.pipeline_data["duplicate_threshold"],
            )
            if not duplicate_result.success:
                raise RuntimeError(duplicate_result.error_message or "Duplicate detection failed")
            self._set_stage("Duplicates Removed", "completed")
            self.pipeline_data["filtered_frames"] = duplicate_result.data["filtered_frames"]

            metadata_result = self.metadata_stage.run(
                self.pipeline_data["filtered_frames"],
                self.pipeline_data["output_folder"],
            )
            if not metadata_result.success:
                raise RuntimeError(metadata_result.error_message or "Metadata generation failed")
            self._set_stage("Metadata Generated", "completed")
            self.pipeline_data["metadata_records"] = metadata_result.data["metadata_records"]

            organizer_result = self.organizer_stage.run(
                self.pipeline_data["metadata_records"],
                self.pipeline_data["output_folder"],
                self.pipeline_data["dataset_name"],
                self.pipeline_data["categories"],
            )
            if not organizer_result.success:
                raise RuntimeError(organizer_result.error_message or "Dataset organization failed")
            self._set_stage("Dataset Organized", "completed")
            self.pipeline_data["dataset_path"] = organizer_result.data["dataset_path"]

            quality_result = self.quality_stage.run(self.pipeline_data["metadata_records"])
            self._set_stage("Quality Review", "pending")
            self.pipeline_data["review_records"] = quality_result.data["review_records"]

            self._set_stage("Export Complete", "pending")
            self._emit_status()

        except Exception as e:
            logger.error(f"PipelineManager error: {e}")
            self.error_message = str(e)
            self.paused = True
            self._emit_status()

    def _extract_progress(self, on_progress: Optional[Callable[[str, float], None]]) -> Optional[Callable[[int, int], None]]:
        if on_progress is None:
            return None

        def callback(current: int, total: int) -> None:
            if self.cancel_requested:
                return
            progress = float(current) / float(total) if total else 0.0
            on_progress("Frames Extracted", progress)

        return callback

    def _stage_error(self, message: str) -> None:
        logger.warning(f"Pipeline stage warning: {message}")
        self.error_message = message

    def _set_stage(self, stage_name: str, status: str) -> None:
        self.stage_status[stage_name] = status
        self.current_stage = stage_name
        self._emit_status()

    def request_cancel(self) -> None:
        self.cancel_requested = True
        self.paused = True
        self.error_message = "Pipeline cancelled by user"
        self._emit_status()

    def resume(self) -> None:
        if not self.paused or self.error_message is None:
            return
        self.paused = False
        self.error_message = None
        self._run_pipeline(None)

    def get_summary(self) -> PipelineStatistics:
        metadata_records = self.pipeline_data.get("metadata_records", [])
        total_frames = len(self.pipeline_data.get("extracted_frames", []))
        kept_frames = sum(1 for record in metadata_records if record.kept)
        removed_frames = total_frames - kept_frames
        blurred_frames = sum(1 for record in self.pipeline_data.get("filtered_frames", []) if record.blur_score is not None and not record.kept)
        duplicate_frames = sum(1 for record in self.pipeline_data.get("filtered_frames", []) if record.is_duplicate)
        average_blur = sum((record.blur_score or 0.0) for record in metadata_records) / len(metadata_records) if metadata_records else 0.0
        average_brightness = sum((record.brightness or 0.0) for record in metadata_records) / len(metadata_records) if metadata_records else 0.0
        average_resolution = sum((record.resolution[0] * record.resolution[1]) for record in metadata_records) / len(metadata_records) if metadata_records else 0.0
        return PipelineStatistics(
            total_frames=total_frames,
            extracted_frames=total_frames,
            kept_frames=kept_frames,
            removed_frames=removed_frames,
            blurred_frames=blurred_frames,
            duplicate_frames=duplicate_frames,
            average_blur=average_blur,
            average_brightness=average_brightness,
            average_resolution=average_resolution,
            processing_time_seconds=0.0,
        )

    def get_stage_status(self) -> Dict[str, str]:
        return self.stage_status.copy()

    def get_review_records(self) -> List[MetadataRecord]:
        return list(self.pipeline_data.get("review_records", []))

    def set_record_status(self, filename: str, status: str) -> None:
        records = self.pipeline_data.get("metadata_records", [])
        for record in records:
            if record.extracted_frame.filename == filename:
                record.status = status
                break

    def get_dataset_path(self) -> Optional[Path]:
        return self.pipeline_data.get("dataset_path")
