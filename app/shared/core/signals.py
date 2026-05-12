"""Qt signals shared by application modules."""

from PyQt6.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    login_succeeded = pyqtSignal(object)
    logout_completed = pyqtSignal()
    session_started = pyqtSignal(object)
    session_stopped = pyqtSignal(object)
    alert_triggered = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
