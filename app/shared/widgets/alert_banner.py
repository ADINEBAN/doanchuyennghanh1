"""Banner widget for live alert state."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel


class AlertBanner(QLabel):
    def __init__(self) -> None:
        super().__init__("System ready.")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setMinimumHeight(64)
        self.set_status("normal", "low", "System ready.")

    def set_status(self, status: str, risk_level: str, message: str) -> None:
        palette = {
            "low": ("#dcfce7", "#166534"),
            "medium": ("#fef3c7", "#92400e"),
            "high": ("#fee2e2", "#991b1b"),
            "danger": ("#7f1d1d", "#ffffff"),
        }
        background, foreground = palette.get(risk_level, ("#e2e8f0", "#1e293b"))
        self.setText(f"{status.upper()} | {message}")
        self.setStyleSheet(
            f"background-color: {background}; color: {foreground}; "
            "padding: 14px; border-radius: 12px; font-weight: 600; font-size: 14px;"
        )
