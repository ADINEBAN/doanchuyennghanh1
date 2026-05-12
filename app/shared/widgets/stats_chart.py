"""Statistics chart widget."""

from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from typing import Optional

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
except ImportError:  # pragma: no cover - optional until dependencies are installed
    FigureCanvas = None
    Figure = None


class StatsChart(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)

        if FigureCanvas is None or Figure is None:
            self.placeholder = QLabel("Install matplotlib to render charts.")
            self.layout.addWidget(self.placeholder)
            self.figure = None
            self.canvas = None
            return

        self.figure = Figure(figsize=(6, 3))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def plot_summary(
        self,
        alerts_by_day: dict[str, int],
        alerts_by_type: Optional[dict[str, int]] = None,
    ) -> None:
        if self.figure is None or self.canvas is None:
            return

        self.figure.clear()
        day_axis = self.figure.add_subplot(121)
        labels = list(alerts_by_day.keys())
        values = list(alerts_by_day.values())
        day_axis.bar(labels, values, color="#0f766e")
        day_axis.set_title("Alerts By Day")
        day_axis.set_ylabel("Count")
        day_axis.tick_params(axis="x", rotation=25)

        type_axis = self.figure.add_subplot(122)
        type_data = alerts_by_type or {}
        if type_data:
            type_axis.pie(
                list(type_data.values()),
                labels=list(type_data.keys()),
                autopct="%1.0f%%",
                startangle=90,
            )
            type_axis.set_title("Alert Types")
        else:
            type_axis.text(0.5, 0.5, "No alert type data", ha="center", va="center")
            type_axis.set_axis_off()

        self.figure.tight_layout()
        self.canvas.draw()
