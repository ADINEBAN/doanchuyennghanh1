"""Smoke test the Supabase monitoring flow with the configured test user."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.features.auth.service import AuthService
from app.features.monitoring.alert_service import AlertService
from app.features.monitoring.session_service import SessionService
from app.shared.config.constants import RISK_MEDIUM, STATUS_DISTRACTED
from app.shared.config.settings import load_settings
from app.shared.database.supabase_service import SupabaseService


def main() -> int:
    settings = load_settings()
    test_email = _read_env_value(ROOT_DIR / ".env", "SUPABASE_TEST_EMAIL")
    test_password = _read_env_value(ROOT_DIR / ".env", "SUPABASE_TEST_PASSWORD")

    if not settings.supabase_enabled:
        print("Missing SUPABASE_URL or SUPABASE_ANON_KEY in .env")
        return 1
    if not test_email or not test_password:
        print("Missing SUPABASE_TEST_EMAIL or SUPABASE_TEST_PASSWORD in .env")
        return 1

    supabase_service = SupabaseService(settings)
    auth_service = AuthService(supabase_service)
    session_service = SessionService(supabase_service)
    alert_service = AlertService(supabase_service)

    print("Signing in test driver...")
    user = auth_service.sign_in(test_email, test_password)
    company = auth_service.fetch_company(user.company_id)
    vehicle = auth_service.fetch_assigned_vehicle(user.id)
    company_id = company.id if company else None
    vehicle_id = vehicle.id if vehicle else None
    print(f"Signed in: {user.email} ({user.id})")

    print("Creating monitoring session...")
    session = session_service.start_session(
        user.id,
        company_id=company_id,
        vehicle_id=vehicle_id,
    )
    print(f"Session created: {session.id}")

    print("Creating synthetic distracted alert...")
    alert = alert_service.create_alert(
        user_id=user.id,
        session_id=session.id,
        company_id=company_id,
        vehicle_id=vehicle_id,
        alert_type=STATUS_DISTRACTED,
        risk_level=RISK_MEDIUM,
        status_label=STATUS_DISTRACTED,
        ear_value=0.31,
        mar_value=0.22,
        head_yaw=36.0,
        head_pitch=3.0,
    )

    session_alerts = alert_service.list_alerts_for_session(session.id)
    stored_alert = next((item for item in session_alerts if item.id == alert.id), None)
    if stored_alert is None:
        print(
            "Alert was not found after insert. Run "
            "db/migrations/20260512_fix_alert_type_constraint.sql in Supabase SQL Editor."
        )
        return 1
    print(f"Alert stored: {stored_alert.id} type={stored_alert.alert_type}")

    print("Stopping monitoring session...")
    summary = alert_service.summarize_alerts(session_alerts)
    type_counts = summary.get("alerts_by_type", {})
    session_service.stop_session(
        session,
        total_alerts=len(session_alerts),
        closed_eyes_count=int(type_counts.get("closed_eyes", 0)),
        yawning_count=int(type_counts.get("yawning", 0)),
        drowsy_count=int(type_counts.get("drowsy", 0)),
        distraction_count=int(type_counts.get("distracted", 0)),
        face_not_detected_count=int(type_counts.get("face_not_detected", 0)),
    )

    client = supabase_service.get_client()
    session_rows = (
        client.table("monitoring_sessions")
        .select("*")
        .eq("id", session.id)
        .limit(1)
        .execute()
        .data
        or []
    )
    if not session_rows:
        print("Session row was not found after stop.")
        return 1

    session_row = session_rows[0]
    if session_row.get("status") != "stopped" or not session_row.get("ended_at"):
        print(f"Session stop update failed: {session_row}")
        return 1

    user_alerts = alert_service.list_alerts_for_user(user.id)
    user_summary = alert_service.get_alert_summary(user.id)
    if not any(item.id == alert.id for item in user_alerts):
        print("History query did not return the synthetic alert.")
        return 1
    if int(user_summary.get("total_alerts", 0)) < 1:
        print("Statistics summary did not count alerts.")
        return 1

    print(
        "Smoke test OK: alert stored, session stopped, "
        "history and statistics queries returned data."
    )
    auth_service.sign_out()
    return 0


def _read_env_value(env_path: Path, key: str) -> str:
    if not env_path.exists():
        return ""

    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip()
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
