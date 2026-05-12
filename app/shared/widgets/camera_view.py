"""Widget used to render webcam frames."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel
from typing import Optional


class CameraView(QLabel):
    def __init__(self) -> None:
        super().__init__("Camera preview")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(720, 405)
        self.setStyleSheet(
            "background-color: #0f172a; color: #cbd5e1; border: 1px solid #334155; "
            "border-radius: 12px;"
        )
        self._current_pixmap: Optional[QPixmap] = None

    def set_frame(self, frame) -> None:
        if isinstance(frame, QPixmap):
            pixmap = frame
        elif isinstance(frame, QImage):
            pixmap = QPixmap.fromImage(frame)
        else:
            height, width, channels = frame.shape
            bytes_per_line = channels * width
            image = QImage(
                frame.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            )
            pixmap = QPixmap.fromImage(image)

        self._current_pixmap = pixmap
        self.setPixmap(
            pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def show_message(self, message: str) -> None:
        self._current_pixmap = None
        self.clear()
        self.setText(message)

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt API name
        super().resizeEvent(event)
        if self._current_pixmap is None:
            return
        self.setPixmap(
            self._current_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
