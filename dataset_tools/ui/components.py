"""
UI components for Dataset Engineering Toolkit.

Utilitarian component library optimized for technical data density and layout efficiency.
"""

import customtkinter as ctk
from typing import Callable, Optional, Any
import tkinter as tk

from config import COLORS


class StyledButton(ctk.CTkButton):
    """Utilitarian block button with distinct operational status colors."""

    def __init__(
        self,
        master,
        text: str = "",
        command: Optional[Callable] = None,
        style: str = "primary",
        **kwargs
    ):
        # Extract configurations safely to avoid multi-value kwargs collisions
        font = kwargs.pop("font", ("Segoe UI", 11, "bold"))
        corner_radius = kwargs.pop("corner_radius", 2)
        height = kwargs.pop("height", 28)

        # Operational color matrices mapping actions directly to standard engineering palettes
        styles = {
            "primary": {
                "fg_color": COLORS["accent"],
                "hover_color": COLORS["accent_hover"],
                "text_color": COLORS["fg_primary"],
            },
            "secondary": {
                "fg_color": COLORS["bg_secondary"],
                "hover_color": COLORS["bg_tertiary"],
                "text_color": COLORS["fg_primary"],
            },
            "danger": {
                "fg_color": COLORS["error"],
                "hover_color": "#c0392b",
                "text_color": COLORS["fg_primary"],
            },
            "success": {
                "fg_color": COLORS["success"],
                "hover_color": "#229954",
                "text_color": COLORS["fg_primary"],
            },
        }

        style_config = styles.get(style, styles["primary"])

        super().__init__(
            master,
            text=text,
            command=command,
            font=font,
            corner_radius=corner_radius,
            height=height,
            border_spacing=2,
            **style_config,
            **kwargs,
        )


class StyledLabel(ctk.CTkLabel):
    """High-contrast label for scannable telemetry arrays."""

    def __init__(
        self,
        master,
        text: str = "",
        style: str = "primary",
        **kwargs
    ):
        text_colors = {
            "primary": COLORS["fg_primary"],
            "secondary": COLORS["fg_secondary"],
        }

        text_color = text_colors.get(style, COLORS["fg_primary"])
        
        # Safe extraction of font configuration overrides
        font = kwargs.pop("font", ("Segoe UI", 11))

        super().__init__(
            master,
            text=text,
            text_color=text_color,
            font=font,
            **kwargs,
        )


class StyledFrame(ctk.CTkFrame):
    """Structural layout container with localized engineering section headers."""

    def __init__(
        self,
        master,
        title: Optional[str] = None,
        **kwargs
    ):
        border_width = kwargs.pop("border_width", 1)
        corner_radius = kwargs.pop("corner_radius", 0)

        super().__init__(
            master,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["bg_tertiary"],
            border_width=border_width,
            corner_radius=corner_radius,
            **kwargs,
        )

        if title:
            # High-density system sectional header banner
            header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"], height=24, corner_radius=0)
            header_frame.pack(side="top", fill="x")
            header_frame.pack_propagate(False)

            title_label = StyledLabel(
                header_frame,
                text=f" {title}",
                style="primary",
                font=("Consolas", 10, "bold"),
            )
            title_label.pack(side="left", padx=4)


class ScrollableFrame(ctk.CTkScrollableFrame):
    """Scrollable block frame containing overflow metrics collections."""

    def __init__(self, master, **kwargs):
        border_width = kwargs.pop("border_width", 1)
        corner_radius = kwargs.pop("corner_radius", 0)

        super().__init__(
            master,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["bg_tertiary"],
            border_width=border_width,
            corner_radius=corner_radius,
            **kwargs,
        )


class ProgressBar(ctk.CTkProgressBar):
    """Linear status trackbar displaying ongoing thread workloads."""

    def __init__(self, master, **kwargs):
        border_width = kwargs.pop("border_width", 1)
        corner_radius = kwargs.pop("corner_radius", 0)

        super().__init__(
            master,
            progress_color=COLORS["accent"],
            fg_color=COLORS["bg_primary"],
            border_color=COLORS["bg_tertiary"],
            border_width=border_width,
            corner_radius=corner_radius,
            **kwargs,
        )


class StatCard(StyledFrame):
    """Compact telemetry data cell optimized for dense horizontal grid positioning."""

    def __init__(
        self,
        master,
        label: str = "",
        value: str = "0",
        **kwargs
    ):
        super().__init__(master, **kwargs)

        # Content container layout maximizing internal matrix density
        content_inner = ctk.CTkFrame(self, fg_color="transparent")
        content_inner.pack(fill="both", expand=True, padx=8, pady=4)

        # Metric Description
        label_widget = StyledLabel(
            content_inner,
            text=label.upper(),
            style="secondary",
            font=("Consolas", 9, "bold"),
        )
        label_widget.pack(side="top", anchor="w")

        # Metric Value Output Matrix
        self.value_widget = StyledLabel(
            content_inner,
            text=value,
            style="primary",
            font=("Consolas", 14, "bold"),
        )
        self.value_widget.pack(side="top", anchor="w", pady=(2, 0))

    def update_value(self, value: str) -> None:
        """Atomically overwrite system telemetry metrics display state."""
        self.value_widget.configure(text=value)


class InputField(ctk.CTkEntry):
    """High-density variable configuration input channel."""

    def __init__(self, master, placeholder: str = "", **kwargs):
        font = kwargs.pop("font", ("Consolas", 11))
        height = kwargs.pop("height", 24)
        corner_radius = kwargs.pop("corner_radius", 0)

        super().__init__(
            master,
            fg_color=COLORS["bg_primary"],
            text_color=COLORS["fg_primary"],
            border_color=COLORS["bg_tertiary"],
            corner_radius=corner_radius,
            font=font,
            height=height,
            **kwargs,
        )

        if placeholder:
            self.placeholder = placeholder
            self.insert(0, placeholder)
            self.bind("<FocusIn>", self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)

    def _on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)

    def get_value(self) -> str:
        value = self.get()
        if hasattr(self, 'placeholder') and value == self.placeholder:
            return ""
        return value


class LogPanel(ScrollableFrame):
    """Standard console stdout console window imitating terminal text output sinks."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Fixed: Changed font size from 9.5 to integer 9 to support strict Tcl interpreters
        self.text_widget = tk.Text(
            self,
            bg=COLORS["bg_primary"],
            fg=COLORS["fg_primary"],
            font=("Consolas", 9),
            relief="flat",
            insertbackground=COLORS["fg_primary"],
            padx=6,
            pady=6,
            wrap="word"
        )
        self.text_widget.pack(fill="both", expand=True)

    def add_log(self, message: str) -> None:
        """Append log message and automatically auto-scroll target stream index to bottom."""
        self.text_widget.insert("end", message + "\n")
        self.text_widget.see("end")
        self.text_widget.update()

    def clear_log(self) -> None:
        """Flush the text buffer display arena."""
        self.text_widget.delete("1.0", "end")

    def get_logs(self) -> str:
        """Exfiltrate written text buffer arrays."""
        return self.text_widget.get("1.0", "end-1c")


class InfoPanel(StyledFrame):
    """Dense key-value status read-out table for stream state introspection."""

    def __init__(self, master, **kwargs):
        super().__init__(master, title="METADATA & INGEST TELEMETRY STATUS", **kwargs)

        self.info_labels = {}
        info_items = [
            ("Filename", "—"),
            ("Resolution", "—"),
            ("FPS", "—"),
            ("Duration", "—"),
            ("Total Frames", "—"),
        ]

        # Compact key-value matrix layout pipeline
        for label, value in info_items:
            row_frame = ctk.CTkFrame(self, fg_color="transparent", height=18)
            row_frame.pack(fill="x", padx=10, pady=1)
            row_frame.pack_propagate(False)

            label_widget = StyledLabel(
                row_frame,
                text=f"{label.upper()}:",
                style="secondary",
                font=("Consolas", 9),
            )
            label_widget.pack(side="left")

            value_widget = StyledLabel(
                row_frame,
                text=value,
                style="primary",
                font=("Consolas", 9, "bold"),
            )
            value_widget.pack(side="right")

            self.info_labels[label] = value_widget

    def update_info(self, label: str, value: str) -> None:
        """Synchronize runtime state maps directly into tabular view metrics."""
        if label in self.info_labels:
            self.info_labels[label].configure(text=value)