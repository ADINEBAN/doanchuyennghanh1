"""Alert persistence and summary service."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.shared.core.app_state import AlertEvent
from app.shared.database.supabase_service import SupabaseService
from app.shared.utils.datetime_helper import utc_now


class AlertService:
    def __init__(self, supabase_service: SupabaseService) -> None:
        self.supabase_service = supabase_service
        self._local_alerts: dict[str, list[AlertEvent]] = {}

    def create_alert(
        self,
        *,
        user_id: str,
        session_id: str,
        alert_type: str,
        risk_level: str,
        status_label: str,
        company_id: Optional[str] = None,
        vehicle_id: Optional[str] = None,
        ear_value: Optional[float] = None,
        mar_value: Optional[float] = None,
        ai_label: Optional[str] = None,
        ai_confidence: Optional[float] = None,
        head_yaw: Optional[float] = None,
        head_pitch: Optional[float] = None,
    ) -> AlertEvent:
        alert = AlertEvent(
            id=str(uuid4()),
            user_id=user_id,
            session_id=session_id,
            alert_type=alert_type,
            risk_level=risk_level,
            status_label=status_label,
            triggered_at=utc_now(),
            company_id=company_id,
            vehicle_id=vehicle_id,
            ear_value=ear_value,
            mar_value=mar_value,
            ai_label=ai_label,
            ai_confidence=ai_confidence,
            head_yaw=head_yaw,
            head_pitch=head_pitch,
        )

        if not self.supabase_service.is_configured():
            self._local_alerts.setdefault(user_id, []).append(alert)
            return alert

        client = self.supabase_service.get_client()
        payload: dict = {
            "id": alert.id,
            "user_id": user_id,
            "session_id": session_id,
            "alert_type": alert_type,
            "risk_level": risk_level,
            "status_label": status_label,
            "triggered_at": alert.triggered_at.isoformat(),
            "ear_value": ear_value,
            "mar_value": mar_value,
            "ai_label": ai_label,
            "ai_confidence": ai_confidence,
            "head_yaw": head_yaw,
            "head_pitch": head_pitch,
        }
        if company_id:
            payload["company_id"] = company_id
        if vehicle_id:
            payload["vehicle_id"] = vehicle_id

        client.table("alerts").insert(payload).execute()
        return alert

    def list_alerts_for_user(self, user_id: str) -> list[AlertEvent]:
        if not self.supabase_service.is_configured():
            return sorted(
                self._local_alerts.get(user_id, []),
                key=lambda alert: alert.triggered_at,
                reverse=True,
            )

        client = self.supabase_service.get_client()
        rows = (
            client.table("alerts")
            .select("*")
            .eq("user_id", user_id)
            .order("triggered_at", desc=True)
            .execute()
        )
        return [self._row_to_alert(row) for row in (rows.data or [])]

    def list_alerts_for_session(self, session_id: str) -> list[AlertEvent]:
        if not self.supabase_service.is_configured():
            session_alerts: list[AlertEvent] = []
            for alerts in self._local_alerts.values():
                session_alerts.extend(
                    alert for alert in alerts if alert.session_id == session_id
                )
            return sorted(session_alerts, key=lambda alert: alert.triggered_at, reverse=True)

        client = self.supabase_service.get_client()
        rows = (
            client.table("alerts")
            .select("*")
            .eq("session_id", session_id)
            .order("triggered_at", desc=True)
            .execute()
        )
        return [self._row_to_alert(row) for row in (rows.data or [])]

    def get_alert_summary(self, user_id: str) -> dict[str, object]:
        alerts = self.list_alerts_for_user(user_id)
        return self.summarize_alerts(alerts)

    def summarize_alerts(self, alerts: list[AlertEvent]) -> dict[str, object]:
        type_counter = Counter(alert.alert_type for alert in alerts)
        risk_counter = Counter(alert.risk_level for alert in alerts)
        by_day = defaultdict(int)

        for alert in alerts:
            by_day[alert.triggered_at.strftime("%Y-%m-%d")] += 1

        return {
            "total_alerts": len(alerts),
            "top_alert_type": type_counter.most_common(1)[0][0] if type_counter else "-",
            "alerts_by_day": dict(sorted(by_day.items())),
            "alerts_by_type": dict(type_counter),
            "alerts_by_risk": dict(risk_counter),
        }

    @staticmethod
    def _row_to_alert(row: dict) -> AlertEvent:
        return AlertEvent(
            id=row["id"],
            user_id=row["user_id"],
            session_id=row["session_id"],
            alert_type=row["alert_type"],
            risk_level=row["risk_level"],
            status_label=row["status_label"],
            triggered_at=_parse_datetime(row.get("triggered_at")),
            company_id=row.get("company_id"),
            vehicle_id=row.get("vehicle_id"),
            ear_value=row.get("ear_value"),
            mar_value=row.get("mar_value"),
            ai_label=row.get("ai_label"),
            ai_confidence=row.get("ai_confidence"),
            head_yaw=row.get("head_yaw"),
            head_pitch=row.get("head_pitch"),
        )


def _parse_datetime(value: Optional[str]):
    if not value:
        return utc_now()
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
