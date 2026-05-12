"""User settings persistence service."""

from __future__ import annotations

from app.shared.config.settings import AppSettings
from app.shared.core.app_state import UserSettingsState
from app.shared.database.supabase_service import SupabaseService


class SettingsService:
    def __init__(self, supabase_service: SupabaseService, app_settings: AppSettings) -> None:
        self.supabase_service = supabase_service
        self.app_settings = app_settings
        self._local_settings: dict[str, UserSettingsState] = {}

    def get_settings(self, user_id: str) -> UserSettingsState:
        if not self.supabase_service.is_configured():
            return self._local_settings.setdefault(
                user_id,
                UserSettingsState(
                    user_id=user_id,
                    ear_threshold=self.app_settings.ear_threshold,
                    ear_consec_frames=self.app_settings.ear_consec_frames,
                    mar_threshold=self.app_settings.mar_threshold,
                    yawn_consec_frames=self.app_settings.yawn_consec_frames,
                    ai_prediction_interval=self.app_settings.ai_prediction_interval,
                    drowsy_alert_seconds=self.app_settings.drowsy_alert_seconds,
                    alert_sound_path=self.app_settings.alert_sound_path,
                    camera_index=self.app_settings.default_camera_index,
                ),
            )

        client = self.supabase_service.get_client()
        response = (
            client.table("user_settings")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        row = (response.data or [{}])[0]
        return UserSettingsState(
            user_id=user_id,
            ear_threshold=row.get("ear_threshold", self.app_settings.ear_threshold),
            ear_consec_frames=row.get("ear_consec_frames", self.app_settings.ear_consec_frames),
            mar_threshold=row.get("mar_threshold", self.app_settings.mar_threshold),
            yawn_consec_frames=row.get("yawn_consec_frames", self.app_settings.yawn_consec_frames),
            ai_prediction_interval=row.get(
                "ai_prediction_interval", self.app_settings.ai_prediction_interval
            ),
            drowsy_alert_seconds=row.get(
                "drowsy_alert_seconds", self.app_settings.drowsy_alert_seconds
            ),
            selected_model_name=row.get("selected_model_name", ""),
            alert_sound_enabled=row.get("alert_sound_enabled", True),
            alert_sound_path=row.get("alert_sound_path", self.app_settings.alert_sound_path),
            camera_index=row.get("camera_index", self.app_settings.default_camera_index),
        )

    def update_settings(self, settings_state: UserSettingsState) -> UserSettingsState:
        if not self.supabase_service.is_configured():
            self._local_settings[settings_state.user_id] = settings_state
            return settings_state

        client = self.supabase_service.get_client()
        payload = {
            "ear_threshold": settings_state.ear_threshold,
            "ear_consec_frames": settings_state.ear_consec_frames,
            "mar_threshold": settings_state.mar_threshold,
            "yawn_consec_frames": settings_state.yawn_consec_frames,
            "ai_prediction_interval": settings_state.ai_prediction_interval,
            "drowsy_alert_seconds": settings_state.drowsy_alert_seconds,
            "selected_model_name": settings_state.selected_model_name,
            "alert_sound_enabled": settings_state.alert_sound_enabled,
            "alert_sound_path": settings_state.alert_sound_path,
            "camera_index": settings_state.camera_index,
        }
        client.table("user_settings").update(payload).eq("user_id", settings_state.user_id).execute()
        return settings_state
