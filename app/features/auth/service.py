"""Authentication service with Supabase and local fallback mode."""

from __future__ import annotations

from dataclasses import asdict
from typing import Optional
from uuid import uuid4

from app.shared.config.constants import ROLE_DRIVER
from app.shared.core.app_state import CompanyInfo, UserProfile, VehicleInfo
from app.shared.core.exceptions import AuthenticationError
from app.shared.database.supabase_service import SupabaseService
from app.shared.utils.datetime_helper import utc_now


class AuthService:
    def __init__(self, supabase_service: SupabaseService) -> None:
        self.supabase_service = supabase_service
        self._local_users: dict[str, dict[str, str]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sign_in(self, email: str, password: str) -> UserProfile:
        if not email or not password:
            raise AuthenticationError("Email and password are required.")

        if not self.supabase_service.is_configured():
            return self._local_sign_in(email, password)

        client = self.supabase_service.get_client()
        try:
            response = client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
        except Exception as exc:
            raise AuthenticationError(self._map_auth_error(exc)) from exc

        auth_user = response.user
        if auth_user is None:
            raise AuthenticationError("Supabase sign-in failed.")

        profile = self._fetch_profile(auth_user.id, fallback_email=auth_user.email or email)

        # Desktop app chỉ cho phép DRIVER đăng nhập
        if profile.role != ROLE_DRIVER:
            self.sign_out()
            raise AuthenticationError(
                "Tai khoan nay khong phai DRIVER. "
                "Vui long dang nhap tren Web Admin."
            )

        if profile.status != "active":
            self.sign_out()
            raise AuthenticationError(
                "Tai khoan da bi khoa hoac vo hieu hoa. "
                "Vui long lien he quan tri vien."
            )

        self._touch_last_login(auth_user.id)
        return profile

    def sign_out(self) -> None:
        if not self.supabase_service.is_configured():
            return

        try:
            client = self.supabase_service.get_client()
            client.auth.sign_out()
        except Exception:
            pass

    def fetch_company(self, company_id: Optional[str]) -> Optional[CompanyInfo]:
        """Fetch company info for the logged-in driver."""
        if not company_id:
            return None

        if not self.supabase_service.is_configured():
            return CompanyInfo(id=company_id, name="Local Demo Company")

        client = self.supabase_service.get_client()
        response = (
            client.table("companies")
            .select("*")
            .eq("id", company_id)
            .limit(1)
            .execute()
        )
        row = (response.data or [None])[0]
        if row is None:
            return None

        return CompanyInfo(
            id=row["id"],
            name=row.get("name", ""),
            address=row.get("address", ""),
            phone=row.get("phone", ""),
            email=row.get("email", ""),
            logo_url=row.get("logo_url", ""),
            status=row.get("status", "active"),
        )

    def fetch_assigned_vehicle(self, driver_id: str) -> Optional[VehicleInfo]:
        """Fetch the vehicle currently assigned to this driver."""
        if not self.supabase_service.is_configured():
            return VehicleInfo(
                id=str(uuid4()),
                company_id="local",
                license_plate="LOCAL-0000",
                brand="Demo",
                model="Demo Vehicle",
            )

        client = self.supabase_service.get_client()
        response = (
            client.table("vehicles")
            .select("*")
            .eq("assigned_driver_id", driver_id)
            .eq("status", "assigned")
            .limit(1)
            .execute()
        )
        row = (response.data or [None])[0]
        if row is None:
            return None

        return VehicleInfo(
            id=row["id"],
            company_id=row.get("company_id", ""),
            license_plate=row.get("license_plate", ""),
            brand=row.get("brand", ""),
            model=row.get("model", ""),
            color=row.get("color", ""),
            year=row.get("year"),
            status=row.get("status", "assigned"),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _local_sign_in(self, email: str, password: str) -> UserProfile:
        """Fallback login for development without Supabase."""
        local_user = self._local_users.get(email)
        if local_user is None:
            # Auto-create a demo driver on first login
            demo_user = self._build_profile(
                id=str(uuid4()),
                email=email,
                username=self._default_username(email),
                full_name="Local Demo Driver",
                role=ROLE_DRIVER,
            )
            self._local_users[email] = {
                "password": password,
                **asdict(demo_user),
            }
            return demo_user

        if local_user["password"] != password:
            raise AuthenticationError("Invalid email or password.")

        return self._build_profile(
            id=local_user["id"],
            email=local_user["email"],
            username=local_user.get("username", self._default_username(email)),
            full_name=local_user.get("full_name", ""),
            phone=local_user.get("phone", ""),
            avatar_url=local_user.get("avatar_url", ""),
            role=local_user.get("role", ROLE_DRIVER),
            status=local_user.get("status", "active"),
            company_id=local_user.get("company_id"),
        )

    def _fetch_profile(self, user_id: str, fallback_email: str) -> UserProfile:
        client = self.supabase_service.get_client()
        response = (
            client.table("profiles")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        row = (response.data or [{}])[0]
        return self._build_profile(
            id=user_id,
            email=row.get("email", fallback_email),
            username=row.get("username", self._default_username(fallback_email)),
            full_name=row.get("full_name", ""),
            phone=row.get("phone", ""),
            avatar_url=row.get("avatar_url", ""),
            role=row.get("role", ROLE_DRIVER),
            status=row.get("status", "active"),
            company_id=row.get("company_id"),
        )

    def _touch_last_login(self, user_id: str) -> None:
        if not self.supabase_service.is_configured():
            return

        try:
            client = self.supabase_service.get_client()
            client.table("profiles").update(
                {"last_login_at": utc_now().isoformat()}
            ).eq("id", user_id).execute()
        except Exception:
            pass

    @staticmethod
    def _build_profile(
        *,
        id: str,
        email: str,
        username: str = "",
        full_name: str = "",
        phone: str = "",
        avatar_url: str = "",
        role: str = "DRIVER",
        status: str = "active",
        company_id: Optional[str] = None,
    ) -> UserProfile:
        return UserProfile(
            id=id,
            email=email,
            username=username,
            full_name=full_name,
            phone=phone,
            avatar_url=avatar_url,
            role=role,
            status=status,
            company_id=company_id,
        )

    @staticmethod
    def _default_username(email: str) -> str:
        local = email.split("@", 1)[0].strip().lower()
        cleaned = "".join(char for char in local if char.isalnum() or char == "_")
        return cleaned or "user"

    @staticmethod
    def _map_auth_error(exc: Exception) -> str:
        message = str(exc)
        lowered = message.lower()
        if "email not confirmed" in lowered:
            return "Email chua duoc xac nhan trong Supabase."
        if "invalid login credentials" in lowered:
            return "Sai email hoac mat khau."
        return message
