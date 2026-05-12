"""Main monitoring dashboard."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
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
    logout_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Dashboard — Driver Monitoring")
        self.resize(1240, 760)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setSpacing(8)

        # ---- Header: user + company + vehicle + session ----
        header = QHBoxLayout()
        self.user_label = QLabel("Tai xe: -")
        self.company_label = QLabel("")
        self.vehicle_label = QLabel("")
        self.session_label = QLabel("Session: idle")

        left_header = QVBoxLayout()
        left_header.setSpacing(2)
        left_header.addWidget(self.user_label)

        company_vehicle_row = QHBoxLayout()
        company_vehicle_row.addWidget(self.company_label)
        company_vehicle_row.addWidget(self.vehicle_label)
        company_vehicle_row.addStretch()
        left_header.addLayout(company_vehicle_row)

        header.addLayout(left_header)
        header.addStretch()
        header.addWidget(self.session_label)

        # ---- Camera view ----
        self.camera_view = CameraView()

        # ---- Alert banner ----
        self.alert_banner = AlertBanner()

        # ---- Realtime metrics ----
        metrics_box = QGroupBox("Realtime Metrics")
        metrics_layout = QGridLayout(metrics_box)
        metrics_layout.setSpacing(6)

        self.status_value = QLabel("normal")
        self.risk_value = QLabel("low")
        self.ear_value = QLabel("0.00")
        self.mar_value = QLabel("0.00")
        self.ai_value = QLabel("-")
        self.yaw_value = QLabel("0.0°")
        self.pitch_value = QLabel("0.0°")

        # Row 0
        metrics_layout.addWidget(QLabel("Status"), 0, 0)
        metrics_layout.addWidget(self.status_value, 0, 1)
        metrics_layout.addWidget(QLabel("Risk"), 0, 2)
        metrics_layout.addWidget(self.risk_value, 0, 3)
        # Row 1
        metrics_layout.addWidget(QLabel("EAR"), 1, 0)
        metrics_layout.addWidget(self.ear_value, 1, 1)
        metrics_layout.addWidget(QLabel("MAR"), 1, 2)
        metrics_layout.addWidget(self.mar_value, 1, 3)
        # Row 2
        metrics_layout.addWidget(QLabel("Yaw"), 2, 0)
        metrics_layout.addWidget(self.yaw_value, 2, 1)
        metrics_layout.addWidget(QLabel("Pitch"), 2, 2)
        metrics_layout.addWidget(self.pitch_value, 2, 3)
        # Row 3
        metrics_layout.addWidget(QLabel("AI"), 3, 0)
        metrics_layout.addWidget(self.ai_value, 3, 1, 1, 3)

        # ---- Action buttons ----
        actions = QHBoxLayout()
        start_button = QPushButton("Bat dau giam sat")
        stop_button = QPushButton("Dung")
        history_button = QPushButton("Lich su")
        statistics_button = QPushButton("Thong ke")
        settings_button = QPushButton("Cai dat")
        logout_button = QPushButton("Dang xuat")

        # Styling for primary action
        start_button.setStyleSheet(
            "QPushButton { background-color: #16a34a; color: white; "
            "padding: 8px 16px; border-radius: 6px; font-weight: 600; }"
            "QPushButton:hover { background-color: #15803d; }"
        )
        stop_button.setStyleSheet(
            "QPushButton { background-color: #dc2626; color: white; "
            "padding: 8px 16px; border-radius: 6px; font-weight: 600; }"
            "QPushButton:hover { background-color: #b91c1c; }"
        )

        start_button.clicked.connect(self.start_requested.emit)
        stop_button.clicked.connect(self.stop_requested.emit)
        history_button.clicked.connect(self.history_requested.emit)
        statistics_button.clicked.connect(self.statistics_requested.emit)
        settings_button.clicked.connect(self.settings_requested.emit)
        logout_button.clicked.connect(self.logout_requested.emit)

        actions.addWidget(start_button)
        actions.addWidget(stop_button)
        actions.addWidget(history_button)
        actions.addWidget(statistics_button)
        actions.addWidget(settings_button)
        actions.addStretch()
        actions.addWidget(logout_button)

        layout.addLayout(header)
        layout.addWidget(self.camera_view)
        layout.addWidget(self.alert_banner)
        layout.addWidget(metrics_box)
        layout.addLayout(actions)
        self.setCentralWidget(root)

    def set_current_user(self, full_name: str, email: str) -> None:
        display = full_name or email
        self.user_label.setText(f"Tai xe: {display}")

    def set_company_info(self, company_name: str, vehicle_plate: str) -> None:
        """Display company and assigned vehicle info."""
        if company_name:
            self.company_label.setText(f"Hang xe: {company_name}")
            self.company_label.setStyleSheet("color: #2563eb; font-weight: 600;")
        else:
            self.company_label.setText("")

        if vehicle_plate:
            self.vehicle_label.setText(f"Xe: {vehicle_plate}")
            self.vehicle_label.setStyleSheet("color: #059669; font-weight: 600; margin-left: 12px;")
        else:
            self.vehicle_label.setText("")

    def set_session_status(self, text: str) -> None:
        self.session_label.setText(f"Session: {text}")

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
        self.yaw_value.setText(f"{head_yaw:.1f}°")
        self.pitch_value.setText(f"{head_pitch:.1f}°")

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
