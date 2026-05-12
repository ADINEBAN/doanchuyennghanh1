"""Supabase client wrapper with lazy initialization."""

from __future__ import annotations

from typing import Any, Optional

from app.shared.config.settings import AppSettings


class SupabaseService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self._client: Any = None

    def is_configured(self) -> bool:
        return self.settings.supabase_enabled

    def get_client(self) -> Optional[Any]:
        if not self.is_configured():
            return None

        if self._client is not None:
            return self._client

        from supabase import create_client

        self._client = create_client(
            self.settings.supabase_url,
            self.settings.supabase_anon_key,
        )
        return self._client
