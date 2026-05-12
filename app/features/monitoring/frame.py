"""Frame preprocessing helpers."""

from __future__ import annotations


def resize_frame(frame, width: int = 960, height: int = 540):
    import cv2

    return cv2.resize(frame, (width, height))


def to_rgb(frame):
    import cv2

    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
