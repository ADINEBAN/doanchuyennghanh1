"""EAR and MAR calculation utilities."""

from __future__ import annotations

from math import dist
from typing import Sequence

Point = Sequence[float]


def eye_aspect_ratio(eye_points: Sequence[Point]) -> float:
    if len(eye_points) != 6:
        raise ValueError("EAR requires exactly 6 eye landmarks.")

    vertical_1 = dist(eye_points[1], eye_points[5])
    vertical_2 = dist(eye_points[2], eye_points[4])
    horizontal = dist(eye_points[0], eye_points[3])
    if horizontal == 0:
        return 0.0
    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def mouth_aspect_ratio(mouth_points: Sequence[Point]) -> float:
    if len(mouth_points) != 8:
        raise ValueError("MAR requires exactly 8 mouth landmarks.")

    vertical_1 = dist(mouth_points[1], mouth_points[7])
    vertical_2 = dist(mouth_points[2], mouth_points[6])
    vertical_3 = dist(mouth_points[3], mouth_points[5])
    horizontal = dist(mouth_points[0], mouth_points[4])
    if horizontal == 0:
        return 0.0
    return (vertical_1 + vertical_2 + vertical_3) / (3.0 * horizontal)
