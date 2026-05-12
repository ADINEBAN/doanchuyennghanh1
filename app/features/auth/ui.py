"""Authentication windows."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
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
        self.setWindowTitle("Driver Login")
        self.resize(480, 300)

        title = QLabel("Driver Drowsiness Monitor")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Dang nhap bang tai khoan duoc hang xe cap")
        subtitle.setStyleSheet("font-size: 13px; color: #64748b;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._submit)
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)

        form = QFormLayout()
        form.addRow("Email", self.email_input)
        form.addRow("Password", self.password_input)

        login_button = QPushButton("Dang nhap")
        login_button.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; "
            "padding: 10px; border-radius: 8px; font-weight: 600; font-size: 14px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
        )
        login_button.clicked.connect(self._submit)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addLayout(form)
        layout.addWidget(login_button)
        layout.addWidget(self.status_label)

    def _submit(self) -> None:
        self.login_submitted.emit(
            self.email_input.text().strip(),
            self.password_input.text(),
        )

    def set_status(self, message: str) -> None:
        self.status_label.setText(message)
