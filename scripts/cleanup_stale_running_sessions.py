"""Mark stale running monitoring sessions as interrupted."""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.shared.config.settings import load_settings
from app.shared.database.supabase_service import SupabaseService
from app.shared.utils.datetime_helper import utc_now


def main() -> int:
    settings = load_settings()
    service = SupabaseService(settings)
    client = service.get_client()

    if client is None:
        print("Supabase is not configured.")
        return 1

    cutoff = utc_now() - timedelta(minutes=10)
    rows = (
        client.table("monitoring_sessions")
        .select("id,started_at,status")
        .eq("status", "running")
        .lt("started_at", cutoff.isoformat())
        .execute()
        .data
        or []
    )

    if not rows:
        print("No stale running sessions found.")
        return 0

    now = utc_now().isoformat()
    for row in rows:
        client.table("monitoring_sessions").update(
            {
                "status": "interrupted",
                "ended_at": now,
            }
        ).eq("id", row["id"]).execute()

    print(f"Marked {len(rows)} stale running sessions as interrupted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
