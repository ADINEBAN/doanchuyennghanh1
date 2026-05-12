"""Application constants."""

APP_NAME = "Drowsiness Desktop App"
APP_WINDOW_WIDTH = 1240
APP_WINDOW_HEIGHT = 760

# ---------------------------------------------------------------------------
# Driver statuses — phân loại trạng thái tài xế
# ---------------------------------------------------------------------------
STATUS_NORMAL = "normal"
STATUS_TIRED = "tired"
STATUS_CLOSED_EYES = "closed_eyes"
STATUS_YAWNING = "yawning"
STATUS_DROWSY = "drowsy"
STATUS_DISTRACTED = "distracted"
STATUS_FACE_NOT_DETECTED = "face_not_detected"

# ---------------------------------------------------------------------------
# Risk levels — cảnh báo nhiều cấp độ
# ---------------------------------------------------------------------------
RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"
RISK_DANGER = "danger"

# ---------------------------------------------------------------------------
# Alert types — loại cảnh báo lưu DB
# ---------------------------------------------------------------------------
ALERT_TYPES = (
    STATUS_CLOSED_EYES,
    STATUS_YAWNING,
    STATUS_DROWSY,
    STATUS_DISTRACTED,
    STATUS_FACE_NOT_DETECTED,
)

# ---------------------------------------------------------------------------
# User roles
# ---------------------------------------------------------------------------
ROLE_SUPER_ADMIN = "SUPER_ADMIN"
ROLE_COMPANY_ADMIN = "COMPANY_ADMIN"
ROLE_DRIVER = "DRIVER"

# ---------------------------------------------------------------------------
# Head pose thresholds (degrees) — ngưỡng quay mặt mất tập trung
# ---------------------------------------------------------------------------
DEFAULT_HEAD_YAW_THRESHOLD = 30.0
DEFAULT_HEAD_PITCH_THRESHOLD = 25.0
DEFAULT_DISTRACTION_SECONDS = 3
DEFAULT_FACE_NOT_DETECTED_SECONDS = 5
