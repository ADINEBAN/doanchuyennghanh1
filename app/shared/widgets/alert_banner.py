"""Banner widget for live alert state."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel


class AlertBanner(QLabel):
    def __init__(self) -> None:
        super().__init__("Hệ thống sẵn sàng.")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setMinimumHeight(64)
        self.set_status("normal", "low", "Hệ thống sẵn sàng.")

    def set_status(self, status: str, risk_level: str, message: str) -> None:
        palette = {
            "low": ("#e8f7ef", "#166534", "#bbf7d0"),
            "medium": ("#fff7dd", "#92400e", "#fde68a"),
            "high": ("#fff1f2", "#991b1b", "#fecdd3"),
            "danger": ("#7f1d1d", "#ffffff", "#450a0a"),
        }
        background, foreground, border = palette.get(
            risk_level, ("#e2e8f0", "#1e293b", "#cbd5e1")
        )
        self.setText(f"{status.upper()} | {message}")
        self.setStyleSheet(
            f"background-color: {background}; color: {foreground}; "
            f"border: 1px solid {border}; "
            "padding: 14px; border-radius: 8px; font-weight: 800; font-size: 14px;"
        )
