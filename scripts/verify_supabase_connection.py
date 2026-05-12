"""Basic Supabase connectivity verifier for the desktop app."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.shared.config.settings import load_settings
from app.shared.database.supabase_service import SupabaseService


def main() -> int:
    settings = load_settings()
    print("Checking Supabase configuration...")

    if not settings.supabase_url or not settings.supabase_anon_key:
        print("Missing SUPABASE_URL or SUPABASE_ANON_KEY in .env")
        return 1

    service = SupabaseService(settings)
    try:
        client = service.get_client()
    except Exception as exc:
        print(f"Failed to create Supabase client: {exc}")
        return 1

    if client is None:
        print("Supabase client is not configured.")
        return 1

    print("Supabase client initialized.")

    test_email = _read_env_value(ROOT_DIR / ".env", "SUPABASE_TEST_EMAIL")
    test_password = _read_env_value(ROOT_DIR / ".env", "SUPABASE_TEST_PASSWORD")

    if not test_email or not test_password:
        print("No SUPABASE_TEST_EMAIL / SUPABASE_TEST_PASSWORD set. Basic config looks OK.")
        return 0

    try:
        response = client.auth.sign_in_with_password(
            {"email": test_email, "password": test_password}
        )
        user = response.user
        if user is None:
            print("Sign-in test failed: no user returned.")
            return 1

        print(f"Sign-in test OK: {user.email}")

        settings_response = (
            client.table("user_settings")
            .select("*")
            .eq("user_id", user.id)
            .limit(1)
            .execute()
        )
        count = len(settings_response.data or [])
        print(f"user_settings rows found for test user: {count}")
        client.auth.sign_out()
        return 0
    except Exception as exc:
        print(f"Supabase sign-in/query test failed: {exc}")
        return 1


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
