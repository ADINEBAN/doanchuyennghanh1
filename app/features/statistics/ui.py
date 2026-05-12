"""Statistics window."""

from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from typing import Any

from app.shared.widgets.stats_chart import StatsChart


class StatisticsWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Thống kê")
        self.resize(980, 560)

        self.summary_label = QLabel("Chưa có dữ liệu.")
        self.summary_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #172033;")
        self.breakdown_label = QLabel("")
        self.breakdown_label.setStyleSheet("color: #64748b; font-weight: 600;")
        self.chart = StatsChart()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.breakdown_label)
        layout.addWidget(self.chart)

    def set_summary(self, summary: dict[str, object]) -> None:
        self.summary_label.setText(
            f"Tổng cảnh báo: {summary.get('total_alerts', 0)} | "
            f"Loại nhiều nhất: {summary.get('top_alert_type', '-')}"
        )
        type_items = summary.get("alerts_by_type", {})
        risk_items = summary.get("alerts_by_risk", {})
        self.breakdown_label.setText(
            f"Theo loại: {_format_breakdown(type_items)} | Theo rủi ro: {_format_breakdown(risk_items)}"
        )
        self.chart.plot_summary(
            summary.get("alerts_by_day", {}),
            summary.get("alerts_by_type", {}),
        )


def _format_breakdown(values: Any) -> str:
    if not isinstance(values, dict) or not values:
        return "-"
    return ", ".join(f"{key}={value}" for key, value in values.items())
