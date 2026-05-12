"""Monitoring session persistence service."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.shared.core.app_state import MonitoringSessionState
from app.shared.database.supabase_service import SupabaseService
from app.shared.utils.datetime_helper import utc_now


class SessionService:
    def __init__(self, supabase_service: SupabaseService) -> None:
        self.supabase_service = supabase_service
        self._local_sessions: dict[str, list[MonitoringSessionState]] = {}

    def start_session(
        self,
        user_id: str,
        *,
        company_id: Optional[str] = None,
        vehicle_id: Optional[str] = None,
    ) -> MonitoringSessionState:
        session = MonitoringSessionState(
            id=str(uuid4()),
            user_id=user_id,
            started_at=utc_now(),
            company_id=company_id,
            vehicle_id=vehicle_id,
        )

        if not self.supabase_service.is_configured():
            self._local_sessions.setdefault(user_id, []).append(session)
            return session

        client = self.supabase_service.get_client()
        payload: dict = {
            "id": session.id,
            "user_id": user_id,
            "status": session.status,
            "started_at": session.started_at.isoformat(),
        }
        if company_id:
            payload["company_id"] = company_id
        if vehicle_id:
            payload["vehicle_id"] = vehicle_id

        client.table("monitoring_sessions").insert(payload).execute()
        return session

    def stop_session(
        self,
        session: MonitoringSessionState,
        *,
        total_alerts: int = 0,
        closed_eyes_count: int = 0,
        yawning_count: int = 0,
        drowsy_count: int = 0,
        distraction_count: int = 0,
        face_not_detected_count: int = 0,
    ) -> MonitoringSessionState:
        session.ended_at = utc_now()
        session.status = "stopped"
        session.total_alerts = total_alerts
        session.closed_eyes_count = closed_eyes_count
        session.yawning_count = yawning_count
        session.drowsy_count = drowsy_count
        session.distraction_count = distraction_count
        session.face_not_detected_count = face_not_detected_count

        if not self.supabase_service.is_configured():
            return session

        duration = int((session.ended_at - session.started_at).total_seconds())
        client = self.supabase_service.get_client()
        client.table("monitoring_sessions").update(
            {
                "ended_at": session.ended_at.isoformat(),
                "duration_seconds": duration,
                "status": session.status,
                "total_alerts": total_alerts,
                "closed_eyes_count": closed_eyes_count,
                "yawning_count": yawning_count,
                "drowsy_count": drowsy_count,
                "distraction_count": distraction_count,
                "face_not_detected_count": face_not_detected_count,
            }
        ).eq("id", session.id).execute()
        return session

    def list_sessions(self, user_id: str) -> list[MonitoringSessionState]:
        if not self.supabase_service.is_configured():
            return list(self._local_sessions.get(user_id, []))

        client = self.supabase_service.get_client()
        rows = (
            client.table("monitoring_sessions")
            .select("*")
            .eq("user_id", user_id)
            .order("started_at", desc=True)
            .execute()
        )
        sessions: list[MonitoringSessionState] = []
        for row in rows.data or []:
            sessions.append(
                MonitoringSessionState(
                    id=row["id"],
                    user_id=row["user_id"],
                    started_at=_parse_datetime(row.get("started_at")),
                    company_id=row.get("company_id"),
                    vehicle_id=row.get("vehicle_id"),
                    status=row.get("status", "stopped"),
                    total_alerts=row.get("total_alerts", 0),
                    closed_eyes_count=row.get("closed_eyes_count", 0),
                    yawning_count=row.get("yawning_count", 0),
                    drowsy_count=row.get("drowsy_count", 0),
                    distraction_count=row.get("distraction_count", 0),
                    face_not_detected_count=row.get("face_not_detected_count", 0),
                )
            )
        return sessions


def _parse_datetime(value: Optional[str]):
    if not value:
        return utc_now()
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
