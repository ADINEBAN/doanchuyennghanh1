"""In-memory application state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class CompanyInfo:
    """Basic company information loaded after login."""
    id: str
    name: str
    address: str = ""
    phone: str = ""
    email: str = ""
    logo_url: str = ""
    status: str = "active"


@dataclass
class VehicleInfo:
    """Basic vehicle information loaded after login."""
    id: str
    company_id: str
    license_plate: str
    brand: str = ""
    model: str = ""
    color: str = ""
    year: Optional[int] = None
    status: str = "available"


@dataclass
class UserProfile:
    id: str
    email: str
    username: str = ""
    full_name: str = ""
    phone: str = ""
    avatar_url: str = ""
    role: str = "DRIVER"
    status: str = "active"
    company_id: Optional[str] = None


@dataclass
class UserSettingsState:
    user_id: str
    ear_threshold: float = 0.23
    ear_consec_frames: int = 20
    mar_threshold: float = 0.65
    yawn_consec_frames: int = 15
    ai_prediction_interval: int = 5
    drowsy_alert_seconds: int = 2
    head_yaw_threshold: float = 30.0
    head_pitch_threshold: float = 25.0
    distraction_seconds: int = 3
    face_not_detected_seconds: int = 5
    selected_model_name: str = ""
    alert_sound_enabled: bool = True
    alert_sound_path: str = "assets/sounds/alert.wav"
    camera_index: int = 0


@dataclass
class MonitoringSessionState:
    id: str
    user_id: str
    started_at: datetime
    company_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    status: str = "running"
    ended_at: Optional[datetime] = None
    total_alerts: int = 0
    closed_eyes_count: int = 0
    yawning_count: int = 0
    drowsy_count: int = 0
    distraction_count: int = 0
    face_not_detected_count: int = 0


@dataclass
class AlertEvent:
    id: str
    user_id: str
    session_id: str
    alert_type: str
    risk_level: str
    status_label: str
    triggered_at: datetime
    company_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    ear_value: Optional[float] = None
    mar_value: Optional[float] = None
    ai_label: Optional[str] = None
    ai_confidence: Optional[float] = None
    head_yaw: Optional[float] = None
    head_pitch: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AppState:
    current_user: Optional[UserProfile] = None
    current_settings: Optional[UserSettingsState] = None
    current_session: Optional[MonitoringSessionState] = None
    current_company: Optional[CompanyInfo] = None
    current_vehicle: Optional[VehicleInfo] = None
    demo_mode: bool = False
