"""
Main application UI for Dataset Engineering Toolkit.

Modern desktop interface using CustomTkinter with dark theme.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional, Callable
import tkinter.filedialog as filedialog
import threading
import time

from config import (
    COLORS,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    DEFAULT_OUTPUT_FOLDER,
    BLUR_THRESHOLD,
    DUPLICATE_THRESHOLD,
)
from ui.components import (
    StyledButton,
    StyledLabel,
    StyledFrame,
    ProgressBar,
    StatCard,
    LogPanel,
    InfoPanel,
    InputField,
)
from frame_extractor.extractor import FrameExtractor, ExtractionConfig
from blur_detector.detector import BlurDetector
from duplicate_detector.detector import DuplicateDetector
from metadata.generator import MetadataGenerator
from utils.logging_utils import get_logger
from utils.file_utils import (
    validate_video_file,
    validate_output_folder,
    format_time,
)

logger = get_logger(__name__)


class DatasetToolkitApp(ctk.CTk):
    """Main application window."""

    def __init__(self) -> None:
        """Initialize application."""
        super().__init__()

        # Configure window
        self.title("Dataset Engineering Toolkit - Aetheris")
        self.geometry(f"{WINDOW_DEFAULT_WIDTH}x{WINDOW_DEFAULT_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Set dark theme
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COLORS["bg_primary"])

        # Initialize state
        self.selected_video: Optional[Path] = None
        self.output_folder: Path = DEFAULT_OUTPUT_FOLDER
        self.extraction_running = False
        self.extraction_thread: Optional[threading.Thread] = None
        self.start_time: float = 0

        # Initialize components
        self.extractor = FrameExtractor()
        self.blur_detector = BlurDetector(BLUR_THRESHOLD)
        self.duplicate_detector = DuplicateDetector(DUPLICATE_THRESHOLD)
        self.metadata_generator = MetadataGenerator()

        # Create UI
        self._create_ui()

        logger.info("Application initialized")

    def _create_ui(self) -> None:
        """Create main UI layout."""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left sidebar
        self._create_left_sidebar(main_container)

        # Main content area
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        # Video info panel
        self.info_panel = InfoPanel(content_frame)
        self.info_panel.pack(fill="x", pady=(0, 10))

        # Extraction settings
        self._create_extraction_settings(content_frame)

        # Progress section
        self._create_progress_section(content_frame)

        # Statistics section
        self._create_statistics_section(content_frame)

        # Log panel
        self.log_panel = LogPanel(content_frame, height=150)
        self.log_panel.pack(fill="both", expand=True, pady=10)

        # Configure grid weights
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

    def _create_left_sidebar(self, parent) -> None:
        """Create left sidebar with file selection."""
        sidebar = StyledFrame(parent, width=350)
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        # Title
        title = StyledLabel(
            sidebar,
            text="Dataset Extraction",
            font=("Arial", 14, "bold"),
        )
        title.pack(fill="x", padx=10, pady=10)

        # Video file selection
        section_label = StyledLabel(
            sidebar,
            text="1. SELECT VIDEO",
            style="secondary",
            font=("Arial", 10, "bold"),
        )
        section_label.pack(fill="x", padx=10, pady=(20, 10))

        browse_btn = StyledButton(
            sidebar,
            text="Browse Video File",
            command=self._select_video,
        )
        browse_btn.pack(fill="x", padx=10)

        self.video_label = StyledLabel(
            sidebar,
            text="No file selected",
            style="secondary",
            font=("Arial", 9),
        )
        self.video_label.pack(fill="x", padx=10, pady=5)

        # Output folder selection
        section_label = StyledLabel(
            sidebar,
            text="2. OUTPUT FOLDER",
            style="secondary",
            font=("Arial", 10, "bold"),
        )
        section_label.pack(fill="x", padx=10, pady=(20, 10))

        output_btn = StyledButton(
            sidebar,
            text="Select Output Folder",
            command=self._select_output_folder,
        )
        output_btn.pack(fill="x", padx=10)

        self.output_label = StyledLabel(
            sidebar,
            text=str(self.output_folder.name),
            style="secondary",
            font=("Arial", 9),
        )
        self.output_label.pack(fill="x", padx=10, pady=5)

        # Extraction interval
        section_label = StyledLabel(
            sidebar,
            text="3. EXTRACTION INTERVAL",
            style="secondary",
            font=("Arial", 10, "bold"),
        )
        section_label.pack(fill="x", padx=10, pady=(20, 10))

        # Interval type selector
        interval_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        interval_frame.pack(fill="x", padx=10, pady=5)

        StyledLabel(
            interval_frame,
            text="Interval Type:",
            style="secondary",
            font=("Arial", 9),
        ).pack(side="left", fill="x", expand=True)

        self.interval_type_var = ctk.StringVar(value="seconds")
        type_menu = ctk.CTkOptionMenu(
            interval_frame,
            variable=self.interval_type_var,
            values=["seconds", "frames"],
            fg_color=COLORS["bg_secondary"],
            text_color=COLORS["fg_primary"],
            button_color=COLORS["accent"],
        )
        type_menu.pack(side="right")

        # Interval value
        interval_value_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        interval_value_frame.pack(fill="x", padx=10, pady=5)

        StyledLabel(
            interval_value_frame,
            text="Interval Value:",
            style="secondary",
            font=("Arial", 9),
        ).pack(side="left", fill="x", expand=True)

        self.interval_value_var = ctk.StringVar(value="1.0")
        interval_input = InputField(
            interval_value_frame,
            width=100,
        )
        interval_input.insert(0, "1.0")
        interval_input.pack(side="right")
        self.interval_value_input = interval_input

        # Options
        section_label = StyledLabel(
            sidebar,
            text="4. OPTIONS",
            style="secondary",
            font=("Arial", 10, "bold"),
        )
        section_label.pack(fill="x", padx=10, pady=(20, 10))

        # Blur threshold
        blur_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        blur_frame.pack(fill="x", padx=10, pady=5)

        StyledLabel(
            blur_frame,
            text="Blur Threshold:",
            style="secondary",
            font=("Arial", 9),
        ).pack(side="left", fill="x", expand=True)

        self.blur_threshold_var = ctk.DoubleVar(value=BLUR_THRESHOLD)
        blur_input = InputField(blur_frame, width=100)
        blur_input.insert(0, str(BLUR_THRESHOLD))
        blur_input.pack(side="right")
        self.blur_threshold_input = blur_input

        # Duplicate threshold
        dup_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        dup_frame.pack(fill="x", padx=10, pady=5)

        StyledLabel(
            dup_frame,
            text="Duplicate Threshold:",
            style="secondary",
            font=("Arial", 9),
        ).pack(side="left", fill="x", expand=True)

        self.duplicate_threshold_var = ctk.DoubleVar(value=DUPLICATE_THRESHOLD)
        dup_input = InputField(dup_frame, width=100)
        dup_input.insert(0, str(DUPLICATE_THRESHOLD))
        dup_input.pack(side="right")
        self.duplicate_threshold_input = dup_input

        # Checkboxes
        self.blur_detection_var = ctk.BooleanVar(value=True)
        blur_check = ctk.CTkCheckBox(
            sidebar,
            text="Enable Blur Detection",
            variable=self.blur_detection_var,
            text_color=COLORS["fg_primary"],
        )
        blur_check.pack(fill="x", padx=10, pady=5)

        self.duplicate_detection_var = ctk.BooleanVar(value=True)
        dup_check = ctk.CTkCheckBox(
            sidebar,
            text="Enable Duplicate Detection",
            variable=self.duplicate_detection_var,
            text_color=COLORS["fg_primary"],
        )
        dup_check.pack(fill="x", padx=10, pady=5)

        # Action buttons
        section_label = StyledLabel(
            sidebar,
            text="5. EXTRACTION",
            style="secondary",
            font=("Arial", 10, "bold"),
        )
        section_label.pack(fill="x", padx=10, pady=(20, 10))

        self.start_btn = StyledButton(
            sidebar,
            text="Start Extraction",
            command=self._start_extraction,
            style="success",
        )
        self.start_btn.pack(fill="x", padx=10, pady=5)

        self.cancel_btn = StyledButton(
            sidebar,
            text="Cancel",
            command=self._cancel_extraction,
            style="danger",
            state="disabled",
        )
        self.cancel_btn.pack(fill="x", padx=10, pady=5)

    def _create_extraction_settings(self, parent) -> None:
        """Create extraction settings panel."""
        settings_frame = StyledFrame(parent, title="Extraction Settings")
        settings_frame.pack(fill="x", pady=10)

        # Settings will be shown here during extraction

    def _create_progress_section(self, parent) -> None:
        """Create progress section."""
        progress_frame = StyledFrame(parent, title="Progress")
        progress_frame.pack(fill="x", pady=10)

        # Progress bar
        self.progress_bar = ProgressBar(progress_frame, height=20)
        self.progress_bar.pack(fill="x", padx=10, pady=10)

        # Progress text
        progress_info_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_info_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.progress_text = StyledLabel(
            progress_info_frame,
            text="Ready",
            style="secondary",
            font=("Arial", 9),
        )
        self.progress_text.pack(side="left", fill="x", expand=True)

        self.time_text = StyledLabel(
            progress_info_frame,
            text="—",
            style="secondary",
            font=("Arial", 9),
        )
        self.time_text.pack(side="right")

    def _create_statistics_section(self, parent) -> None:
        """Create statistics section."""
        stats_frame = StyledFrame(parent, title="Statistics")
        stats_frame.pack(fill="x", pady=10)

        # Stats grid
        grid_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=10)

        self.stat_cards = {}
        stats = [
            ("extracted", "Extracted"),
            ("kept", "Kept"),
            ("removed", "Removed"),
            ("blurred", "Blurred"),
            ("duplicates", "Duplicates"),
        ]

        for idx, (key, label) in enumerate(stats):
            card = StatCard(
                grid_frame,
                label=label,
                value="0",
            )
            card.grid(row=0, column=idx, padx=5, sticky="ew")
            self.stat_cards[key] = card

        grid_frame.grid_columnconfigure("all", weight=1)

    def _select_video(self) -> None:
        """Select video file dialog."""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv"),
            ("All files", "*.*"),
        ]

        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=filetypes,
        )

        if file_path:
            video_path = Path(file_path)

            # Validate
            is_valid, error_msg = validate_video_file(video_path)
            if not is_valid:
                self.log_panel.add_log(f"❌ Error: {error_msg}")
                return

            self.selected_video = video_path
            self.video_label.configure(text=video_path.name)
            self.log_panel.add_log(f"✓ Selected: {video_path.name}")

            # Load video metadata
            self._load_video_metadata()

    def _load_video_metadata(self) -> None:
        """Load and display video metadata."""
        if not self.selected_video:
            return

        metadata = self.extractor.get_video_metadata(self.selected_video)

        if metadata:
            self.info_panel.update_info("Filename", self.selected_video.name)
            self.info_panel.update_info("Resolution", f"{metadata.width}x{metadata.height}")
            self.info_panel.update_info("FPS", f"{metadata.fps:.1f}")
            self.info_panel.update_info("Duration", format_time(metadata.duration))
            self.info_panel.update_info("Total Frames", str(metadata.total_frames))

            self.log_panel.add_log(
                f"✓ Loaded metadata: {metadata.total_frames} frames, "
                f"{metadata.fps:.1f} fps, {format_time(metadata.duration)}"
            )

    def _select_output_folder(self) -> None:
        """Select output folder dialog."""
        folder_path = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=str(self.output_folder),
        )

        if folder_path:
            self.output_folder = Path(folder_path)
            self.output_label.configure(text=self.output_folder.name)
            self.log_panel.add_log(f"✓ Output folder set to: {self.output_folder.name}")

    def _start_extraction(self) -> None:
        """Start frame extraction process."""
        if not self.selected_video:
            self.log_panel.add_log("❌ Error: No video selected")
            return

        # Validate inputs
        try:
            interval_value = float(self.interval_value_input.get())
            blur_threshold = float(self.blur_threshold_input.get())
            duplicate_threshold = float(self.duplicate_threshold_input.get())
        except ValueError:
            self.log_panel.add_log("❌ Error: Invalid parameter values")
            return

        # Start extraction in background thread
        self.extraction_running = True
        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")

        self.extraction_thread = threading.Thread(
            target=self._extraction_worker,
            args=(
                self.selected_video,
                interval_value,
                blur_threshold,
                duplicate_threshold,
            ),
            daemon=True,
        )
        self.extraction_thread.start()

        self.log_panel.add_log("Starting extraction...")
        self.start_time = time.time()

    def _extraction_worker(
        self,
        video_path: Path,
        interval_value: float,
        blur_threshold: float,
        duplicate_threshold: float,
    ) -> None:
        """Worker thread for extraction."""
        try:
            # Create extraction config
            config = ExtractionConfig(
                output_folder=self.output_folder / video_path.stem,
                interval_type=self.interval_type_var.get(),
                interval_value=interval_value,
                blur_threshold=blur_threshold,
                remove_duplicates=True,
            )

            # Extract frames
            def on_progress(current, total):
                progress = current / total if total > 0 else 0
                self.progress_bar.set(progress)
                self.progress_text.configure(
                    text=f"Extracting: {current}/{total} frames"
                )
                elapsed = time.time() - self.start_time
                self.time_text.configure(text=format_time(elapsed))

            def on_error(msg):
                self.log_panel.add_log(f"⚠ {msg}")

            extracted, frame_metadata = self.extractor.extract_frames(
                video_path,
                config,
                on_progress=on_progress,
                on_error=on_error,
            )

            if extracted == 0:
                self.log_panel.add_log("❌ Failed to extract frames")
                return

            self.log_panel.add_log(f"✓ Extracted {extracted} frames")

            # Blur detection
            if self.blur_detection_var.get():
                self.log_panel.add_log("Starting blur detection...")
                kept, removed, frame_metadata = self.blur_detector.process_frames(
                    frame_metadata,
                    config.output_folder,
                    blur_threshold,
                )
                self.log_panel.add_log(f"✓ Blur detection: {kept} kept, {removed} removed")
                self.blur_detector.cleanup_blurry_frames(frame_metadata, config.output_folder)

            # Duplicate detection
            if self.duplicate_detection_var.get():
                self.log_panel.add_log("Starting duplicate detection...")
                kept, removed, frame_metadata = self.duplicate_detector.process_frames(
                    frame_metadata,
                    config.output_folder,
                    duplicate_threshold,
                )
                self.log_panel.add_log(f"✓ Duplicate detection: {kept} kept, {removed} removed")
                self.duplicate_detector.cleanup_duplicate_frames(frame_metadata, config.output_folder)

            # Generate metadata and report
            self.metadata_generator.generate_csv(frame_metadata, config.output_folder)
            extraction_time = time.time() - self.start_time
            self.metadata_generator.generate_report(
                frame_metadata,
                config.output_folder,
                extraction_time,
                video_path.stem,
            )

            # Update statistics
            final_kept = sum(1 for m in frame_metadata if m.get("kept", True))
            final_removed = len(frame_metadata) - final_kept
            blurred = sum(1 for m in frame_metadata if m.get("blur_score") is not None and m.get("blur_score") < blur_threshold)
            duplicates = sum(1 for m in frame_metadata if m.get("is_duplicate", False))

            self.stat_cards["extracted"].update_value(str(extracted))
            self.stat_cards["kept"].update_value(str(final_kept))
            self.stat_cards["removed"].update_value(str(final_removed))
            self.stat_cards["blurred"].update_value(str(blurred))
            self.stat_cards["duplicates"].update_value(str(duplicates))

            self.progress_bar.set(1.0)
            self.log_panel.add_log("✓ Extraction complete!")

        except Exception as e:
            self.log_panel.add_log(f"❌ Error: {str(e)}")
            logger.error(f"Extraction error: {str(e)}")

        finally:
            self.extraction_running = False
            self.start_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")

    def _cancel_extraction(self) -> None:
        """Cancel extraction process."""
        self.extraction_running = False
        self.log_panel.add_log("⚠ Extraction cancelled")
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")


def main() -> None:
    """Entry point for application."""
    app = DatasetToolkitApp()
    app.mainloop()


if __name__ == "__main__":
    main()
