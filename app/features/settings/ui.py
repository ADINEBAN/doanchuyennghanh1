"""Settings window."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QLabel,
)

from app.shared.core.app_state import UserSettingsState


class SettingsWindow(QDialog):
    save_requested = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Cài đặt")
        self.resize(620, 520)
        self._user_id = ""

        self.ear_threshold = QDoubleSpinBox()
        self.ear_threshold.setRange(0.01, 1.0)
        self.ear_threshold.setSingleStep(0.01)

        self.ear_consec_frames = QSpinBox()
        self.ear_consec_frames.setRange(1, 300)

        self.mar_threshold = QDoubleSpinBox()
        self.mar_threshold.setRange(0.01, 2.0)
        self.mar_threshold.setSingleStep(0.01)

        self.yawn_consec_frames = QSpinBox()
        self.yawn_consec_frames.setRange(1, 300)

        self.ai_prediction_interval = QSpinBox()
        self.ai_prediction_interval.setRange(1, 60)

        self.drowsy_alert_seconds = QSpinBox()
        self.drowsy_alert_seconds.setRange(1, 30)

        self.camera_index = QSpinBox()
        self.camera_index.setRange(0, 10)

        self.selected_model_name = QLineEdit()
        self.alert_sound_path = QLineEdit()
        self.alert_sound_enabled = QCheckBox("Bật âm thanh cảnh báo")

        title = QLabel("Cài đặt giám sát")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #172033;")
        subtitle = QLabel("Thay đổi sẽ áp dụng từ phiên giám sát tiếp theo")
        subtitle.setStyleSheet("color: #64748b;")

        form = QFormLayout()
        form.setSpacing(12)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.addRow("Ngưỡng EAR", self.ear_threshold)
        form.addRow("Số frame nhắm mắt", self.ear_consec_frames)
        form.addRow("Ngưỡng MAR", self.mar_threshold)
        form.addRow("Số frame ngáp", self.yawn_consec_frames)
        form.addRow("Chu kỳ dự đoán AI", self.ai_prediction_interval)
        form.addRow("Giây cảnh báo buồn ngủ", self.drowsy_alert_seconds)
        form.addRow("Camera index", self.camera_index)
        form.addRow("Tên model", self.selected_model_name)
        form.addRow("Đường dẫn âm thanh", self.alert_sound_path)
        form.addRow("", self.alert_sound_enabled)

        save_button = QPushButton("Lưu")
        close_button = QPushButton("Đóng")
        save_button.setObjectName("primaryButton")
        close_button.setObjectName("secondaryButton")
        save_button.clicked.connect(self._submit)
        close_button.clicked.connect(self.close)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(save_button)
        actions.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)
        layout.addLayout(actions)

    def load_settings(self, settings_state: UserSettingsState) -> None:
        self._user_id = settings_state.user_id
        self.ear_threshold.setValue(settings_state.ear_threshold)
        self.ear_consec_frames.setValue(settings_state.ear_consec_frames)
        self.mar_threshold.setValue(settings_state.mar_threshold)
        self.yawn_consec_frames.setValue(settings_state.yawn_consec_frames)
        self.ai_prediction_interval.setValue(settings_state.ai_prediction_interval)
        self.drowsy_alert_seconds.setValue(settings_state.drowsy_alert_seconds)
        self.camera_index.setValue(settings_state.camera_index)
        self.selected_model_name.setText(settings_state.selected_model_name)
        self.alert_sound_path.setText(settings_state.alert_sound_path)
        self.alert_sound_enabled.setChecked(settings_state.alert_sound_enabled)

    def _submit(self) -> None:
        self.save_requested.emit(
            UserSettingsState(
                user_id=self._user_id,
                ear_threshold=self.ear_threshold.value(),
                ear_consec_frames=self.ear_consec_frames.value(),
                mar_threshold=self.mar_threshold.value(),
                yawn_consec_frames=self.yawn_consec_frames.value(),
                ai_prediction_interval=self.ai_prediction_interval.value(),
                drowsy_alert_seconds=self.drowsy_alert_seconds.value(),
                selected_model_name=self.selected_model_name.text().strip(),
                alert_sound_enabled=self.alert_sound_enabled.isChecked(),
                alert_sound_path=self.alert_sound_path.text().strip(),
                camera_index=self.camera_index.value(),
            )
        )
