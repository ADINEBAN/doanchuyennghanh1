"""Webcam lifecycle wrapper."""

from __future__ import annotations

from typing import Any

from app.shared.core.exceptions import CameraError


class WebcamManager:
    def __init__(self, camera_index: int = 0) -> None:
        self.camera_index = camera_index
        self.capture: Any = None

    def open(self) -> None:
        import cv2

        self.capture = cv2.VideoCapture(self.camera_index)
        if not self.capture.isOpened():
            raise CameraError(f"Could not open camera index {self.camera_index}.")

    def read_frame(self):
        if self.capture is None:
            raise CameraError("Camera is not open.")

        ok, frame = self.capture.read()
        if not ok:
            raise CameraError("Failed to read a frame from the webcam.")
        return frame

    def release(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None
