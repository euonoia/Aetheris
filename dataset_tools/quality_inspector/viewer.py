"""Standalone Dataset Quality Inspector UI."""

import os
import threading
from pathlib import Path
from typing import Dict, List, Optional

import customtkinter as ctk
from PIL import Image

from .inspector import QualityInspectorManager, QualityRecord
from .thumbnail_cache import ThumbnailCache
from .actions import export_inspection_report, move_records, restore_deleted_images
from .filters import QualityFilter
from ..utils.file_utils import format_file_size
from ..config import COLORS

DEFAULT_THUMBNAIL_SIZE = (150, 90)


class QualityInspectorApp(ctk.CTk):
    """Interactive dataset quality inspection workspace."""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Dataset Quality Inspector")
        self.geometry("1600x950")
        self.minsize(1400, 860)

        self.manager = QualityInspectorManager()
        self.thumbnail_cache = ThumbnailCache(size=DEFAULT_THUMBNAIL_SIZE)
        self.records: List[QualityRecord] = []
        self.filtered_records: List[QualityRecord] = []
        self.current_record: Optional[QualityRecord] = None
        self.thumbnail_buttons: Dict[str, ctk.CTkButton] = {}
        self.thumbnail_images: Dict[str, ctk.CTkImage] = {}
        self.preview_image: Optional[ctk.CTkImage] = None
        self.zoom_factor = 1.0

        self._build_ui()
        self.bind_shortcuts()

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=12, pady=12)
        container.grid_columnconfigure(0, weight=1, minsize=320)
        container.grid_columnconfigure(1, weight=2)
        container.grid_columnconfigure(2, weight=1, minsize=340)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=0)

        self._build_browser_panel(container)
        self._build_preview_panel(container)
        self._build_inspection_panel(container)
        self._build_thumbnail_strip(container)

    def _build_browser_panel(self, parent) -> None:
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
        frame.grid_rowconfigure(5, weight=1)

        title = ctk.CTkLabel(frame, text="Dataset Browser", font=("Consolas", 16, "bold"), text_color=COLORS["fg_primary"])
        title.pack(anchor="w", padx=16, pady=(16, 8))

        self.folder_label = ctk.CTkLabel(frame, text="No folder selected", font=("Arial", 11), text_color=COLORS["fg_secondary"])
        self.folder_label.pack(fill="x", padx=16, pady=(0, 10))

        browse_btn = ctk.CTkButton(frame, text="Open Dataset Folder", command=self._browse_folder, fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], corner_radius=6)
        browse_btn.pack(fill="x", padx=16, pady=(0, 14))

        search_frame = ctk.CTkFrame(frame, fg_color=COLORS["bg_primary"], corner_radius=6)
        search_frame.pack(fill="x", padx=16, pady=(0, 12))
        self.search_var = ctk.StringVar(value="")
        search_input = ctk.CTkEntry(search_frame, placeholder_text="Search filename...", textvariable=self.search_var, fg_color=COLORS["bg_secondary"], text_color=COLORS["fg_primary"], border_color=COLORS["bg_tertiary"], corner_radius=6)
        search_input.pack(fill="x", padx=8, pady=8)
        search_input.bind("<KeyRelease>", lambda _: self._apply_filters())

        filter_frame = ctk.CTkFrame(frame, fg_color=COLORS["bg_primary"], corner_radius=6)
        filter_frame.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkLabel(filter_frame, text="Filter", font=("Arial", 10, "bold"), text_color=COLORS["fg_primary"]).pack(anchor="w", padx=8, pady=(8, 0))
        self.filter_var = ctk.StringVar(value=QualityFilter.ALL.value)
        filter_menu = ctk.CTkOptionMenu(filter_frame, values=[filter_type.value for filter_type in QualityFilter], variable=self.filter_var, command=self._on_filter_change, fg_color=COLORS["bg_secondary"], button_color=COLORS["accent"], text_color=COLORS["fg_primary"], width=260)
        filter_menu.pack(fill="x", padx=8, pady=(6, 12))

        self.browser_stats = ctk.CTkLabel(frame, text="Images: 0  |  Approved: 0  |  Rejected: 0", font=("Arial", 10), text_color=COLORS["fg_secondary"])
        self.browser_stats.pack(anchor="w", padx=16, pady=(0, 6))

        self.health_frame = ctk.CTkFrame(frame, fg_color=COLORS["bg_primary"], corner_radius=6)
        self.health_frame.pack(fill="both", expand=True, padx=16, pady=(10, 16))
        self.health_frame.grid_rowconfigure(0, weight=1)
        self.health_labels: Dict[str, ctk.CTkLabel] = {}
        for label in ["Total", "Approved", "Rejected", "Review", "Blurred", "Duplicates"]:
            metric = ctk.CTkLabel(self.health_frame, text=f"{label}: 0", font=("Arial", 11), text_color=COLORS["fg_primary"])
            metric.pack(anchor="w", padx=12, pady=4)
            self.health_labels[label.lower()] = metric

    def _build_preview_panel(self, parent) -> None:
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=10)
        frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=(0, 6))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)

        preview_header = ctk.CTkLabel(frame, text="Large Image Preview", font=("Consolas", 16, "bold"), text_color=COLORS["fg_primary"])
        preview_header.pack(anchor="w", padx=16, pady=(16, 6))

        self.preview_container = ctk.CTkFrame(frame, fg_color=COLORS["bg_primary"], corner_radius=10)
        self.preview_container.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.preview_label = ctk.CTkLabel(self.preview_container, text="No image selected", font=("Arial", 12), text_color=COLORS["fg_secondary"])
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")
        self.preview_container.bind("<MouseWheel>", self._on_zoom)
        self.preview_container.bind("<Button-4>", self._on_zoom)
        self.preview_container.bind("<Button-5>", self._on_zoom)
        self.preview_container.bind("<Double-Button-1>", lambda _: self._fit_preview())

        info_frame = ctk.CTkFrame(frame, fg_color=COLORS["bg_primary"], corner_radius=10)
        info_frame.pack(fill="x", padx=16, pady=(0, 14))
        self.preview_info: Dict[str, ctk.CTkLabel] = {}
        for label in ["Filename", "Resolution", "Blur Score", "Similarity", "Brightness", "Contrast", "Sharpness", "Size"]:
            text = ctk.CTkLabel(info_frame, text=f"{label}: —", font=("Arial", 10), text_color=COLORS["fg_secondary"])
            text.pack(anchor="w", padx=10, pady=2)
            self.preview_info[label.lower().replace(" ", "_")] = text

    def _build_inspection_panel(self, parent) -> None:
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=10)
        frame.grid(row=0, column=2, sticky="nsew", padx=(6, 0), pady=(0, 6))

        title = ctk.CTkLabel(frame, text="Quality Metrics", font=("Consolas", 16, "bold"), text_color=COLORS["fg_primary"])
        title.pack(anchor="w", padx=16, pady=(16, 8))

        self.metric_cards: Dict[str, ctk.CTkLabel] = {}
        for label in ["Average Blur", "Average Brightness", "Average Contrast", "Average Sharpness", "Objects Reviewed"]:
            metric = ctk.CTkLabel(frame, text=f"{label}: —", font=("Arial", 11), text_color=COLORS["fg_secondary"])
            metric.pack(anchor="w", padx=16, pady=4)
            self.metric_cards[label.lower().replace(" ", "_")] = metric

        self.warning_label = ctk.CTkLabel(frame, text="Warnings: None", font=("Arial", 11), text_color=COLORS["warning"])
        self.warning_label.pack(fill="x", padx=16, pady=(10, 12))

        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=16, pady=(0, 10))

        actions = [
            ("Approve", self._action_approve, COLORS["success"]),
            ("Reject", self._action_reject, COLORS["error"]),
            ("Delete", self._action_delete, COLORS["warning"]),
            ("Review", self._action_review, COLORS["accent"]),
        ]

        for text, callback, color in actions:
            btn = ctk.CTkButton(button_frame, text=text, command=callback, fg_color=color, hover_color=color, corner_radius=8)
            btn.pack(fill="x", pady=4)

        export_frame = ctk.CTkFrame(frame, fg_color=COLORS["bg_primary"], corner_radius=10)
        export_frame.pack(fill="x", padx=16, pady=(12, 16))

        ctk.CTkLabel(export_frame, text="Export / Batch Actions", font=("Arial", 11, "bold"), text_color=COLORS["fg_primary"]).pack(anchor="w", padx=12, pady=(10, 6))
        self.export_button = ctk.CTkButton(export_frame, text="Export Selected Report", command=self._export_report, fg_color=COLORS["accent"], corner_radius=8)
        self.export_button.pack(fill="x", padx=12, pady=(0, 8))

        move_frame = ctk.CTkFrame(export_frame, fg_color="transparent")
        move_frame.pack(fill="x", padx=12, pady=(0, 10))
        move_approved = ctk.CTkButton(move_frame, text="Move Approved", command=lambda: self._batch_move("approved"), fg_color=COLORS["success"], corner_radius=8)
        move_approved.pack(fill="x", pady=4)
        move_review = ctk.CTkButton(move_frame, text="Move Review", command=lambda: self._batch_move("review"), fg_color=COLORS["warning"], corner_radius=8)
        move_review.pack(fill="x", pady=4)

    def _build_thumbnail_strip(self, parent) -> None:
        strip_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=10)
        strip_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(0, 0))
        strip_frame.grid_columnconfigure(0, weight=1)
        strip_frame.grid_rowconfigure(0, weight=1)

        self.thumbnail_scroll = ctk.CTkScrollableFrame(strip_frame, fg_color=COLORS["bg_primary"], corner_radius=10, height=180)
        self.thumbnail_scroll.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self.thumbnail_scroll.pack_propagate(False)

    def bind_shortcuts(self) -> None:
        self.bind("<Left>", lambda _: self._navigate(-1))
        self.bind("<Right>", lambda _: self._navigate(1))
        self.bind("<space>", lambda _: self._toggle_zoom())
        self.bind("<a>", lambda _: self._action_approve())
        self.bind("<r>", lambda _: self._action_reject())
        self.bind("<Delete>", lambda _: self._action_delete())
        self.bind("<Control-a>", lambda _: self._batch_approve_all())

    def _browse_folder(self) -> None:
        folder_path = ctk.filedialog.askdirectory(title="Choose extracted dataset folder")
        if not folder_path:
            return

        self.folder_label.configure(text=str(folder_path))
        thread = threading.Thread(target=self._load_dataset, args=(Path(folder_path),), daemon=True)
        thread.start()

    def _load_dataset(self, dataset_folder: Path) -> None:
        self.records = self.manager.load_dataset(dataset_folder)
        self.filtered_records = self.records
        self.thumbnail_cache.preload(tuple(record.image_path for record in self.records))
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        self._apply_filters()
        self._render_thumbnails()
        self._update_health_metrics()
        self._update_browser_stats()
        self._update_inspection_metrics()

    def _render_thumbnails(self) -> None:
        for widget in self.thumbnail_scroll.winfo_children():
            widget.destroy()

        self.thumbnail_buttons.clear()
        self.thumbnail_images.clear()

        for record in self.filtered_records:
            thumbnail = self.thumbnail_cache.get_thumbnail(record.image_path)
            if thumbnail is None:
                continue

            self.thumbnail_images[record.filename] = thumbnail
            border_color = self._status_border_color(record)
            btn = ctk.CTkButton(
                self.thumbnail_scroll,
                image=thumbnail,
                text="",
                fg_color=COLORS["bg_primary"],
                hover_color=COLORS["bg_tertiary"],
                border_width=3,
                border_color=border_color,
                corner_radius=8,
                width=DEFAULT_THUMBNAIL_SIZE[0],
                height=DEFAULT_THUMBNAIL_SIZE[1],
                command=lambda item=record: self._select_record(item),
            )
            btn.pack(side="left", padx=6, pady=8)
            self.thumbnail_buttons[record.filename] = btn

    def _status_border_color(self, record: QualityRecord) -> str:
        return {
            "approved": COLORS["success"],
            "rejected": COLORS["error"],
            "needs_review": COLORS["warning"],
            "deleted": COLORS["fg_secondary"],
            "not_reviewed": COLORS["fg_secondary"],
        }.get(record.status, COLORS["fg_secondary"])

    def _select_record(self, record: QualityRecord) -> None:
        self.current_record = record
        self.zoom_factor = 1.0
        self._update_preview()
        self._highlight_selected_thumbnail()

    def _highlight_selected_thumbnail(self) -> None:
        for filename, button in self.thumbnail_buttons.items():
            if self.current_record and filename == self.current_record.filename:
                button.configure(border_color=COLORS["accent"], border_width=4)
            else:
                record = next((r for r in self.records if r.filename == filename), None)
                if record:
                    button.configure(border_color=self._status_border_color(record), border_width=3)

    def _update_preview(self) -> None:
        if not self.current_record:
            self.preview_label.configure(text="No image selected", image=None)
            return

        try:
            image = Image.open(self.current_record.image_path)
            preview_size = (int(760 * self.zoom_factor), int(520 * self.zoom_factor))
            image.thumbnail(preview_size, Image.Resampling.LANCZOS)
            self.preview_image = ctk.CTkImage(light_image=image, size=image.size)
            self.preview_label.configure(image=self.preview_image, text="")
        except Exception:
            self.preview_label.configure(text="Failed to render image", image=None)
            return

        description = self.manager.describe_record(self.current_record)
        for key, label in self.preview_info.items():
            label.configure(text=f"{key.replace('_', ' ').title()}: {description.get(key.replace('_', ' '), '—')}")

        self._update_warning_badges(self.current_record)

    def _update_warning_badges(self, record: QualityRecord) -> None:
        warnings = []
        if record.blur_score is not None and record.blur_score < self.manager.blur_threshold:
            warnings.append("⚠ Very Blurry")
        if record.similarity_score is not None and record.similarity_score >= 0.90:
            warnings.append("⚠ Possible Duplicate")
        if record.brightness is not None and record.brightness < 60:
            warnings.append("⚠ Very Dark")
        if record.brightness is not None and record.brightness > 190:
            warnings.append("⚠ Very Bright")
        self.warning_label.configure(text="Warnings: " + (", ".join(warnings) if warnings else "None"))

    def _navigate(self, direction: int) -> None:
        if not self.filtered_records or not self.current_record:
            return
        try:
            index = self.filtered_records.index(self.current_record)
            index = max(0, min(len(self.filtered_records) - 1, index + direction))
            self._select_record(self.filtered_records[index])
        except ValueError:
            return

    def _toggle_zoom(self) -> None:
        self.zoom_factor = 1.0 if self.zoom_factor != 1.0 else 1.4
        self._update_preview()

    def _on_zoom(self, event) -> None:
        if event.delta > 0 or getattr(event, "num", None) == 4:
            self.zoom_factor = min(2.5, self.zoom_factor + 0.1)
        else:
            self.zoom_factor = max(0.6, self.zoom_factor - 0.1)
        self._update_preview()

    def _fit_preview(self) -> None:
        self.zoom_factor = 1.0
        self._update_preview()

    def _apply_filters(self) -> None:
        if not self.records:
            return

        query = self.search_var.get().strip().lower()
        self.manager.set_filter(self.filter_var.get())
        filtered = self.manager.get_filtered_records()

        if query:
            filtered = [record for record in filtered if query in record.filename.lower()]

        self.filtered_records = filtered
        if self.filtered_records:
            self.current_record = self.filtered_records[0]
        else:
            self.current_record = None

        self._render_thumbnails()
        self._update_browser_stats()
        self._update_inspection_metrics()
        self._update_health_metrics()
        self._update_preview()

    def _on_filter_change(self, value: str) -> None:
        self._apply_filters()

    def _update_browser_stats(self) -> None:
        summary = self.manager.get_health_summary()
        self.browser_stats.configure(text=f"Images: {summary['total']}  |  Approved: {summary['approved']}  |  Rejected: {summary['rejected']}")
        self._update_health_metrics()

    def _update_inspection_metrics(self) -> None:
        stats = self.manager.get_dataset_stats()
        self.metric_cards["average_blur"].configure(text=f"Average Blur: {stats['average_blur']:.2f}")
        self.metric_cards["average_brightness"].configure(text=f"Average Brightness: {stats['average_brightness']:.2f}")
        self.metric_cards["average_contrast"].configure(text=f"Average Contrast: —")
        self.metric_cards["average_sharpness"].configure(text=f"Average Sharpness: {stats['average_sharpness']:.2f}")
        self.metric_cards["objects_reviewed"].configure(text=f"Objects Reviewed: {sum(1 for r in self.records if r.status != 'not_reviewed')}")

    def _update_health_metrics(self) -> None:
        summary = self.manager.get_health_summary()
        self.health_labels["total"].configure(text=f"Total: {summary['total']}")
        self.health_labels["approved"].configure(text=f"Approved: {summary['approved']}")
        self.health_labels["rejected"].configure(text=f"Rejected: {summary['rejected']}")
        self.health_labels["review"].configure(text=f"Review: {summary['needs_review']}")
        self.health_labels["blurred"].configure(text=f"Blurred: {summary['blurred']}")
        self.health_labels["duplicates"].configure(text=f"Duplicates: {summary['duplicates']}")

    def _action_approve(self) -> None:
        if self.current_record:
            self.manager.update_status(self.current_record, "approved")
            self._refresh_ui()

    def _action_reject(self) -> None:
        if self.current_record:
            self.manager.update_status(self.current_record, "rejected")
            self._refresh_ui()

    def _action_delete(self) -> None:
        if self.current_record:
            self.manager.update_status(self.current_record, "deleted")
            try:
                self.current_record.image_path.unlink()
            except Exception:
                pass
            self._refresh_ui()

    def _action_review(self) -> None:
        if self.current_record:
            self.manager.update_status(self.current_record, "needs_review")
            self._refresh_ui()

    def _batch_move(self, destination: str) -> None:
        if not self.filtered_records:
            return
        selected = [record for record in self.filtered_records if record.status in ("approved", "needs_review")]
        destination_folder = Path(self.folder_label.cget("text")) / destination
        move_records(selected, destination_folder, update_status=destination)
        self._refresh_ui()

    def _batch_approve_all(self) -> None:
        if not self.filtered_records:
            return
        self.manager.batch_update_status(self.filtered_records, "approved")
        self._refresh_ui()

    def _export_report(self) -> None:
        if not self.records:
            return
        dataset_folder = Path(self.folder_label.cget("text"))
        destination = dataset_folder / "inspection_reports"
        export_inspection_report(self.records, destination)
        self._add_notification("Inspection report exported")

    def _add_notification(self, message: str) -> None:
        self.warning_label.configure(text=f"Warnings: {message}", text_color=COLORS["success"])


def main() -> None:
    app = QualityInspectorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
