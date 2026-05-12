"""Driver profile window."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from urllib.request import urlopen

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.shared.core.app_state import CompanyInfo, UserProfile, VehicleInfo


class ProfileWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Hồ sơ tài xế")
        self.resize(720, 520)

        self.avatar_label = QLabel("--")
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setFixedSize(104, 104)
        self.avatar_label.setStyleSheet(
            "background-color: #dbeafe; color: #1d4ed8; border-radius: 52px; "
            "font-size: 32px; font-weight: 900;"
        )

        self.name_label = QLabel("-")
        self.name_label.setStyleSheet("font-size: 24px; font-weight: 900; color: #172033;")

        self.role_label = QLabel("DRIVER")
        self.role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.role_label.setStyleSheet(
            "background-color: #dcfce7; color: #166534; border-radius: 7px; "
            "padding: 6px 10px; font-weight: 800;"
        )

        header = QFrame()
        header.setObjectName("panel")
        header_layout = QGridLayout(header)
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setHorizontalSpacing(18)
        header_layout.addWidget(self.avatar_label, 0, 0, 2, 1)
        header_layout.addWidget(self.name_label, 0, 1)
        header_layout.addWidget(self.role_label, 0, 2)

        self.email_value = QLabel("-")
        self.phone_value = QLabel("-")
        self.username_value = QLabel("-")
        self.status_value = QLabel("-")
        self.company_value = QLabel("-")
        self.company_phone_value = QLabel("-")
        self.vehicle_plate_value = QLabel("-")
        self.vehicle_model_value = QLabel("-")
        self.vehicle_status_value = QLabel("-")

        info_panel = QFrame()
        info_panel.setObjectName("panel")
        info_layout = QGridLayout(info_panel)
        info_layout.setContentsMargins(18, 18, 18, 18)
        info_layout.setHorizontalSpacing(22)
        info_layout.setVerticalSpacing(12)

        self._add_row(info_layout, 0, "Email", self.email_value)
        self._add_row(info_layout, 1, "Số điện thoại", self.phone_value)
        self._add_row(info_layout, 2, "Tên đăng nhập", self.username_value)
        self._add_row(info_layout, 3, "Trạng thái", self.status_value)
        self._add_row(info_layout, 4, "Hãng xe", self.company_value)
        self._add_row(info_layout, 5, "Điện thoại hãng", self.company_phone_value)
        self._add_row(info_layout, 6, "Biển số xe", self.vehicle_plate_value)
        self._add_row(info_layout, 7, "Dòng xe", self.vehicle_model_value)
        self._add_row(info_layout, 8, "Trạng thái xe", self.vehicle_status_value)

        close_button = QPushButton("Đóng")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(header)
        layout.addWidget(info_panel)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

    def set_profile(
        self,
        user: UserProfile,
        company: Optional[CompanyInfo],
        vehicle: Optional[VehicleInfo],
    ) -> None:
        display_name = user.full_name or user.email
        if not self._set_avatar_image(user.avatar_url):
            self.avatar_label.setPixmap(QPixmap())
            self.avatar_label.setText(_initials(display_name))
        self.name_label.setText(display_name)
        self.role_label.setText(user.role)
        self.email_value.setText(user.email or "-")
        self.phone_value.setText(user.phone or "-")
        self.username_value.setText(user.username or "-")
        self.status_value.setText(_status_label(user.status))

        if company is None:
            self.company_value.setText("-")
            self.company_phone_value.setText("-")
        else:
            self.company_value.setText(company.name or "-")
            self.company_phone_value.setText(company.phone or "-")

        if vehicle is None:
            self.vehicle_plate_value.setText("-")
            self.vehicle_model_value.setText("-")
            self.vehicle_status_value.setText("-")
        else:
            self.vehicle_plate_value.setText(vehicle.license_plate or "-")
            model = " ".join(
                value for value in (vehicle.brand, vehicle.model, str(vehicle.year or ""))
                if value
            )
            self.vehicle_model_value.setText(model or "-")
            self.vehicle_status_value.setText(_status_label(vehicle.status))

    @staticmethod
    def _add_row(layout: QGridLayout, row: int, label: str, value: QLabel) -> None:
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #64748b; font-weight: 700;")
        value.setStyleSheet("color: #172033; font-weight: 800;")
        value.setWordWrap(True)
        layout.addWidget(label_widget, row, 0)
        layout.addWidget(value, row, 1)

    def _set_avatar_image(self, avatar_url: str) -> bool:
        if not avatar_url:
            return False

        pixmap = QPixmap()
        try:
            if avatar_url.startswith(("http://", "https://")):
                with urlopen(avatar_url, timeout=3) as response:
                    pixmap.loadFromData(response.read())
            else:
                path = Path(avatar_url)
                if not path.is_absolute():
                    path = Path.cwd() / path
                pixmap.load(str(path))
        except Exception:
            return False

        if pixmap.isNull():
            return False

        self.avatar_label.setText("")
        self.avatar_label.setPixmap(
            pixmap.scaled(
                self.avatar_label.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        return True


def _initials(name: str) -> str:
    parts = [part for part in name.replace("@", " ").replace(".", " ").split() if part]
    if not parts:
        return "--"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f"{parts[0][0]}{parts[-1][0]}".upper()


def _status_label(status: str) -> str:
    labels = {
        "active": "Đang hoạt động",
        "inactive": "Không hoạt động",
        "locked": "Đã khóa",
        "assigned": "Đã gán",
        "available": "Sẵn sàng",
        "maintenance": "Bảo trì",
    }
    return labels.get(status, status or "-")
