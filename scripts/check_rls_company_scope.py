"""Verify that COMPANY_ADMIN cannot read rows outside their company.

Usage:
    python scripts/check_rls_company_scope.py companyadmin@gmail.com 123456
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")
    load_dotenv(root / "web-admin" / ".env.local")


def _get_setting(name: str) -> str:
    import os

    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def _assert_company_scope(table: str, rows: list[dict], company_id: str) -> list[str]:
    leaks: list[str] = []
    for row in rows:
        row_company_id = row.get("company_id")
        if row_company_id and row_company_id != company_id:
            leaks.append(str(row.get("id") or row.get("driver_id") or row_company_id))
    if leaks:
        return [f"{table}: leaked {len(leaks)} row(s): {', '.join(leaks[:5])}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("email")
    parser.add_argument("password")
    args = parser.parse_args()

    _load_env()

    from supabase import create_client

    url = _get_setting("NEXT_PUBLIC_SUPABASE_URL")
    anon_key = _get_setting("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    client = create_client(url, anon_key)

    auth = client.auth.sign_in_with_password({"email": args.email, "password": args.password})
    user = auth.user
    if user is None:
        raise RuntimeError("Could not sign in as COMPANY_ADMIN")

    profile_rows = (
        client.table("profiles")
        .select("*")
        .eq("id", user.id)
        .limit(1)
        .execute()
        .data
        or []
    )
    if not profile_rows:
        raise RuntimeError("Profile not found")

    current_profile = profile_rows[0]
    if current_profile.get("role") != "COMPANY_ADMIN":
        raise RuntimeError(f"Expected COMPANY_ADMIN, got {current_profile.get('role')}")

    company_id = current_profile.get("company_id")
    if not company_id:
        raise RuntimeError("COMPANY_ADMIN has no company_id")

    checks: list[str] = []

    profiles = client.table("profiles").select("*").execute().data or []
    for row in profiles:
        if row.get("id") == user.id:
            continue
        if row.get("company_id") != company_id:
            checks.append(f"profiles: leaked profile {row.get('id')}")

    for table in ["vehicles", "monitoring_sessions", "alerts", "driver_live_status"]:
        rows = client.table(table).select("*").execute().data or []
        checks.extend(_assert_company_scope(table, rows, company_id))

    if checks:
        print("RLS CHECK FAILED")
        for item in checks:
            print(f"- {item}")
        return 1

    print("RLS CHECK PASSED")
    print(f"COMPANY_ADMIN can only read company_id={company_id}")
    print(f"Visible profiles: {len(profiles)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"RLS CHECK ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
