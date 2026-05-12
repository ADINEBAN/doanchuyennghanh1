import type { DriverLiveStatus } from "@/types/database";

export const LIVE_STATUS_FRESH_MS = 45000;
export const LIVE_STATUS_POLL_MS = 5000;

export function isLiveStatusFresh(live: DriverLiveStatus | null | undefined, now = Date.now()) {
  if (!live?.last_seen_at) return false;
  return now - new Date(live.last_seen_at).getTime() < LIVE_STATUS_FRESH_MS;
}

export function getDriverPresence(live: DriverLiveStatus | null | undefined, now = Date.now()) {
  const fresh = isLiveStatusFresh(live, now);

  return {
    fresh,
    online: Boolean(live?.is_app_online && fresh),
    monitoring: Boolean(live?.is_monitoring && fresh),
    label: !fresh || !live?.is_app_online
      ? "Offline"
      : live.is_monitoring
        ? "Đang giám sát"
        : "Đã đăng nhập app",
  };
}
