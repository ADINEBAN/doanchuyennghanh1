"""Application entry point."""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from app.ai.predictor import DrowsinessPredictor
from app.features.auth.service import AuthService
from app.features.auth.ui import LoginWindow
from app.features.history.ui import HistoryWindow
from app.features.monitoring.alert_service import AlertService
from app.features.monitoring.engine import DetectionMetrics, DrowsinessEngine
from app.features.monitoring.frame import resize_frame, to_rgb
from app.features.monitoring.landmark import FaceLandmarkDetector
from app.features.monitoring.live_status_service import LiveStatusService
from app.features.monitoring.metrics import eye_aspect_ratio, mouth_aspect_ratio
from app.features.monitoring.overlay import draw_contour, draw_monitoring_overlay, draw_points
from app.features.monitoring.session_service import SessionService
from app.features.monitoring.ui import DashboardWindow
from app.features.monitoring.webcam import WebcamManager
from app.features.profile.ui import ProfileWindow
from app.features.settings.service import SettingsService
from app.features.settings.ui import SettingsWindow
from app.features.statistics.ui import StatisticsWindow
from app.shared.config.constants import (
    APP_NAME,
)
from app.shared.config.settings import load_settings
from app.shared.core.app_state import AppState, UserSettingsState
from app.shared.core.exceptions import AuthenticationError, CameraError
from app.shared.core.signals import AppSignals
from app.shared.database.supabase_service import SupabaseService
from app.shared.utils.audio_player import AudioPlayer
from app.shared.utils.logger import configure_logging


LOGGER = logging.getLogger(__name__)


class AppController:
    def __init__(self, qt_app: QApplication) -> None:
        self.qt_app = qt_app
        self.settings = load_settings()
        self.state = AppState()
        self.signals = AppSignals()
        self.audio_player = AudioPlayer()

        self.supabase_service = SupabaseService(self.settings)
        self.auth_service = AuthService(self.supabase_service)
        self.session_service = SessionService(self.supabase_service)
        self.alert_service = AlertService(self.supabase_service)
        self.live_status_service = LiveStatusService(self.supabase_service)
        self.settings_service = SettingsService(self.supabase_service, self.settings)

        self.login_window = LoginWindow()
        self.dashboard_window = DashboardWindow()
        self.history_window = HistoryWindow()
        self.statistics_window = StatisticsWindow()
        self.settings_window = SettingsWindow()
        self.profile_window = ProfileWindow()
        self.webcam_manager: Optional[WebcamManager] = None
        self.landmark_detector = FaceLandmarkDetector()
        self.drowsiness_engine: Optional[DrowsinessEngine] = None
        self.predictor: Optional[DrowsinessPredictor] = None
        self.camera_timer = QTimer()
        self.camera_timer.setInterval(33)
        self.camera_timer.timeout.connect(self._pull_camera_frame)
        self.live_status_timer = QTimer()
        self.live_status_timer.setInterval(5000)
        self.live_status_timer.timeout.connect(self._send_live_presence)

        # Detection state counters
        self._frame_counter = 0
        self._eyes_closed_frames = 0
        self._yawn_frames = 0
        self._status_started_at = time.monotonic()
        self._last_alert_frame = -1000
        self._last_alert_type: Optional[str] = None
        self._last_live_status_at = 0.0
        self._last_live_status = "normal"
        self._last_live_risk_level = "low"

        # Distraction / face-not-detected tracking
        self._distracted_since: Optional[float] = None
        self._face_not_detected_since: Optional[float] = None
        self._last_head_yaw = 0.0
        self._last_head_pitch = 0.0

        self._apply_stylesheet()
        self._connect_ui()
        self.qt_app.aboutToQuit.connect(self._cleanup_runtime)

    def _apply_stylesheet(self) -> None:
        stylesheet_path = Path(__file__).resolve().parent / "shared" / "styles" / "theme.qss"
        if stylesheet_path.exists():
            self.qt_app.setStyleSheet(stylesheet_path.read_text(encoding="utf-8"))

    def _connect_ui(self) -> None:
        self.login_window.login_submitted.connect(self.handle_login)

        self.dashboard_window.start_requested.connect(self.start_monitoring)
        self.dashboard_window.stop_requested.connect(self.stop_monitoring)
        self.dashboard_window.history_requested.connect(self.show_history)
        self.dashboard_window.statistics_requested.connect(self.show_statistics)
        self.dashboard_window.settings_requested.connect(self.show_settings)
        self.dashboard_window.profile_requested.connect(self.show_profile)
        self.dashboard_window.logout_requested.connect(self.handle_logout)

        self.settings_window.save_requested.connect(self.save_settings)

    # ------------------------------------------------------------------
    # Auth flow
    # ------------------------------------------------------------------

    def show_login(self) -> None:
        self.dashboard_window.hide()
        self.login_window.show()

    def handle_login(self, email: str, password: str) -> None:
        try:
            user = self.auth_service.sign_in(email, password)
        except AuthenticationError as exc:
            self.login_window.set_status(str(exc))
            return

        self.state.current_user = user
        self.state.demo_mode = not self.supabase_service.is_configured()
        self.state.current_settings = self.settings_service.get_settings(user.id)

        # Fetch company and vehicle info
        self.state.current_company = self.auth_service.fetch_company(user.company_id)
        self.state.current_vehicle = self.auth_service.fetch_assigned_vehicle(user.id)

        # Try to load the AI predictor
        self._init_predictor()

        # Update dashboard
        self.dashboard_window.set_current_user(user.full_name, user.email)

        company_name = self.state.current_company.name if self.state.current_company else ""
        vehicle_plate = self.state.current_vehicle.license_plate if self.state.current_vehicle else ""
        self.dashboard_window.set_company_info(company_name, vehicle_plate)
        self.live_status_service.mark_online(
            driver_id=user.id,
            company_id=self.state.current_company.id if self.state.current_company else None,
            vehicle_id=self.state.current_vehicle.id if self.state.current_vehicle else None,
        )
        self.live_status_timer.start()

        self.dashboard_window.set_session_status(
            "local mode" if self.state.demo_mode else "connected"
        )
        self.dashboard_window.update_detection_state(
            status="normal",
            risk_level="low",
            message="Sẵn sàng bắt đầu giám sát.",
        )
        self.login_window.hide()
        self.dashboard_window.show()

    def handle_logout(self) -> None:
        driver_id = self.state.current_user.id if self.state.current_user else None
        self.live_status_timer.stop()
        self.stop_monitoring()
        if driver_id:
            self.live_status_service.mark_offline(driver_id=driver_id)
        self.auth_service.sign_out()
        self.state.current_user = None
        self.state.current_settings = None
        self.state.current_session = None
        self.state.current_company = None
        self.state.current_vehicle = None
        self.predictor = None
        self.dashboard_window.hide()
        self.show_login()

    # ------------------------------------------------------------------
    # AI Predictor
    # ------------------------------------------------------------------

    def _init_predictor(self) -> None:
        """Initialize the AI predictor if a model file exists."""
        model_name = ""
        if self.state.current_settings:
            model_name = self.state.current_settings.selected_model_name

        model_path = self.settings.resolved_model_path
        if model_name:
            candidate = self.settings.project_root / "ml" / "exported_models" / model_name
            if candidate.exists():
                model_path = candidate

        self.predictor = DrowsinessPredictor(model_path)
        if self.predictor.is_ready:
            LOGGER.info("AI predictor loaded: %s", model_path)
        else:
            LOGGER.info("AI predictor not available (model not found or lib missing).")

    # ------------------------------------------------------------------
    # Monitoring
    # ------------------------------------------------------------------

    def start_monitoring(self) -> None:
        if self.state.current_user is None:
            return
        if self.state.current_session is not None:
            return

        camera_index = 0
        if self.state.current_settings is not None:
            camera_index = self.state.current_settings.camera_index

        self.webcam_manager = WebcamManager(camera_index)
        try:
            self.webcam_manager.open()
            # Fail fast here if the landmark backend cannot be initialized.
            self.landmark_detector._ensure_face_mesh()
        except CameraError as exc:
            self._release_camera()
            error_message = str(exc)
            preview_message = "Camera not available."
            if "MediaPipe Face Mesh" in error_message:
                preview_message = "MediaPipe backend not available."
            self.dashboard_window.update_detection_state(
                status="normal",
                risk_level="medium",
                message=error_message,
            )
            self.dashboard_window.camera_view.show_message(preview_message)
            return

        self._reset_detection_state()
        self.drowsiness_engine = self._build_drowsiness_engine()

        # Determine company and vehicle IDs for the session
        company_id = None
        vehicle_id = None
        if self.state.current_company:
            company_id = self.state.current_company.id
        if self.state.current_vehicle:
            vehicle_id = self.state.current_vehicle.id

        self.state.current_session = self.session_service.start_session(
            self.state.current_user.id,
            company_id=company_id,
            vehicle_id=vehicle_id,
        )
        self.live_status_service.mark_monitoring(
            driver_id=self.state.current_user.id,
            session_id=self.state.current_session.id,
            company_id=company_id,
            vehicle_id=vehicle_id,
        )
        self._last_live_status = "normal"
        self._last_live_risk_level = "low"
        self._frame_counter = 0
        self.camera_timer.start()
        self.dashboard_window.set_session_status("running")
        self.dashboard_window.update_detection_state(
            status="normal",
            risk_level="low",
            message="Phiên giám sát đã bắt đầu. Webcam đang hoạt động.",
        )
        LOGGER.info("Started session %s", self.state.current_session.id)

    def stop_monitoring(self) -> None:
        self.camera_timer.stop()
        self._release_camera()
        self._reset_detection_state()

        if self.state.current_session is None:
            self.dashboard_window.camera_view.show_message("Xem trước camera")
            return

        session_alerts = self.alert_service.list_alerts_for_session(self.state.current_session.id)
        total_alerts = len(session_alerts)
        summary = self.alert_service.summarize_alerts(session_alerts)
        type_counts = summary.get("alerts_by_type", {})
        self.session_service.stop_session(
            self.state.current_session,
            total_alerts=total_alerts,
            closed_eyes_count=int(type_counts.get("closed_eyes", 0)),
            yawning_count=int(type_counts.get("yawning", 0)),
            drowsy_count=int(type_counts.get("drowsy", 0)),
            distraction_count=int(type_counts.get("distracted", 0)),
            face_not_detected_count=int(type_counts.get("face_not_detected", 0)),
        )
        self.live_status_service.mark_idle(
            driver_id=self.state.current_session.user_id,
            company_id=self.state.current_session.company_id,
            vehicle_id=self.state.current_session.vehicle_id,
        )
        self.dashboard_window.set_session_status("stopped")
        self.dashboard_window.update_detection_state(
            status="normal",
            risk_level="low",
            message=f"Phiên giám sát đã dừng. Tổng cảnh báo: {total_alerts}.",
        )
        self.dashboard_window.camera_view.show_message("Đã dừng giám sát.")
        self.state.current_session = None

    # ------------------------------------------------------------------
    # History / Statistics / Settings
    # ------------------------------------------------------------------

    def show_history(self) -> None:
        if self.state.current_user is None:
            return

        alerts = self.alert_service.list_alerts_for_user(self.state.current_user.id)
        self.history_window.set_alerts(alerts)
        self.history_window.show()

    def show_statistics(self) -> None:
        if self.state.current_user is None:
            return

        summary = self.alert_service.get_alert_summary(self.state.current_user.id)
        self.statistics_window.set_summary(summary)
        self.statistics_window.show()

    def show_settings(self) -> None:
        if self.state.current_user is None:
            return

        settings_state = self.settings_service.get_settings(self.state.current_user.id)
        self.state.current_settings = settings_state
        self.settings_window.load_settings(settings_state)
        self.settings_window.show()

    def show_profile(self) -> None:
        if self.state.current_user is None:
            return

        self.profile_window.set_profile(
            self.state.current_user,
            self.state.current_company,
            self.state.current_vehicle,
        )
        self.profile_window.show()

    def save_settings(self, settings_state: UserSettingsState) -> None:
        self.state.current_settings = self.settings_service.update_settings(settings_state)
        self.settings_window.close()
        self.dashboard_window.update_detection_state(
            status="normal",
            risk_level="low",
            message="Cài đặt đã lưu. Thay đổi sẽ áp dụng ở phiên giám sát tiếp theo.",
        )

    # ------------------------------------------------------------------
    # Frame processing loop
    # ------------------------------------------------------------------

    def _pull_camera_frame(self) -> None:
        if self.webcam_manager is None or self.drowsiness_engine is None:
            return

        try:
            frame = self.webcam_manager.read_frame()
        except CameraError as exc:
            LOGGER.exception("Failed while reading webcam frame")
            self.camera_timer.stop()
            self._release_camera()
            self.dashboard_window.update_detection_state(
                status="normal",
                risk_level="high",
                message=str(exc),
            )
            self.dashboard_window.camera_view.show_message("Camera stream interrupted.")
            return

        frame = resize_frame(frame)
        frame_rgb = to_rgb(frame)
        self._frame_counter += 1

        try:
            face_landmarks = self.landmark_detector.detect(frame_rgb)
        except CameraError as exc:
            LOGGER.exception("Landmark backend failed")
            self.camera_timer.stop()
            self._release_camera()
            self.dashboard_window.update_detection_state(
                status="normal",
                risk_level="high",
                message=str(exc),
            )
            self.dashboard_window.camera_view.show_message("MediaPipe backend not available.")
            return

        now = time.monotonic()

        # ---------- No face detected ----------
        if face_landmarks is None:
            self._eyes_closed_frames = 0
            self._yawn_frames = 0
            self._distracted_since = None
            self._last_head_yaw = 0.0
            self._last_head_pitch = 0.0

            if self._face_not_detected_since is None:
                self._face_not_detected_since = now
            face_not_detected_seconds = now - self._face_not_detected_since

            metrics = DetectionMetrics(
                ear_value=0.0,
                mar_value=0.0,
                face_not_detected_seconds=face_not_detected_seconds,
            )
            detection_result = self.drowsiness_engine.evaluate(metrics)

            draw_monitoring_overlay(
                frame_rgb,
                status=detection_result.status,
                risk_level=detection_result.risk_level,
                ear_value=0.0,
                mar_value=0.0,
                ear_threshold=self.drowsiness_engine.ear_threshold,
                mar_threshold=self.drowsiness_engine.mar_threshold,
                eyes_closed_frames=0,
                yawn_frames=0,
            )
            self.dashboard_window.camera_view.set_frame(frame_rgb)
            self.dashboard_window.update_detection_state(
                status=detection_result.status,
                risk_level=detection_result.risk_level,
                message=detection_result.message,
                ear_value=0.0,
                mar_value=0.0,
                ai_value="-",
            )

            if detection_result.should_alert:
                self._handle_detection_alert(detection_result, 0.0, 0.0)

            self._maybe_update_live_status(
                status=detection_result.status,
                risk_level=detection_result.risk_level,
                ear_value=0.0,
                mar_value=0.0,
            )

            return

        # Face detected - reset face_not_detected timer
        self._face_not_detected_since = None

        feature_points = self.landmark_detector.extract_feature_points(
            face_landmarks,
            frame_width=frame_rgb.shape[1],
            frame_height=frame_rgb.shape[0],
        )
        left_ear = eye_aspect_ratio(feature_points.left_eye)
        right_ear = eye_aspect_ratio(feature_points.right_eye)
        ear_value = (left_ear + right_ear) / 2.0
        mar_value = mouth_aspect_ratio(feature_points.mouth)

        # Head pose for distraction
        head_pose = feature_points.head_pose
        self._last_head_yaw = head_pose.yaw
        self._last_head_pitch = head_pose.pitch

        is_looking_away = (
            abs(head_pose.yaw) > self.drowsiness_engine.head_yaw_threshold
            or abs(head_pose.pitch) > self.drowsiness_engine.head_pitch_threshold
        )

        if is_looking_away:
            if self._distracted_since is None:
                self._distracted_since = now
            distracted_seconds = now - self._distracted_since
        else:
            self._distracted_since = None
            distracted_seconds = 0.0

        # EAR/MAR frame counters
        if ear_value <= self.drowsiness_engine.ear_threshold:
            self._eyes_closed_frames += 1
        else:
            self._eyes_closed_frames = 0

        if mar_value >= self.drowsiness_engine.mar_threshold:
            self._yawn_frames += 1
        else:
            self._yawn_frames = 0

        # AI prediction (every N frames)
        ai_label = ""
        ai_confidence = 0.0
        ai_display = "-"
        prediction_interval = self.settings.ai_prediction_interval
        if self.state.current_settings:
            prediction_interval = self.state.current_settings.ai_prediction_interval

        if self.predictor and self.predictor.is_ready and self._frame_counter % prediction_interval == 0:
            result = self.predictor.predict(frame_rgb)
            ai_label = result.label
            ai_confidence = result.confidence
            ai_display = f"{ai_label} ({ai_confidence:.0%})"

        metrics = DetectionMetrics(
            ear_value=ear_value,
            mar_value=mar_value,
            eyes_closed_frames=self._eyes_closed_frames,
            yawn_frames=self._yawn_frames,
            drowsy_seconds=now - self._status_started_at,
            ai_label=ai_label,
            ai_confidence=ai_confidence,
            head_yaw=head_pose.yaw,
            head_pitch=head_pose.pitch,
            distracted_seconds=distracted_seconds,
        )
        detection_result = self.drowsiness_engine.evaluate(metrics)

        if detection_result.status == "normal":
            self._status_started_at = now

        # Draw overlays
        draw_points(frame_rgb, feature_points.left_eye, (14, 165, 233))
        draw_points(frame_rgb, feature_points.right_eye, (14, 165, 233))
        draw_points(frame_rgb, feature_points.mouth, (249, 115, 22))
        draw_contour(frame_rgb, feature_points.left_eye, (14, 165, 233))
        draw_contour(frame_rgb, feature_points.right_eye, (14, 165, 233))
        draw_contour(frame_rgb, feature_points.mouth, (249, 115, 22))
        draw_monitoring_overlay(
            frame_rgb,
            status=detection_result.status,
            risk_level=detection_result.risk_level,
            ear_value=ear_value,
            mar_value=mar_value,
            ear_threshold=self.drowsiness_engine.ear_threshold,
            mar_threshold=self.drowsiness_engine.mar_threshold,
            eyes_closed_frames=self._eyes_closed_frames,
            yawn_frames=self._yawn_frames,
            head_yaw=head_pose.yaw,
            head_pitch=head_pose.pitch,
        )
        self.dashboard_window.camera_view.set_frame(frame_rgb)
        self.dashboard_window.update_detection_state(
            status=detection_result.status,
            risk_level=detection_result.risk_level,
            message=detection_result.message,
            ear_value=ear_value,
            mar_value=mar_value,
            ai_value=ai_display,
            head_yaw=head_pose.yaw,
            head_pitch=head_pose.pitch,
        )

        if detection_result.should_alert:
            self._handle_detection_alert(
                detection_result, ear_value, mar_value,
                head_yaw=head_pose.yaw, head_pitch=head_pose.pitch,
                ai_label=ai_label, ai_confidence=ai_confidence,
            )

        self._maybe_update_live_status(
            status=detection_result.status,
            risk_level=detection_result.risk_level,
            ear_value=ear_value,
            mar_value=mar_value,
            head_yaw=head_pose.yaw,
            head_pitch=head_pose.pitch,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _release_camera(self) -> None:
        if self.webcam_manager is not None:
            self.webcam_manager.release()
            self.webcam_manager = None

    def _cleanup_runtime(self) -> None:
        self.camera_timer.stop()
        self.live_status_timer.stop()
        self._release_camera()
        if self.state.current_user is not None:
            self.live_status_service.mark_offline(driver_id=self.state.current_user.id)
        self.landmark_detector.close()

    def _send_live_presence(self) -> None:
        if self.state.current_user is None:
            return

        company_id = self.state.current_company.id if self.state.current_company else None
        vehicle_id = self.state.current_vehicle.id if self.state.current_vehicle else None

        if self.state.current_session is not None:
            self.live_status_service.update_metrics(
                driver_id=self.state.current_user.id,
                session_id=self.state.current_session.id,
                company_id=company_id,
                vehicle_id=vehicle_id,
                status=self._last_live_status,
                risk_level=self._last_live_risk_level,
            )
            return

        self.live_status_service.mark_online(
            driver_id=self.state.current_user.id,
            company_id=company_id,
            vehicle_id=vehicle_id,
        )

    def _maybe_update_live_status(
        self,
        *,
        status: str,
        risk_level: str,
        ear_value: Optional[float] = None,
        mar_value: Optional[float] = None,
        head_yaw: Optional[float] = None,
        head_pitch: Optional[float] = None,
    ) -> None:
        now = time.monotonic()
        if now - self._last_live_status_at < 2.0:
            return
        if self.state.current_user is None:
            return

        self._last_live_status_at = now
        self._last_live_status = status
        self._last_live_risk_level = risk_level
        self.live_status_service.update_metrics(
            driver_id=self.state.current_user.id,
            session_id=self.state.current_session.id if self.state.current_session else None,
            company_id=self.state.current_company.id if self.state.current_company else None,
            vehicle_id=self.state.current_vehicle.id if self.state.current_vehicle else None,
            status=status,
            risk_level=risk_level,
            ear_value=ear_value,
            mar_value=mar_value,
            head_yaw=head_yaw,
            head_pitch=head_pitch,
        )

    def _build_drowsiness_engine(self) -> DrowsinessEngine:
        settings_state = self.state.current_settings
        if settings_state is None:
            return DrowsinessEngine(
                ear_threshold=self.settings.ear_threshold,
                ear_consec_frames=self.settings.ear_consec_frames,
                mar_threshold=self.settings.mar_threshold,
                yawn_consec_frames=self.settings.yawn_consec_frames,
                drowsy_alert_seconds=self.settings.drowsy_alert_seconds,
                head_yaw_threshold=self.settings.head_yaw_threshold,
                head_pitch_threshold=self.settings.head_pitch_threshold,
                distraction_seconds=self.settings.distraction_seconds,
                face_not_detected_seconds=self.settings.face_not_detected_seconds,
            )

        return DrowsinessEngine(
            ear_threshold=settings_state.ear_threshold,
            ear_consec_frames=settings_state.ear_consec_frames,
            mar_threshold=settings_state.mar_threshold,
            yawn_consec_frames=settings_state.yawn_consec_frames,
            drowsy_alert_seconds=settings_state.drowsy_alert_seconds,
            head_yaw_threshold=settings_state.head_yaw_threshold,
            head_pitch_threshold=settings_state.head_pitch_threshold,
            distraction_seconds=settings_state.distraction_seconds,
            face_not_detected_seconds=settings_state.face_not_detected_seconds,
        )

    def _handle_detection_alert(
        self,
        detection_result,
        ear_value: float,
        mar_value: float,
        *,
        head_yaw: float = 0.0,
        head_pitch: float = 0.0,
        ai_label: Optional[str] = None,
        ai_confidence: Optional[float] = None,
    ) -> None:
        if self.state.current_user is None or self.state.current_session is None:
            return

        is_duplicate = (
            detection_result.alert_type == self._last_alert_type
            and self._frame_counter - self._last_alert_frame < 45
        )
        if is_duplicate:
            return

        if self.state.current_settings is None or self.state.current_settings.alert_sound_enabled:
            sound_path = self.settings.resolved_alert_sound_path
            if self.state.current_settings is not None and self.state.current_settings.alert_sound_path:
                sound_path = self.settings.project_root / self.state.current_settings.alert_sound_path
            self.audio_player.play(sound_path)

        # Determine company/vehicle from state
        company_id = self.state.current_company.id if self.state.current_company else None
        vehicle_id = self.state.current_vehicle.id if self.state.current_vehicle else None

        self.alert_service.create_alert(
            user_id=self.state.current_user.id,
            session_id=self.state.current_session.id,
            alert_type=detection_result.alert_type or detection_result.status,
            risk_level=detection_result.risk_level,
            status_label=detection_result.status,
            company_id=company_id,
            vehicle_id=vehicle_id,
            ear_value=ear_value,
            mar_value=mar_value,
            head_yaw=head_yaw,
            head_pitch=head_pitch,
            ai_label=ai_label,
            ai_confidence=ai_confidence,
        )
        self._last_alert_type = detection_result.alert_type
        self._last_alert_frame = self._frame_counter

    def _reset_detection_state(self) -> None:
        self._frame_counter = 0
        self._eyes_closed_frames = 0
        self._yawn_frames = 0
        self._status_started_at = time.monotonic()
        self._last_alert_frame = -1000
        self._last_alert_type = None
        self._last_live_status_at = 0.0
        self._distracted_since = None
        self._face_not_detected_since = None
        self._last_head_yaw = 0.0
        self._last_head_pitch = 0.0
        self.drowsiness_engine = None


def main() -> int:
    configure_logging()
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName(APP_NAME)
    controller = AppController(qt_app)
    controller.show_login()
    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
