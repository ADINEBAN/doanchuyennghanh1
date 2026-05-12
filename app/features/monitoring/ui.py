"""Main monitoring dashboard."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from typing import Optional

from app.shared.widgets.alert_banner import AlertBanner
from app.shared.widgets.camera_view import CameraView


class DashboardWindow(QMainWindow):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    history_requested = pyqtSignal()
    statistics_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    profile_requested = pyqtSignal()
    logout_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Bảng điều khiển - Giám sát tài xế")
        self.resize(1240, 760)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(12)

        # ---- Header: user + company + vehicle + session ----
        header_panel = QFrame()
        header_panel.setObjectName("panel")
        header = QHBoxLayout()
        header.setContentsMargins(16, 12, 16, 12)
        header.setSpacing(14)
        self.user_label = QLabel("Tài xế: -")
        self.user_label.setStyleSheet("font-size: 16px; font-weight: 800; color: #172033;")
        self.company_label = QLabel("")
        self.vehicle_label = QLabel("")
        self.session_label = QLabel("Phiên: chờ")
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setMinimumWidth(150)
        self.session_label.setStyleSheet(
            "background-color: #e2e8f0; color: #334155; border-radius: 7px; "
            "padding: 7px 10px; font-weight: 700;"
        )

        left_header = QVBoxLayout()
        left_header.setSpacing(5)
        left_header.addWidget(self.user_label)

        company_vehicle_row = QHBoxLayout()
        company_vehicle_row.addWidget(self.company_label)
        company_vehicle_row.addWidget(self.vehicle_label)
        company_vehicle_row.addStretch()
        left_header.addLayout(company_vehicle_row)

        header.addLayout(left_header)
        header.addStretch()
        header.addWidget(self.session_label)
        header_panel.setLayout(header)

        # ---- Camera view ----
        self.camera_view = CameraView()

        # ---- Alert banner ----
        self.alert_banner = AlertBanner()

        # ---- Realtime metrics ----
        metrics_box = QGroupBox("Chỉ số thời gian thực")
        metrics_layout = QGridLayout(metrics_box)
        metrics_layout.setContentsMargins(14, 18, 14, 12)
        metrics_layout.setHorizontalSpacing(18)
        metrics_layout.setVerticalSpacing(8)

        self.status_value = QLabel("normal")
        self.risk_value = QLabel("low")
        self.ear_value = QLabel("0.00")
        self.mar_value = QLabel("0.00")
        self.ai_value = QLabel("-")
        self.yaw_value = QLabel("0.0 độ")
        self.pitch_value = QLabel("0.0 độ")

        labels = []
        for text in ("Trạng thái", "Mức rủi ro", "EAR", "MAR", "Góc ngang", "Góc dọc", "AI"):
            label = QLabel(text)
            label.setStyleSheet("color: #64748b; font-weight: 600;")
            labels.append(label)

        for value in (
            self.status_value,
            self.risk_value,
            self.ear_value,
            self.mar_value,
            self.yaw_value,
            self.pitch_value,
            self.ai_value,
        ):
            value.setStyleSheet("font-size: 15px; font-weight: 800; color: #172033;")

        metrics_layout.addWidget(labels[0], 0, 0)
        metrics_layout.addWidget(self.status_value, 0, 1)
        metrics_layout.addWidget(labels[1], 0, 2)
        metrics_layout.addWidget(self.risk_value, 0, 3)
        metrics_layout.addWidget(labels[2], 1, 0)
        metrics_layout.addWidget(self.ear_value, 1, 1)
        metrics_layout.addWidget(labels[3], 1, 2)
        metrics_layout.addWidget(self.mar_value, 1, 3)
        metrics_layout.addWidget(labels[4], 2, 0)
        metrics_layout.addWidget(self.yaw_value, 2, 1)
        metrics_layout.addWidget(labels[5], 2, 2)
        metrics_layout.addWidget(self.pitch_value, 2, 3)
        metrics_layout.addWidget(labels[6], 3, 0)
        metrics_layout.addWidget(self.ai_value, 3, 1, 1, 3)

        # ---- Action buttons ----
        actions = QHBoxLayout()
        actions.setSpacing(10)
        start_button = QPushButton("Bắt đầu giám sát")
        stop_button = QPushButton("Dừng")
        history_button = QPushButton("Lịch sử")
        statistics_button = QPushButton("Thống kê")
        settings_button = QPushButton("Cài đặt")
        profile_button = QPushButton("Hồ sơ")
        logout_button = QPushButton("Đăng xuất")

        start_button.setObjectName("primaryButton")
        stop_button.setObjectName("dangerButton")
        logout_button.setObjectName("secondaryButton")

        start_button.clicked.connect(self.start_requested.emit)
        stop_button.clicked.connect(self.stop_requested.emit)
        history_button.clicked.connect(self.history_requested.emit)
        statistics_button.clicked.connect(self.statistics_requested.emit)
        settings_button.clicked.connect(self.settings_requested.emit)
        profile_button.clicked.connect(self.profile_requested.emit)
        logout_button.clicked.connect(self.logout_requested.emit)

        actions.addWidget(start_button)
        actions.addWidget(stop_button)
        actions.addWidget(history_button)
        actions.addWidget(statistics_button)
        actions.addWidget(settings_button)
        actions.addWidget(profile_button)
        actions.addStretch()
        actions.addWidget(logout_button)

        layout.addWidget(header_panel)
        layout.addWidget(self.camera_view)
        layout.addWidget(self.alert_banner)
        layout.addWidget(metrics_box)
        layout.addLayout(actions)
        self.setCentralWidget(root)

    def set_current_user(self, full_name: str, email: str) -> None:
        display = full_name or email
        self.user_label.setText(f"Tài xế: {display}")

    def set_company_info(self, company_name: str, vehicle_plate: str) -> None:
        """Display company and assigned vehicle info."""
        if company_name:
            self.company_label.setText(f"Hãng xe: {company_name}")
            self.company_label.setStyleSheet("color: #2563eb; font-weight: 600;")
        else:
            self.company_label.setText("")

        if vehicle_plate:
            self.vehicle_label.setText(f"Xe: {vehicle_plate}")
            self.vehicle_label.setStyleSheet("color: #059669; font-weight: 600; margin-left: 12px;")
        else:
            self.vehicle_label.setText("")

    def set_session_status(self, text: str) -> None:
        labels = {
            "idle": "chờ",
            "connected": "đã kết nối",
            "running": "đang giám sát",
            "stopped": "đã dừng",
            "local mode": "chế độ cục bộ",
        }
        self.session_label.setText(f"Phiên: {labels.get(text, text)}")
        color = "#2563eb" if text in {"connected", "running"} else "#64748b"
        background = "#dbeafe" if text in {"connected", "running"} else "#e2e8f0"
        self.session_label.setStyleSheet(
            f"background-color: {background}; color: {color}; border-radius: 7px; "
            "padding: 7px 10px; font-weight: 700;"
        )

    def update_detection_state(
        self,
        *,
        status: str,
        risk_level: str,
        message: str,
        ear_value: Optional[float] = None,
        mar_value: Optional[float] = None,
        ai_value: str = "-",
        head_yaw: float = 0.0,
        head_pitch: float = 0.0,
    ) -> None:
        self.status_value.setText(status.upper())
        self.risk_value.setText(risk_level.upper())
        self.ear_value.setText(f"{ear_value:.2f}" if ear_value is not None else "-")
        self.mar_value.setText(f"{mar_value:.2f}" if mar_value is not None else "-")
        self.ai_value.setText(ai_value)
        self.yaw_value.setText(f"{head_yaw:.1f} độ")
        self.pitch_value.setText(f"{head_pitch:.1f} độ")

        # Color code the risk label
        risk_colors = {
            "low": "#16a34a",
            "medium": "#d97706",
            "high": "#dc2626",
            "danger": "#7f1d1d",
        }
        color = risk_colors.get(risk_level, "#64748b")
        self.risk_value.setStyleSheet(f"color: {color}; font-weight: 700;")
        self.status_value.setStyleSheet(f"color: {color}; font-weight: 700;")

        self.alert_banner.set_status(status, risk_level, message)
