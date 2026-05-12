from app.features.auth.service import AuthService
from app.features.settings.service import SettingsService
from app.shared.config.settings import AppSettings
from app.shared.database.supabase_service import SupabaseService


def test_local_auth_and_settings_flow():
    app_settings = AppSettings()
    supabase_service = SupabaseService(app_settings)
    auth_service = AuthService(supabase_service)
    settings_service = SettingsService(supabase_service, app_settings)

    user = auth_service.register_user("Demo User", "demo@example.com", "secret123")
    logged_in = auth_service.sign_in("demo@example.com", "secret123")
    settings_state = settings_service.get_settings(user.id)

    assert logged_in.email == "demo@example.com"
    assert settings_state.user_id == user.id
