"""Driver live presence updates for web admin realtime views."""

from __future__ import annotations

import logging
from typing import Optional

from app.shared.database.supabase_service import SupabaseService
from app.shared.utils.datetime_helper import utc_now


LOGGER = logging.getLogger(__name__)


class LiveStatusService:
    def __init__(self, supabase_service: SupabaseService) -> None:
        self.supabase_service = supabase_service

    def mark_online(
        self,
        *,
        driver_id: str,
        company_id: Optional[str] = None,
        vehicle_id: Optional[str] = None,
    ) -> None:
        self._upsert(
            driver_id=driver_id,
            company_id=company_id,
            vehicle_id=vehicle_id,
            is_app_online=True,
            is_monitoring=False,
            status="online",
            risk_level="low",
            session_id=None,
        )

    def mark_monitoring(
        self,
        *,
        driver_id: str,
        session_id: str,
        company_id: Optional[str] = None,
        vehicle_id: Optional[str] = None,
    ) -> None:
        self._upsert(
            driver_id=driver_id,
            session_id=session_id,
            company_id=company_id,
            vehicle_id=vehicle_id,
            is_app_online=True,
            is_monitoring=True,
            status="normal",
            risk_level="low",
        )

    def update_metrics(
        self,
        *,
        driver_id: str,
        session_id: Optional[str],
        company_id: Optional[str],
        vehicle_id: Optional[str],
        status: str,
        risk_level: str,
        ear_value: Optional[float] = None,
        mar_value: Optional[float] = None,
        head_yaw: Optional[float] = None,
        head_pitch: Optional[float] = None,
    ) -> None:
        self._upsert(
            driver_id=driver_id,
            session_id=session_id,
            company_id=company_id,
            vehicle_id=vehicle_id,
            is_app_online=True,
            is_monitoring=bool(session_id),
            status=status,
            risk_level=risk_level,
            ear_value=ear_value,
            mar_value=mar_value,
            head_yaw=head_yaw,
            head_pitch=head_pitch,
        )

    def mark_idle(
        self,
        *,
        driver_id: str,
        company_id: Optional[str] = None,
        vehicle_id: Optional[str] = None,
    ) -> None:
        self._upsert(
            driver_id=driver_id,
            session_id=None,
            company_id=company_id,
            vehicle_id=vehicle_id,
            is_app_online=True,
            is_monitoring=False,
            status="online",
            risk_level="low",
        )

    def mark_offline(self, *, driver_id: str) -> None:
        self._upsert(
            driver_id=driver_id,
            session_id=None,
            is_app_online=False,
            is_monitoring=False,
            status="offline",
            risk_level="low",
        )

    def _upsert(self, **payload) -> None:
        if not self.supabase_service.is_configured():
            return

        now = utc_now().isoformat()
        payload.setdefault("last_seen_at", now)
        payload["updated_at"] = now

        try:
            client = self.supabase_service.get_client()
            client.table("driver_live_status").upsert(payload, on_conflict="driver_id").execute()
        except Exception:
            LOGGER.exception("Failed to update driver live status")
