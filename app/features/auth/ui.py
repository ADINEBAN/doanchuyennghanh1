"""Authentication windows."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LoginWindow(QWidget):
    """Login window for DRIVER only.

    DRIVER accounts are created by COMPANY_ADMIN through the web admin,
    so there is no self-registration option here.
    """

    login_submitted = pyqtSignal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Đăng nhập tài xế")
        self.resize(620, 460)

        badge = QLabel("Ứng dụng tài xế")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            "background-color: #dbeafe; color: #1d4ed8; border-radius: 7px; "
            "padding: 6px 10px; font-weight: 800;"
        )

        title = QLabel("Giám sát buồn ngủ")
        title.setStyleSheet("font-size: 28px; font-weight: 900; color: #172033;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Đăng nhập bằng tài khoản do hãng xe cấp")
        subtitle.setStyleSheet("font-size: 13px; color: #64748b;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._submit)
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #b91c1c; font-weight: 600;")

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.addRow("Email", self.email_input)
        form.addRow("Mật khẩu", self.password_input)

        login_button = QPushButton("Đăng nhập")
        login_button.setObjectName("primaryButton")
        login_button.setMinimumHeight(42)
        login_button.clicked.connect(self._submit)

        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMaximumWidth(440)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        panel_layout.setSpacing(14)
        panel_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(title)
        panel_layout.addWidget(subtitle)
        panel_layout.addSpacing(12)
        panel_layout.addLayout(form)
        panel_layout.addSpacing(4)
        panel_layout.addWidget(login_button)
        panel_layout.addWidget(self.status_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 38, 42, 38)
        layout.addStretch()
        layout.addWidget(panel, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def _submit(self) -> None:
        self.login_submitted.emit(
            self.email_input.text().strip(),
            self.password_input.text(),
        )

    def set_status(self, message: str) -> None:
        self.status_label.setText(message)
