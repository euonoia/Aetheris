"""
UI components for Dataset Engineering Toolkit.

Reusable components for building the application interface.
"""

import customtkinter as ctk
from typing import Callable, Optional, Any
import tkinter as tk

from config import COLORS


class StyledButton(ctk.CTkButton):
    """Styled button component."""

    def __init__(
        self,
        master,
        text: str = "",
        command: Optional[Callable] = None,
        style: str = "primary",
        **kwargs
    ):
        """
        Create styled button.

        Args:
            master: Parent widget
            text: Button text
            command: Click callback
            style: 'primary', 'secondary', 'danger', 'success'
        """
        # Define styles
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
            **style_config,
            **kwargs,
        )


class StyledLabel(ctk.CTkLabel):
    """Styled label component."""

    def __init__(
        self,
        master,
        text: str = "",
        style: str = "primary",
        **kwargs
    ):
        """
        Create styled label.

        Args:
            master: Parent widget
            text: Label text
            style: 'primary', 'secondary'
        """
        text_colors = {
            "primary": COLORS["fg_primary"],
            "secondary": COLORS["fg_secondary"],
        }

        text_color = text_colors.get(style, COLORS["fg_primary"])

        super().__init__(
            master,
            text=text,
            text_color=text_color,
            **kwargs,
        )


class StyledFrame(ctk.CTkFrame):
    """Styled frame component with border."""

    def __init__(
        self,
        master,
        title: Optional[str] = None,
        **kwargs
    ):
        """Create styled frame."""
        super().__init__(
            master,
            fg_color=COLORS["bg_secondary"],
            **kwargs,
        )

        if title:
            # Create title label
            title_label = StyledLabel(
                self,
                text=title,
                style="primary",
                font=("Arial", 12, "bold"),
            )
            title_label.pack(side="top", fill="x", padx=10, pady=(10, 5))


class ScrollableFrame(ctk.CTkScrollableFrame):
    """Scrollable frame component."""

    def __init__(self, master, **kwargs):
        """Create scrollable frame."""
        super().__init__(
            master,
            fg_color=COLORS["bg_secondary"],
            **kwargs,
        )


class ProgressBar(ctk.CTkProgressBar):
    """Styled progress bar."""

    def __init__(self, master, **kwargs):
        """Create progress bar."""
        super().__init__(
            master,
            progress_color=COLORS["accent"],
            fg_color=COLORS["bg_tertiary"],
            **kwargs,
        )


class StatCard(StyledFrame):
    """Card displaying a statistic."""

    def __init__(
        self,
        master,
        label: str = "",
        value: str = "0",
        **kwargs
    ):
        """
        Create stat card.

        Args:
            master: Parent widget
            label: Stat label
            value: Stat value
        """
        super().__init__(master, **kwargs)

        # Label
        label_widget = StyledLabel(
            self,
            text=label,
            style="secondary",
            font=("Arial", 10),
        )
        label_widget.pack(side="top", fill="x", padx=10, pady=(5, 0))

        # Value
        self.value_widget = StyledLabel(
            self,
            text=value,
            style="primary",
            font=("Arial", 14, "bold"),
        )
        self.value_widget.pack(side="top", fill="x", padx=10, pady=(0, 5))

    def update_value(self, value: str) -> None:
        """Update displayed value."""
        self.value_widget.configure(text=value)


class InputField(ctk.CTkEntry):
    """Styled input field."""

    def __init__(self, master, placeholder: str = "", **kwargs):
        """Create input field."""
        super().__init__(
            master,
            fg_color=COLORS["bg_tertiary"],
            text_color=COLORS["fg_primary"],
            border_color=COLORS["bg_primary"],
            **kwargs,
        )

        if placeholder:
            self.placeholder = placeholder
            self.insert(0, placeholder)
            self.bind("<FocusIn>", self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        """Clear placeholder on focus."""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)

    def _on_focus_out(self, event):
        """Restore placeholder if empty."""
        if not self.get():
            self.insert(0, self.placeholder)

    def get_value(self) -> str:
        """Get actual value (excluding placeholder)."""
        value = self.get()
        if hasattr(self, 'placeholder') and value == self.placeholder:
            return ""
        return value


class LogPanel(ScrollableFrame):
    """Panel for displaying logs."""

    def __init__(self, master, **kwargs):
        """Create log panel."""
        super().__init__(master, **kwargs)

        # Configure text widget for better display
        self.text_widget = tk.Text(
            self,
            bg=COLORS["bg_primary"],
            fg=COLORS["fg_primary"],
            font=("Courier", 9),
            height=8,
            relief="flat",
            insertbackground=COLORS["fg_primary"],
        )
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)

    def add_log(self, message: str) -> None:
        """Add message to log."""
        self.text_widget.insert("end", message + "\n")
        self.text_widget.see("end")
        self.text_widget.update()

    def clear_log(self) -> None:
        """Clear all logs."""
        self.text_widget.delete("1.0", "end")

    def get_logs(self) -> str:
        """Get all log content."""
        return self.text_widget.get("1.0", "end-1c")


class InfoPanel(StyledFrame):
    """Panel for displaying video information."""

    def __init__(self, master, **kwargs):
        """Create info panel."""
        super().__init__(master, title="Video Information", **kwargs)

        # Create grid for info items
        self.info_labels = {}

        info_items = [
            ("Filename", "—"),
            ("Resolution", "—"),
            ("FPS", "—"),
            ("Duration", "—"),
            ("Total Frames", "—"),
        ]

        for label, value in info_items:
            row_frame = ctk.CTkFrame(self, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=5)

            label_widget = StyledLabel(
                row_frame,
                text=f"{label}:",
                style="secondary",
                font=("Arial", 10),
            )
            label_widget.pack(side="left", fill="x", expand=True)

            value_widget = StyledLabel(
                row_frame,
                text=value,
                style="primary",
                font=("Arial", 10, "bold"),
            )
            value_widget.pack(side="left")

            self.info_labels[label] = value_widget

    def update_info(self, label: str, value: str) -> None:
        """Update info value."""
        if label in self.info_labels:
            self.info_labels[label].configure(text=value)
