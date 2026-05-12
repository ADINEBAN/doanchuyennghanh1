export function formatDateTime(value: string | null | undefined) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatDuration(seconds: number | null | undefined) {
  if (!seconds) return "-";
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  if (minutes <= 0) return `${rest}s`;
  return `${minutes}m ${rest}s`;
}

export function roleLabel(role: string) {
  const labels: Record<string, string> = {
    SUPER_ADMIN: "Quản trị hệ thống",
    COMPANY_ADMIN: "Quản lý hãng xe",
    DRIVER: "Tài xế",
  };
  return labels[role] ?? role;
}

export function statusLabel(status: string | null | undefined) {
  const labels: Record<string, string> = {
    active: "Đang hoạt động",
    inactive: "Không hoạt động",
    locked: "Đã khóa",
    running: "Đang chạy",
    stopped: "Đã dừng",
    interrupted: "Gián đoạn",
    assigned: "Đã gán",
    available: "Sẵn sàng",
    maintenance: "Bảo trì",
    low: "Thấp",
    medium: "Trung bình",
    high: "Cao",
    danger: "Nguy hiểm",
  };
  return labels[status ?? ""] ?? status ?? "-";
}

export function alertTypeLabel(type: string | null | undefined) {
  const labels: Record<string, string> = {
    closed_eyes: "Nhắm mắt",
    yawning: "Ngáp",
    drowsy: "Buồn ngủ",
    distracted: "Mất tập trung",
    face_not_detected: "Không thấy mặt",
  };
  return labels[type ?? ""] ?? type ?? "-";
}
