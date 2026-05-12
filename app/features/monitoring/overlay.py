"""Realtime overlay drawing helpers for the monitoring preview."""

from __future__ import annotations

from typing import Iterable, Optional


def draw_points(frame_rgb, points: Iterable[tuple[float, float]], color: tuple[int, int, int]) -> None:
    import cv2

    for x, y in points:
        cv2.circle(frame_rgb, (int(x), int(y)), 2, color, -1)


def draw_contour(
    frame_rgb,
    points: Iterable[tuple[float, float]],
    color: tuple[int, int, int],
    *,
    closed: bool = True,
) -> None:
    import cv2

    point_list = list(points)
    if len(point_list) < 2:
        return

    for start, end in zip(point_list, point_list[1:]):
        cv2.line(frame_rgb, (int(start[0]), int(start[1])), (int(end[0]), int(end[1])), color, 1)

    if closed:
        start = point_list[-1]
        end = point_list[0]
        cv2.line(frame_rgb, (int(start[0]), int(start[1])), (int(end[0]), int(end[1])), color, 1)


def draw_monitoring_overlay(
    frame_rgb,
    *,
    status: str,
    risk_level: str,
    ear_value: float,
    mar_value: float,
    ear_threshold: float,
    mar_threshold: float,
    eyes_closed_frames: int,
    yawn_frames: int,
    head_yaw: float = 0.0,
    head_pitch: float = 0.0,
) -> None:
    import cv2

    palette = {
        "low": ((34, 197, 94), (15, 23, 42)),
        "medium": ((251, 191, 36), (15, 23, 42)),
        "high": ((239, 68, 68), (255, 255, 255)),
        "danger": ((220, 38, 38), (255, 255, 255)),
    }
    accent, text_color = palette.get(risk_level, ((148, 163, 184), (15, 23, 42)))

    # Background panel
    panel_height = 190
    cv2.rectangle(frame_rgb, (18, 18), (380, panel_height), (248, 250, 252), -1)
    cv2.rectangle(frame_rgb, (18, 18), (380, panel_height), accent, 2)

    # Danger flash overlay
    if risk_level == "danger":
        overlay = frame_rgb.copy()
        cv2.rectangle(overlay, (0, 0), (frame_rgb.shape[1], frame_rgb.shape[0]), (0, 0, 200), -1)
        cv2.addWeighted(overlay, 0.15, frame_rgb, 0.85, 0, frame_rgb)

    font = cv2.FONT_HERSHEY_SIMPLEX
    lines = [
        f"Status: {status.upper()}",
        f"Risk: {risk_level.upper()}",
        f"EAR: {ear_value:.3f} | Thr: {ear_threshold:.2f}",
        f"MAR: {mar_value:.3f} | Thr: {mar_threshold:.2f}",
        f"Closed: {eyes_closed_frames}f | Yawn: {yawn_frames}f",
        f"Yaw: {head_yaw:.1f} | Pitch: {head_pitch:.1f}",
    ]

    y = 44
    for line in lines:
        cv2.putText(frame_rgb, line, (32, y), font, 0.52, text_color, 1, cv2.LINE_AA)
        y += 24
