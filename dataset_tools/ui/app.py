"""
Main application UI for Dataset Engineering Toolkit.

Utilitarian desktop interface optimized for information density and technical observability.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional, Callable, Dict, List
import tkinter.filedialog as filedialog
import threading
import time

from config import (
    COLORS,
    DEFAULT_CATEGORIES,
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
from pipeline.manager import PipelineManager
from models.dataset_record import MetadataRecord
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

        # Configure window base options
        self.title("Dataset Engineering Toolkit - Core Engine")
        self.geometry(f"{WINDOW_DEFAULT_WIDTH}x{WINDOW_DEFAULT_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Set unified dark style context
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COLORS["bg_primary"])

        # Initialize core runtime states
        self.selected_video: Optional[Path] = None
        self.output_folder: Path = DEFAULT_OUTPUT_FOLDER
        self.extraction_running = False
        self.extraction_thread: Optional[threading.Thread] = None
        self.start_time: float = 0

        # Instantiate the centralized pipeline manager
        self.pipeline_manager = PipelineManager()
        self.pipeline_manager.add_status_callback(self._on_pipeline_status_update)

        self.review_records: List[MetadataRecord] = []
        self.review_index: int = 0

        # Build structural developer dashboard
        self._create_ui()

        # Initialize parameter fields from preset baselines
        self._apply_profile_presets(self.profile_var.get())

        logger.info("Application context fully initialized")

    def _create_ui(self) -> None:
        """Construct a high-density, side-by-side utility layout."""
        # Top-level window container grid
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=12, pady=12)
        
        main_container.grid_columnconfigure(0, weight=1, minsize=380)  # Controls Matrix
        main_container.grid_columnconfigure(1, weight=2)              # Monitoring Matrix
        main_container.grid_rowconfigure(0, weight=1)

        # Column Layout Split
        config_column = ctk.CTkFrame(main_container, fg_color="transparent")
        config_column.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        telemetry_column = ctk.CTkFrame(main_container, fg_color="transparent")
        telemetry_column.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # --- LEFT COLUMN: System Inputs & Option Matrix ---
        self._build_io_section(config_column)
        self._build_parameter_section(config_column)
        self._build_execution_section(config_column)

        # --- RIGHT COLUMN: Execution Telemetry & Diagnostics ---
        # 1. Video Source Properties
        self.info_panel = InfoPanel(telemetry_column)
        self.info_panel.pack(fill="x", pady=(0, 6))

        # 2. Pipeline Real-time Counters
        self._create_statistics_section(telemetry_column)

        # 3. Thread Process Trackers
        self._create_progress_section(telemetry_column)
        # 4. Embedded Quality Review Panel
        self._create_review_section(telemetry_column)

        # 5. Standard Output Log Engine Panel
        self.log_panel = LogPanel(telemetry_column, height=260)
        self.log_panel.pack(fill="both", expand=True, pady=(6, 0))

    def _build_io_section(self, parent) -> None:
        """I/O path and environment parameter selectors."""
        frame = StyledFrame(parent, title="1. FILE SYSTEM CONFIGURATION")
        frame.pack(fill="x", pady=(0, 6))

        # Video source input block
        v_frame = ctk.CTkFrame(frame, fg_color="transparent")
        v_frame.pack(fill="x", padx=10, pady=4)
        browse_btn = StyledButton(v_frame, text="Source Video", command=self._select_video, width=110)
        browse_btn.pack(side="left")
        self.video_label = StyledLabel(v_frame, text="No source tracking target designated", style="secondary", font=("Arial", 9))
        self.video_label.pack(side="left", padx=10, fill="x", expand=True)

        # Output folder target block
        o_frame = ctk.CTkFrame(frame, fg_color="transparent")
        o_frame.pack(fill="x", padx=10, pady=4)
        output_btn = StyledButton(o_frame, text="Output Directory", command=self._select_output_folder, width=110)
        output_btn.pack(side="left")
        self.output_label = StyledLabel(o_frame, text=str(self.output_folder.name), style="secondary", font=("Arial", 9))
        self.output_label.pack(side="left", padx=10, fill="x", expand=True)

        # Operational presets pipeline matrix selector
        p_frame = ctk.CTkFrame(frame, fg_color="transparent")
        p_frame.pack(fill="x", padx=10, pady=(6, 8))
        StyledLabel(p_frame, text="Target Profile Preset:", style="secondary", font=("Arial", 9)).pack(side="left")
        
        self.profile_var = ctk.StringVar(value="Fluid Traffic / Day")
        profile_menu = ctk.CTkOptionMenu(
            p_frame,
            variable=self.profile_var,
            values=["Fluid Traffic / Day", "Congested / Rush Hour", "Night / Low-Light", "High-Speed / Dashcam"],
            fg_color=COLORS["bg_secondary"],
            text_color=COLORS["fg_primary"],
            button_color=COLORS["accent"],
            command=self._apply_profile_presets,
            width=160
        )
        profile_menu.pack(side="right")

    def _build_parameter_section(self, parent) -> None:
        """Pipeline thresholds and processing flags execution parameters."""
        frame = StyledFrame(parent, title="2. INTERPOLATION & PIPELINE THRESHOLDS")
        frame.pack(fill="x", pady=6)

        # Sampling unit calculation choice
        it_frame = ctk.CTkFrame(frame, fg_color="transparent")
        it_frame.pack(fill="x", padx=10, pady=4)
        StyledLabel(it_frame, text="Interval Evaluation Unit:", style="secondary", font=("Arial", 9)).pack(side="left")
        self.interval_type_var = ctk.StringVar(value="seconds")
        type_menu = ctk.CTkOptionMenu(
            it_frame,
            variable=self.interval_type_var,
            values=["seconds", "frames"],
            fg_color=COLORS["bg_secondary"],
            text_color=COLORS["fg_primary"],
            button_color=COLORS["accent"],
            width=100
        )
        type_menu.pack(side="right")

        # Sampling numerical frequency scalar
        iv_frame = ctk.CTkFrame(frame, fg_color="transparent")
        iv_frame.pack(fill="x", padx=10, pady=4)
        StyledLabel(iv_frame, text="Interval Unit Value:", style="secondary", font=("Arial", 9)).pack(side="left")
        self.interval_value_var = ctk.StringVar(value="1.0")
        self.interval_value_input = InputField(iv_frame, width=100)
        self.interval_value_input.insert(0, "1.0")
        self.interval_value_input.pack(side="right")

        # Laplacians edge variance analysis limit boundary
        b_frame = ctk.CTkFrame(frame, fg_color="transparent")
        b_frame.pack(fill="x", padx=10, pady=4)
        StyledLabel(b_frame, text="Blur Variance Cutoff:", style="secondary", font=("Arial", 9)).pack(side="left")
        self.blur_threshold_var = ctk.DoubleVar(value=BLUR_THRESHOLD)
        self.blur_threshold_input = InputField(b_frame, width=100)
        self.blur_threshold_input.insert(0, str(BLUR_THRESHOLD))
        self.blur_threshold_input.pack(side="right")

        # Perceptual hash or comparative match tolerance boundary
        d_frame = ctk.CTkFrame(frame, fg_color="transparent")
        d_frame.pack(fill="x", padx=10, pady=4)
        StyledLabel(d_frame, text="Duplicate Match Limit (%):", style="secondary", font=("Arial", 9)).pack(side="left")
        self.duplicate_threshold_var = ctk.DoubleVar(value=DUPLICATE_THRESHOLD)
        self.duplicate_threshold_input = InputField(d_frame, width=100)
        self.duplicate_threshold_input.insert(0, str(DUPLICATE_THRESHOLD))
        self.duplicate_threshold_input.pack(side="right")

        # Stage filter evaluation state switches
        cb_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cb_frame.pack(fill="x", padx=10, pady=(6, 8))
        
        self.blur_detection_var = ctk.BooleanVar(value=True)
        blur_check = ctk.CTkCheckBox(cb_frame, text="Blur Filter Module", variable=self.blur_detection_var, text_color=COLORS["fg_primary"], font=("Arial", 9))
        blur_check.pack(side="left", expand=True, anchor="w")

        self.duplicate_detection_var = ctk.BooleanVar(value=True)
        dup_check = ctk.CTkCheckBox(cb_frame, text="Duplicate Filter Module", variable=self.duplicate_detection_var, text_color=COLORS["fg_primary"], font=("Arial", 9))
        dup_check.pack(side="left", expand=True, anchor="w")

    def _build_execution_section(self, parent) -> None:
        """Pipeline runtime triggers."""
        frame = StyledFrame(parent, title="3. PIPELINE CONTROLS")
        frame.pack(fill="x", pady=(6, 0))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)

        self.start_btn = StyledButton(btn_frame, text="Execute Engine Process", command=self._start_extraction, style="success")
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.cancel_btn = StyledButton(btn_frame, text="Abort Processing", command=self._cancel_extraction, style="danger", state="disabled")
        self.cancel_btn.pack(side="right", fill="x", expand=True, padx=(4, 0))

    def _create_statistics_section(self, parent) -> None:
        """Create telemetry live statistical telemetry metrics dashboard grid."""
        stats_frame = StyledFrame(parent, title="Live Operational Metrics Summary")
        stats_frame.pack(fill="x", pady=(0, 6))

        grid_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=(4, 10))

        self.stat_cards = {}
        stats = [
            ("extracted", "Frames Parsed"),
            ("kept", "Passed Filters"),
            ("removed", "Dropped (Total)"),
            ("blurred", "Blur Rejections"),
            ("duplicates", "Dup Rejections"),
        ]

        for idx, (key, label) in enumerate(stats):
            card = StatCard(grid_frame, label=label, value="0")
            card.grid(row=0, column=idx, padx=4, sticky="ew")
            self.stat_cards[key] = card

        grid_frame.grid_columnconfigure("all", weight=1)

    def _create_progress_section(self, parent) -> None:
        """Processing track bar instrumentation."""
        progress_frame = StyledFrame(parent, title="Thread Runtime Metrics Tracker")
        progress_frame.pack(fill="x", pady=6)

        self.progress_bar = ProgressBar(progress_frame, height=14)
        self.progress_bar.pack(fill="x", padx=10, pady=(8, 6))

        progress_info_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_info_frame.pack(fill="x", padx=10, pady=(0, 8))

        self.progress_text = StyledLabel(progress_info_frame, text="Pipeline Thread IDLE", style="secondary", font=("Arial", 9))
        self.progress_text.pack(side="left", fill="x", expand=True)

        self.time_text = StyledLabel(progress_info_frame, text="T+ 00:00:00", style="secondary", font=("Arial", 9))
        self.time_text.pack(side="right")

    def _apply_profile_presets(self, choice: str) -> None:
        """Dynamically rewrite profile thresholds and internal states."""
        if choice == "Congested / Rush Hour":
            interval_val, blur_val, dup_val = "2.0", "100.0", "98.0"
        elif choice == "Fluid Traffic / Day":
            interval_val, blur_val, dup_val = "1.0", "120.0", "95.0"
        elif choice == "Night / Low-Light":
            interval_val, blur_val, dup_val = "1.0", "70.0", "93.0"
        elif choice == "High-Speed / Dashcam":
            interval_val, blur_val, dup_val = "0.3", "180.0", "90.0"
        else:
            return

        # Commit configurations to standard bindings
        self.interval_type_var.set("seconds")
        self.interval_value_var.set(interval_val)
        self.blur_threshold_var.set(float(blur_val))
        self.duplicate_threshold_var.set(float(dup_val))

        # Clear active entry arrays
        if hasattr(self, "interval_value_input"):
            self.interval_value_input.delete(0, "end")
            self.interval_value_input.insert(0, interval_val)
        if hasattr(self, "blur_threshold_input"):
            self.blur_threshold_input.delete(0, "end")
            self.blur_threshold_input.insert(0, blur_val)
        if hasattr(self, "duplicate_threshold_input"):
            self.duplicate_threshold_input.delete(0, "end")
            self.duplicate_threshold_input.insert(0, dup_val)

        self._add_log(f"[Preset Config Updated] Mode: '{choice}' -> Interval={interval_val}s | BlurThreshold={blur_val} | DuplicateThreshold={dup_val}%")

    def _add_log(self, message: str) -> None:
        """Proxy routing channel preventing asynchronous early initialization collisions."""
        if hasattr(self, "log_panel") and self.log_panel is not None:
            self.log_panel.add_log(message)
        else:
            logger.info(f"[Boot Stream Initialization Log] {message}")

    def _select_video(self) -> None:
        """Invoke runtime input target file parsing dialog handles."""
        filetypes = [("Video structures", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        file_path = filedialog.askopenfilename(title="Designate Input Stream target", filetypes=filetypes)

        if file_path:
            video_path = Path(file_path)
            is_valid, error_msg = validate_video_file(video_path)
            if not is_valid:
                self._add_log(f"[IO Error] Target initialization failed: {error_msg}")
                return

            self.selected_video = video_path
            self.video_label.configure(text=video_path.name)
            self._add_log(f"[IO Channel Established] Source designated: {video_path.name}")
            self._load_video_metadata()

    def _load_video_metadata(self) -> None:
        """Populate the telemetry tracking display maps with file metadata payload parameters."""
        if not self.selected_video:
            return

        metadata = self.extractor.get_video_metadata(self.selected_video)
        if metadata:
            self.info_panel.update_info("Filename", self.selected_video.name)
            self.info_panel.update_info("Resolution", f"{metadata.width}x{metadata.height}")
            self.info_panel.update_info("FPS", f"{metadata.fps:.1f}")
            self.info_panel.update_info("Duration", format_time(metadata.duration))
            self.info_panel.update_info("Total Frames", str(metadata.total_frames))

            self._add_log(
                f"[Source Metrics Ingested] Total frames: {metadata.total_frames} | "
                f"Framerate: {metadata.fps:.1f} FPS | Length: {format_time(metadata.duration)}"
            )

    def _select_output_folder(self) -> None:
        """Select storage destination output directory file array handle."""
        folder_path = filedialog.askdirectory(title="Designate Write Destination Mount", initialdir=str(self.output_folder))
        if folder_path:
            self.output_folder = Path(folder_path)
            self.output_label.configure(text=self.output_folder.name)
            self._add_log(f"[IO Channel Established] Target writing tree set: {self.output_folder.name}")

    def _start_extraction(self) -> None:
        """Launch extraction logic background loop matrix worker thread safely."""
        if not self.selected_video:
            self._add_log("[Runtime Abort] No execution target file context detected")
            return

        try:
            interval_value = float(self.interval_value_input.get())
            blur_threshold = float(self.blur_threshold_input.get())
            duplicate_threshold = float(self.duplicate_threshold_input.get())
        except ValueError:
            self._add_log("[Type Error] Input token parameters failed conversion metrics check")
            return

        self.extraction_running = True
        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")

        # Start the centralized pipeline manager
        self.pipeline_manager.start(
            self.selected_video,
            self.output_folder,
            self.interval_type_var.get(),
            interval_value,
            blur_threshold,
            duplicate_threshold,
            dataset_name=self.selected_video.stem,
            categories=DEFAULT_CATEGORIES,
            on_progress=self._on_pipeline_progress,
        )
        self.start_time = time.time()
        self._add_log("[Pipeline Thread Engaged] PipelineManager start invoked")

    def _extraction_worker(
        self,
        video_path: Path,
        interval_value: float,
        blur_threshold: float,
        duplicate_threshold: float,
    ) -> None:
        """Deprecated: extraction worker logic moved to PipelineManager.

        This method is retained for reference but no longer executes processing.
        """
        self._add_log("[Deprecated] _extraction_worker is no longer used. Use PipelineManager.")
        return

    def _cancel_extraction(self) -> None:
        """Set execution termination signals."""
        self.extraction_running = False
        self._add_log("[Pipeline Abort Event Intercepted] Execution pipeline worker state cancellation processing triggered")
        # Signal pipeline manager to cancel
        try:
            self.pipeline_manager.request_cancel()
        except Exception:
            pass
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")

    def _create_review_section(self, parent) -> None:
        """Embedded quality review panel for pipeline inspection."""
        frame = StyledFrame(parent, title="4. QUALITY REVIEW SUMMARY")
        frame.pack(fill="x", pady=(6, 6))

        self.review_summary_labels = {}
        info_items = [
            ("Pending", "0"),
            ("Approved", "0"),
            ("Rejected", "0"),
            ("Needs Review", "0"),
            ("Current File", "—"),
            ("Current Status", "—"),
        ]

        for label, value in info_items:
            row = ctk.CTkFrame(frame, fg_color="transparent", height=20)
            row.pack(fill="x", padx=10, pady=2)
            row.pack_propagate(False)
            title = StyledLabel(row, text=f"{label}:", style="secondary", font=("Consolas", 9))
            title.pack(side="left")
            value_label = StyledLabel(row, text=value, style="primary", font=("Consolas", 9, "bold"))
            value_label.pack(side="right")
            self.review_summary_labels[label.lower().replace(" ", "_")] = value_label

        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(8, 8))
        self.review_prev_btn = StyledButton(button_frame, text="Previous", command=lambda: self._navigate_review(-1), width=120)
        self.review_prev_btn.pack(side="left", padx=(0, 4))
        self.review_next_btn = StyledButton(button_frame, text="Next", command=lambda: self._navigate_review(1), width=120)
        self.review_next_btn.pack(side="left", padx=(4, 0))
        self.review_approve_btn = StyledButton(button_frame, text="Approve", command=lambda: self._set_review_status("approved"), style="success", width=120)
        self.review_approve_btn.pack(side="left", padx=(12, 4))
        self.review_reject_btn = StyledButton(button_frame, text="Reject", command=lambda: self._set_review_status("rejected"), style="danger", width=120)
        self.review_reject_btn.pack(side="left", padx=(4, 0))
        self.review_needs_btn = StyledButton(button_frame, text="Needs Review", command=lambda: self._set_review_status("needs_review"), style="warning", width=120)
        self.review_needs_btn.pack(side="left", padx=(4, 0))

    def _on_pipeline_progress(self, stage_name: str, progress: float) -> None:
        self.after(0, lambda: self._update_progress(stage_name, progress))

    def _update_progress(self, stage_name: str, progress: float) -> None:
        self.progress_bar.set(progress)
        self.progress_text.configure(text=f"{stage_name}: {progress*100:.0f}%")
        elapsed = time.time() - self.start_time
        self.time_text.configure(text=f"T+ {format_time(elapsed)}")

    def _on_pipeline_status_update(self) -> None:
        self.after(0, self._sync_pipeline_status)

    def _sync_pipeline_status(self) -> None:
        status = self.pipeline_manager.get_stage_status()
        current = self.pipeline_manager.current_stage
        try:
            stage_index = self.pipeline_manager.pipeline_steps.index(current) if current in self.pipeline_manager.pipeline_steps else 0
            overall_progress = (stage_index + 1) / len(self.pipeline_manager.pipeline_steps)
        except Exception:
            overall_progress = 0.0
        self.progress_bar.set(overall_progress)
        self.progress_text.configure(text=f"{current} [{status.get(current, 'unknown')}]")

        summary = self.pipeline_manager.get_summary()
        self.stat_cards["extracted"].update_value(str(summary.extracted_frames))
        self.stat_cards["kept"].update_value(str(summary.kept_frames))
        self.stat_cards["removed"].update_value(str(summary.removed_frames))
        self.stat_cards["blurred"].update_value(str(summary.blurred_frames))
        self.stat_cards["duplicates"].update_value(str(summary.duplicate_frames))

        if current in {"Quality Review", "Export Complete"}:
            records = self.pipeline_manager.get_review_records()
            self._load_review_records(records)

        if current == "Export Complete" or self.pipeline_manager.error_message:
            self.start_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
            if self.pipeline_manager.error_message:
                self._add_log(f"[Pipeline Error] {self.pipeline_manager.error_message}")
            else:
                self._add_log("[Pipeline Success] End-to-end pipeline complete")

    def _load_review_records(self, records: List[MetadataRecord]) -> None:
        self.review_records = records
        self.review_index = 0
        self._update_review_summary()
        self._refresh_review_detail()

    def _navigate_review(self, direction: int) -> None:
        if not self.review_records:
            return
        self.review_index = max(0, min(self.review_index + direction, len(self.review_records) - 1))
        self._refresh_review_detail()

    def _refresh_review_detail(self) -> None:
        if not self.review_records:
            self.review_summary_labels["current_file"].configure(text="—")
            self.review_summary_labels["current_status"].configure(text="—")
            return

        record = self.review_records[self.review_index]
        self.review_summary_labels["current_file"].configure(text=record.extracted_frame.filename)
        self.review_summary_labels["current_status"].configure(text=record.status.replace("_", " ").title())
        self._update_review_summary()

    def _set_review_status(self, status: str) -> None:
        if not self.review_records:
            return
        record = self.review_records[self.review_index]
        try:
            self.pipeline_manager.set_record_status(record.extracted_frame.filename, status)
        except Exception:
            pass
        record.status = status
        self._refresh_review_detail()

    def _update_review_summary(self) -> None:
        pending = sum(1 for r in self.review_records if r.status == "not_reviewed")
        approved = sum(1 for r in self.review_records if r.status == "approved")
        rejected = sum(1 for r in self.review_records if r.status == "rejected")
        needs_review = sum(1 for r in self.review_records if r.status == "needs_review")
        self.review_summary_labels["pending"].configure(text=str(pending))
        self.review_summary_labels["approved"].configure(text=str(approved))
        self.review_summary_labels["rejected"].configure(text=str(rejected))
        self.review_summary_labels["needs_review"].configure(text=str(needs_review))


def main() -> None:
    """Entry pipeline thread initialization core application execution context."""
    app = DatasetToolkitApp()
    app.mainloop()


if __name__ == "__main__":
    main()
