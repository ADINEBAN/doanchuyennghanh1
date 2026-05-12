"""Statistics window."""

from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from typing import Any

from app.shared.widgets.stats_chart import StatsChart


class StatisticsWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Statistics")
        self.resize(920, 520)

        self.summary_label = QLabel("No data yet.")
        self.breakdown_label = QLabel("")
        self.chart = StatsChart()

        layout = QVBoxLayout(self)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.breakdown_label)
        layout.addWidget(self.chart)

    def set_summary(self, summary: dict[str, object]) -> None:
        self.summary_label.setText(
            f"Total alerts: {summary.get('total_alerts', 0)} | "
            f"Top alert type: {summary.get('top_alert_type', '-')}"
        )
        type_items = summary.get("alerts_by_type", {})
        risk_items = summary.get("alerts_by_risk", {})
        self.breakdown_label.setText(
            f"By type: {_format_breakdown(type_items)} | By risk: {_format_breakdown(risk_items)}"
        )
        self.chart.plot_summary(
            summary.get("alerts_by_day", {}),
            summary.get("alerts_by_type", {}),
        )


def _format_breakdown(values: Any) -> str:
    if not isinstance(values, dict) or not values:
        return "-"
    return ", ".join(f"{key}={value}" for key, value in values.items())
