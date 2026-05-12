"""Decision engine that combines CV metrics and model output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.shared.config.constants import (
    DEFAULT_DISTRACTION_SECONDS,
    DEFAULT_FACE_NOT_DETECTED_SECONDS,
    DEFAULT_HEAD_PITCH_THRESHOLD,
    DEFAULT_HEAD_YAW_THRESHOLD,
    RISK_DANGER,
    RISK_HIGH,
    RISK_LOW,
    RISK_MEDIUM,
    STATUS_CLOSED_EYES,
    STATUS_DISTRACTED,
    STATUS_DROWSY,
    STATUS_FACE_NOT_DETECTED,
    STATUS_NORMAL,
    STATUS_TIRED,
    STATUS_YAWNING,
)


@dataclass
class DetectionMetrics:
    ear_value: float
    mar_value: float
    eyes_closed_frames: int = 0
    yawn_frames: int = 0
    ai_label: str = ""
    ai_confidence: float = 0.0
    drowsy_seconds: float = 0.0
    # Head pose angles (degrees)
    head_yaw: float = 0.0
    head_pitch: float = 0.0
    distracted_seconds: float = 0.0
    # Face not detected duration
    face_not_detected_seconds: float = 0.0


@dataclass
class DetectionResult:
    status: str
    risk_level: str
    should_alert: bool
    alert_type: Optional[str]
    message: str


class DrowsinessEngine:
    def __init__(
        self,
        *,
        ear_threshold: float,
        ear_consec_frames: int,
        mar_threshold: float,
        yawn_consec_frames: int,
        drowsy_alert_seconds: int,
        head_yaw_threshold: float = DEFAULT_HEAD_YAW_THRESHOLD,
        head_pitch_threshold: float = DEFAULT_HEAD_PITCH_THRESHOLD,
        distraction_seconds: float = DEFAULT_DISTRACTION_SECONDS,
        face_not_detected_seconds: float = DEFAULT_FACE_NOT_DETECTED_SECONDS,
    ) -> None:
        self.ear_threshold = ear_threshold
        self.ear_consec_frames = ear_consec_frames
        self.mar_threshold = mar_threshold
        self.yawn_consec_frames = yawn_consec_frames
        self.drowsy_alert_seconds = drowsy_alert_seconds
        self.head_yaw_threshold = head_yaw_threshold
        self.head_pitch_threshold = head_pitch_threshold
        self.distraction_seconds = distraction_seconds
        self.face_not_detected_seconds = face_not_detected_seconds

    def evaluate(self, metrics: DetectionMetrics) -> DetectionResult:
        # ----- Priority 1: DANGER — Prolonged eyes closed (nhắm mắt lâu) -----
        if (
            metrics.eyes_closed_frames >= self.ear_consec_frames * 2
            and metrics.ear_value <= self.ear_threshold
        ):
            return DetectionResult(
                status=STATUS_DROWSY,
                risk_level=RISK_DANGER,
                should_alert=True,
                alert_type=STATUS_DROWSY,
                message="NGUY HIEM! Nham mat qua lau. Can dung xe nghi ngoi ngay!",
            )

        # ----- Priority 2: HIGH — Eyes closed -----
        if (
            metrics.eyes_closed_frames >= self.ear_consec_frames
            and metrics.ear_value <= self.ear_threshold
        ):
            return DetectionResult(
                status=STATUS_CLOSED_EYES,
                risk_level=RISK_HIGH,
                should_alert=True,
                alert_type=STATUS_CLOSED_EYES,
                message="Mat da nham qua lau. Canh bao buon ngu!",
            )

        # ----- Priority 3: HIGH — AI model detects drowsy with high confidence -----
        if metrics.ai_label.lower() in {STATUS_DROWSY, STATUS_TIRED} and (
            metrics.ai_confidence >= 0.75
            or metrics.drowsy_seconds >= self.drowsy_alert_seconds
        ):
            return DetectionResult(
                status=STATUS_DROWSY,
                risk_level=RISK_HIGH,
                should_alert=True,
                alert_type=STATUS_DROWSY,
                message="AI phat hien nguy co buon ngu cao.",
            )

        # ----- Priority 4: HIGH — Face not detected for too long -----
        if metrics.face_not_detected_seconds >= self.face_not_detected_seconds:
            return DetectionResult(
                status=STATUS_FACE_NOT_DETECTED,
                risk_level=RISK_HIGH,
                should_alert=True,
                alert_type=STATUS_FACE_NOT_DETECTED,
                message="Khong tim thay khuon mat qua lau. Vui long nhin vao camera.",
            )

        # ----- Priority 5: MEDIUM — Distracted (quay mặt) -----
        is_looking_away = (
            abs(metrics.head_yaw) > self.head_yaw_threshold
            or abs(metrics.head_pitch) > self.head_pitch_threshold
        )
        if is_looking_away and metrics.distracted_seconds >= self.distraction_seconds:
            return DetectionResult(
                status=STATUS_DISTRACTED,
                risk_level=RISK_MEDIUM,
                should_alert=True,
                alert_type=STATUS_DISTRACTED,
                message="Mat tap trung! Dang khong nhin vao duong.",
            )

        # ----- Priority 6: MEDIUM — Yawning -----
        if (
            metrics.yawn_frames >= self.yawn_consec_frames
            and metrics.mar_value >= self.mar_threshold
        ):
            return DetectionResult(
                status=STATUS_YAWNING,
                risk_level=RISK_MEDIUM,
                should_alert=True,
                alert_type=STATUS_YAWNING,
                message="Phat hien ngap lien tuc.",
            )

        # ----- Priority 7: LOW — Mild fatigue signs from AI -----
        if metrics.ai_label.lower() == STATUS_TIRED:
            return DetectionResult(
                status=STATUS_TIRED,
                risk_level=RISK_LOW,
                should_alert=False,
                alert_type=None,
                message="Co dau hieu met moi nhe.",
            )

        # ----- Default: NORMAL -----
        return DetectionResult(
            status=STATUS_NORMAL,
            risk_level=RISK_LOW,
            should_alert=False,
            alert_type=None,
            message="Trang thai binh thuong.",
        )
