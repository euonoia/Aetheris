"""
Metadata generation module for Dataset Engineering Toolkit.

Generates CSV metadata files and statistics reports.
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

from utils.logging_utils import get_logger

logger = get_logger(__name__)


class MetadataGenerator:
    """Generates and manages metadata for extracted datasets."""

    def __init__(self) -> None:
        """Initialize metadata generator."""
        self.logger = get_logger(__name__)

    def generate_csv(
        self,
        frame_metadata_list: List[Dict],
        output_folder: Path,
        filename: str = "metadata.csv",
    ) -> Tuple[bool, Optional[str]]:
        """
        Generate metadata CSV file.

        Args:
            frame_metadata_list: List of frame metadata dictionaries
            output_folder: Path to output folder
            filename: CSV filename

        Returns:
            Tuple of (success, error_message)
        """
        try:
            csv_path = output_folder / filename

            # Define CSV columns
            fieldnames = [
                "filename",
                "frame_number",
                "frame_index",
                "time_seconds",
                "blur_score",
                "is_duplicate",
                "kept",
            ]

            with open(csv_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header
                writer.writeheader()

                # Write rows
                for metadata in frame_metadata_list:
                    row = {
                        "filename": metadata.get("filename", ""),
                        "frame_number": metadata.get("frame_number", ""),
                        "frame_index": metadata.get("frame_index", ""),
                        "time_seconds": f"{metadata.get('time_seconds', 0):.2f}",
                        "blur_score": (
                            f"{metadata.get('blur_score', ''):.2f}"
                            if metadata.get("blur_score") is not None
                            else ""
                        ),
                        "is_duplicate": metadata.get("is_duplicate", False),
                        "kept": metadata.get("kept", True),
                    }
                    writer.writerow(row)

            self.logger.info(f"Generated metadata CSV: {csv_path}")
            return True, None

        except Exception as e:
            error_msg = f"Error generating metadata CSV: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def generate_statistics(
        self,
        frame_metadata_list: List[Dict],
        total_extraction_time: float,
        video_filename: str = "video",
    ) -> Dict:
        """
        Calculate and return dataset statistics.

        Args:
            frame_metadata_list: List of frame metadata dictionaries
            total_extraction_time: Total extraction time in seconds
            video_filename: Name of source video

        Returns:
            Dictionary with statistics
        """
        total_frames = len(frame_metadata_list)
        kept_frames = sum(1 for m in frame_metadata_list if m.get("kept", True))
        removed_frames = total_frames - kept_frames

        blurred_frames = sum(1 for m in frame_metadata_list if not m.get("kept", True) and m.get("blur_score") is not None and m.get("blur_score") >= 0)
        duplicate_frames = sum(1 for m in frame_metadata_list if m.get("is_duplicate", False))

        # Calculate average blur score (for kept frames only)
        blur_scores = [
            m.get("blur_score")
            for m in frame_metadata_list
            if m.get("blur_score") is not None and m.get("kept", True)
        ]
        avg_blur_score = sum(blur_scores) / len(blur_scores) if blur_scores else 0

        statistics = {
            "video_filename": video_filename,
            "total_extracted": total_frames,
            "kept_frames": kept_frames,
            "removed_frames": removed_frames,
            "blurred_frames": blurred_frames,
            "duplicate_frames": duplicate_frames,
            "average_blur_score": round(avg_blur_score, 2),
            "extraction_time_seconds": round(total_extraction_time, 2),
        }

        self.logger.info(
            f"Statistics generated: {kept_frames} kept, {removed_frames} removed, "
            f"avg blur score: {avg_blur_score:.2f}"
        )

        return statistics

    def generate_report(
        self,
        frame_metadata_list: List[Dict],
        output_folder: Path,
        total_extraction_time: float,
        video_filename: str = "video",
        filename: str = "statistics.json",
    ) -> Tuple[bool, Optional[str]]:
        """
        Generate statistics report as JSON file.

        Args:
            frame_metadata_list: List of frame metadata dictionaries
            output_folder: Path to output folder
            total_extraction_time: Total extraction time in seconds
            video_filename: Name of source video
            filename: JSON filename

        Returns:
            Tuple of (success, error_message)
        """
        try:
            report_path = output_folder / filename

            # Generate statistics
            statistics = self.generate_statistics(
                frame_metadata_list, total_extraction_time, video_filename
            )

            # Add timestamp
            statistics["generated_at"] = datetime.now().isoformat()

            # Write JSON
            with open(report_path, "w") as f:
                json.dump(statistics, f, indent=2)

            self.logger.info(f"Generated statistics report: {report_path}")
            return True, None

        except Exception as e:
            error_msg = f"Error generating report: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def format_report(self, statistics: Dict) -> str:
        """
        Format statistics dictionary as human-readable report string.

        Args:
            statistics: Statistics dictionary

        Returns:
            Formatted report string
        """
        report = f"""
================== DATASET EXTRACTION REPORT ==================

Source Video:           {statistics.get('video_filename', 'N/A')}
Generated:              {statistics.get('generated_at', 'N/A')}

EXTRACTION RESULTS
─────────────────
Total Extracted:        {statistics.get('total_extracted', 0):,} frames
Kept Frames:            {statistics.get('kept_frames', 0):,} frames
Removed Frames:         {statistics.get('removed_frames', 0):,} frames

QUALITY METRICS
───────────────
Blurred Frames:         {statistics.get('blurred_frames', 0):,} frames
Duplicate Frames:       {statistics.get('duplicate_frames', 0):,} frames
Average Blur Score:     {statistics.get('average_blur_score', 0):.2f}

TIMING
──────
Extraction Time:        {statistics.get('extraction_time_seconds', 0):.2f} seconds

==============================================================
"""
        return report
