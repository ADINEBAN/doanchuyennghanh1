"""History window showing saved alerts."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
from typing import Optional

from app.shared.core.app_state import AlertEvent
from app.shared.utils.datetime_helper import format_datetime


class HistoryWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Lịch sử cảnh báo")
        self.resize(980, 560)

        title = QLabel("Lịch sử cảnh báo")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #172033;")
        subtitle = QLabel("Các cảnh báo gần đây của tài xế hiện tại")
        subtitle.setStyleSheet("color: #64748b;")

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Thời gian", "Loại", "Trạng thái", "Rủi ro", "EAR", "MAR"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.table)

    def set_alerts(self, alerts: list[AlertEvent]) -> None:
        self.table.setRowCount(len(alerts))
        for row, alert in enumerate(alerts):
            self.table.setItem(row, 0, QTableWidgetItem(format_datetime(alert.triggered_at)))
            self.table.setItem(row, 1, QTableWidgetItem(alert.alert_type))
            self.table.setItem(row, 2, QTableWidgetItem(alert.status_label))
            self.table.setItem(row, 3, QTableWidgetItem(alert.risk_level))
            self.table.setItem(row, 4, QTableWidgetItem(_format_metric(alert.ear_value)))
            self.table.setItem(row, 5, QTableWidgetItem(_format_metric(alert.mar_value)))


def _format_metric(value: Optional[float]) -> str:
    if value is None:
        return "-"
    return f"{value:.3f}"
