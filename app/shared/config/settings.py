"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional before deps are installed
    load_dotenv = None


def _load_env_file(env_file: str) -> None:
    """Load .env values even when python-dotenv is not installed yet."""
    if load_dotenv is not None:
        load_dotenv(env_file)
        return

    env_path = Path(env_file)
    if not env_path.is_absolute():
        env_path = Path.cwd() / env_path
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass
class AppSettings:
    app_env: str = "development"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    default_camera_index: int = 0
    model_path: str = "ml/exported_models/drowsiness_model.keras"
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
    alert_sound_path: str = "assets/sounds/alert.wav"

    @property
    def supabase_enabled(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    @property
    def resolved_model_path(self) -> Path:
        return self.project_root / self.model_path

    @property
    def resolved_alert_sound_path(self) -> Path:
        return self.project_root / self.alert_sound_path


def load_settings(env_file: str = ".env") -> AppSettings:
    _load_env_file(env_file)

    return AppSettings(
        app_env=os.getenv("APP_ENV", "development"),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
        default_camera_index=_get_int("DEFAULT_CAMERA_INDEX", 0),
        model_path=os.getenv("MODEL_PATH", "ml/exported_models/drowsiness_model.keras"),
        ear_threshold=_get_float("EAR_THRESHOLD", 0.23),
        ear_consec_frames=_get_int("EAR_CONSEC_FRAMES", 20),
        mar_threshold=_get_float("MAR_THRESHOLD", 0.65),
        yawn_consec_frames=_get_int("YAWN_CONSEC_FRAMES", 15),
        ai_prediction_interval=_get_int("AI_PREDICTION_INTERVAL", 5),
        drowsy_alert_seconds=_get_int("DROWSY_ALERT_SECONDS", 2),
        head_yaw_threshold=_get_float("HEAD_YAW_THRESHOLD", 30.0),
        head_pitch_threshold=_get_float("HEAD_PITCH_THRESHOLD", 25.0),
        distraction_seconds=_get_int("DISTRACTION_SECONDS", 3),
        face_not_detected_seconds=_get_int("FACE_NOT_DETECTED_SECONDS", 5),
        alert_sound_path=os.getenv("ALERT_SOUND_PATH", "assets/sounds/alert.wav"),
    )
