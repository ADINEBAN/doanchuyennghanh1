-- =============================================================================
-- DROWSINESS MONITORING SYSTEM — SUPABASE POSTGRESQL SCHEMA
-- =============================================================================
-- Version: 2.0
-- Hỗ trợ 3 vai trò: SUPER_ADMIN, COMPANY_ADMIN, DRIVER
-- Bao gồm: companies, vehicles, profiles, monitoring_sessions, alerts,
--           user_settings, ai_models, system_settings
-- =============================================================================

-- Bật extension uuid nếu chưa có
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. BẢNG COMPANIES — Hãng xe dịch vụ
-- =============================================================================
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    address TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    logo_url TEXT DEFAULT '',
    description TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'locked')),
    created_by UUID,  -- sẽ references profiles(id) sau khi tạo profiles
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index cho tìm kiếm nhanh
CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);

-- =============================================================================
-- 2. BẢNG PROFILES — Thông tin người dùng (mở rộng từ Supabase Auth)
-- =============================================================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    username TEXT DEFAULT '',
    full_name TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    avatar_url TEXT DEFAULT '',
    role TEXT NOT NULL DEFAULT 'DRIVER'
        CHECK (role IN ('SUPER_ADMIN', 'COMPANY_ADMIN', 'DRIVER')),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'locked')),
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_company ON profiles(company_id);
CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles(status);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);

-- Thêm FK cho companies.created_by sau khi profiles đã tồn tại
ALTER TABLE companies
    ADD CONSTRAINT fk_companies_created_by
    FOREIGN KEY (created_by) REFERENCES profiles(id) ON DELETE SET NULL;

-- =============================================================================
-- 3. BẢNG VEHICLES — Xe thuộc hãng
-- =============================================================================
CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    license_plate TEXT NOT NULL,
    brand TEXT DEFAULT '',
    model TEXT DEFAULT '',
    color TEXT DEFAULT '',
    year INT,
    vin_number TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'available'
        CHECK (status IN ('available', 'assigned', 'maintenance', 'inactive')),
    assigned_driver_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_vehicles_company ON vehicles(company_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_driver ON vehicles(assigned_driver_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_vehicles_plate_unique ON vehicles(license_plate);

-- =============================================================================
-- 4. BẢNG USER_SETTINGS — Cài đặt ngưỡng cảnh báo cho từng user
-- =============================================================================
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    ear_threshold FLOAT NOT NULL DEFAULT 0.23,
    ear_consec_frames INT NOT NULL DEFAULT 20,
    mar_threshold FLOAT NOT NULL DEFAULT 0.65,
    yawn_consec_frames INT NOT NULL DEFAULT 15,
    ai_prediction_interval INT NOT NULL DEFAULT 5,
    drowsy_alert_seconds INT NOT NULL DEFAULT 2,
    head_yaw_threshold FLOAT NOT NULL DEFAULT 30.0,
    head_pitch_threshold FLOAT NOT NULL DEFAULT 25.0,
    distraction_seconds INT NOT NULL DEFAULT 3,
    face_not_detected_seconds INT NOT NULL DEFAULT 5,
    selected_model_name TEXT DEFAULT '',
    alert_sound_enabled BOOLEAN NOT NULL DEFAULT true,
    alert_sound_path TEXT DEFAULT 'assets/sounds/alert.wav',
    camera_index INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id)
);

-- =============================================================================
-- 5. BẢNG MONITORING_SESSIONS — Phiên giám sát
-- =============================================================================
CREATE TABLE IF NOT EXISTS monitoring_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'running'
        CHECK (status IN ('running', 'stopped', 'interrupted')),
    duration_seconds INT DEFAULT 0,
    total_alerts INT DEFAULT 0,
    closed_eyes_count INT DEFAULT 0,
    yawning_count INT DEFAULT 0,
    drowsy_count INT DEFAULT 0,
    distraction_count INT DEFAULT 0,
    face_not_detected_count INT DEFAULT 0,
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sessions_user ON monitoring_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_company ON monitoring_sessions(company_id);
CREATE INDEX IF NOT EXISTS idx_sessions_vehicle ON monitoring_sessions(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON monitoring_sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON monitoring_sessions(started_at DESC);

-- =============================================================================
-- 6. BẢNG ALERTS — Cảnh báo
-- =============================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES monitoring_sessions(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    alert_type TEXT NOT NULL
        CHECK (alert_type IN (
            'closed_eyes', 'yawning', 'drowsy', 'distracted', 'face_not_detected'
        )),
    risk_level TEXT NOT NULL DEFAULT 'low'
        CHECK (risk_level IN ('low', 'medium', 'high', 'danger')),
    status_label TEXT NOT NULL DEFAULT 'normal',
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ear_value FLOAT,
    mar_value FLOAT,
    ai_label TEXT,
    ai_confidence FLOAT,
    head_yaw FLOAT,
    head_pitch FLOAT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_session ON alerts(session_id);
CREATE INDEX IF NOT EXISTS idx_alerts_company ON alerts(company_id);
CREATE INDEX IF NOT EXISTS idx_alerts_vehicle ON alerts(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_risk ON alerts(risk_level);
CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alerts(triggered_at DESC);

-- =============================================================================
-- 7. BẢNG AI_MODELS — Quản lý model AI
-- =============================================================================
CREATE TABLE IF NOT EXISTS ai_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    version TEXT DEFAULT '1.0',
    file_path TEXT NOT NULL,
    file_format TEXT NOT NULL DEFAULT 'keras'
        CHECK (file_format IN ('h5', 'keras', 'pt', 'onnx', 'tflite')),
    description TEXT DEFAULT '',
    accuracy FLOAT,
    precision_score FLOAT,
    recall_score FLOAT,
    f1_score FLOAT,
    num_classes INT DEFAULT 4,
    class_labels TEXT DEFAULT 'normal,closed_eyes,yawning,drowsy',
    is_default BOOLEAN DEFAULT false,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'testing')),
    created_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- 8. BẢNG SYSTEM_SETTINGS — Cấu hình hệ thống (SUPER_ADMIN quản lý)
-- =============================================================================
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    data_type TEXT DEFAULT 'string'
        CHECK (data_type IN ('string', 'int', 'float', 'boolean', 'json')),
    description TEXT DEFAULT '',
    updated_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- 9. TRIGGERS — Tự động tạo profile + settings khi user đăng ký
-- =============================================================================

-- Trigger function: tạo profile khi có user mới trong auth.users
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, username, full_name, role, status)
    VALUES (
        NEW.id,
        COALESCE(NEW.email, ''),
        COALESCE(
            NEW.raw_user_meta_data ->> 'username',
            SPLIT_PART(COALESCE(NEW.email, ''), '@', 1)
        ),
        COALESCE(NEW.raw_user_meta_data ->> 'full_name', ''),
        COALESCE(NEW.raw_user_meta_data ->> 'role', 'DRIVER'),
        'active'
    );

    INSERT INTO public.user_settings (user_id)
    VALUES (NEW.id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Xóa trigger cũ nếu có
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Tạo trigger mới
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();

-- Trigger function: cập nhật updated_at tự động
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Áp dụng trigger updated_at cho các bảng cần thiết
DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_vehicles_updated_at ON vehicles;
CREATE TRIGGER update_vehicles_updated_at
    BEFORE UPDATE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_settings_updated_at ON user_settings;
CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_ai_models_updated_at ON ai_models;
CREATE TRIGGER update_ai_models_updated_at
    BEFORE UPDATE ON ai_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 10. ROW LEVEL SECURITY (RLS) — Bảo mật theo vai trò
-- =============================================================================

-- Bật RLS trên tất cả bảng
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE monitoring_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- ---- Helper function: lấy role của user hiện tại ----
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS TEXT AS $$
    SELECT role FROM public.profiles WHERE id = auth.uid();
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- ---- Helper function: lấy company_id của user hiện tại ----
CREATE OR REPLACE FUNCTION get_user_company_id()
RETURNS UUID AS $$
    SELECT company_id FROM public.profiles WHERE id = auth.uid();
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- ---------------------------------------------------------------------------
-- PROFILES policies
-- ---------------------------------------------------------------------------
-- SUPER_ADMIN: đọc/sửa tất cả profiles
CREATE POLICY "super_admin_all_profiles"
    ON profiles FOR ALL TO authenticated
    USING (get_user_role() = 'SUPER_ADMIN')
    WITH CHECK (get_user_role() = 'SUPER_ADMIN');

-- COMPANY_ADMIN: đọc profiles cùng công ty + chính mình
CREATE POLICY "company_admin_read_profiles"
    ON profiles FOR SELECT TO authenticated
    USING (
        get_user_role() = 'COMPANY_ADMIN'
        AND (
            company_id = get_user_company_id()
            OR id = auth.uid()
        )
    );

-- COMPANY_ADMIN: sửa profiles tài xế cùng công ty
CREATE POLICY "company_admin_update_profiles"
    ON profiles FOR UPDATE TO authenticated
    USING (
        get_user_role() = 'COMPANY_ADMIN'
        AND company_id = get_user_company_id()
        AND role = 'DRIVER'
    )
    WITH CHECK (
        get_user_role() = 'COMPANY_ADMIN'
        AND company_id = get_user_company_id()
        AND role = 'DRIVER'
    );

-- DRIVER: chỉ đọc profile chính mình
CREATE POLICY "driver_read_own_profile"
    ON profiles FOR SELECT TO authenticated
    USING (id = auth.uid() AND get_user_role() = 'DRIVER');

-- DRIVER: sửa profile chính mình (chỉ thông tin cá nhân)
CREATE POLICY "driver_update_own_profile"
    ON profiles FOR UPDATE TO authenticated
    USING (id = auth.uid() AND get_user_role() = 'DRIVER')
    WITH CHECK (id = auth.uid() AND get_user_role() = 'DRIVER');

-- ---------------------------------------------------------------------------
-- COMPANIES policies
-- ---------------------------------------------------------------------------
-- SUPER_ADMIN: full access companies
CREATE POLICY "super_admin_all_companies"
    ON companies FOR ALL TO authenticated
    USING (get_user_role() = 'SUPER_ADMIN')
    WITH CHECK (get_user_role() = 'SUPER_ADMIN');

-- COMPANY_ADMIN: đọc công ty của mình
CREATE POLICY "company_admin_read_own_company"
    ON companies FOR SELECT TO authenticated
    USING (
        get_user_role() = 'COMPANY_ADMIN'
        AND id = get_user_company_id()
    );

-- COMPANY_ADMIN: sửa thông tin công ty mình
CREATE POLICY "company_admin_update_own_company"
    ON companies FOR UPDATE TO authenticated
    USING (
        get_user_role() = 'COMPANY_ADMIN'
        AND id = get_user_company_id()
    )
    WITH CHECK (
        get_user_role() = 'COMPANY_ADMIN'
        AND id = get_user_company_id()
    );

-- DRIVER: đọc công ty mình thuộc về
CREATE POLICY "driver_read_own_company"
    ON companies FOR SELECT TO authenticated
    USING (
        get_user_role() = 'DRIVER'
        AND id = get_user_company_id()
    );

-- ---------------------------------------------------------------------------
-- VEHICLES policies
-- ---------------------------------------------------------------------------
-- SUPER_ADMIN: full access vehicles
CREATE POLICY "super_admin_all_vehicles"
    ON vehicles FOR ALL TO authenticated
    USING (get_user_role() = 'SUPER_ADMIN')
    WITH CHECK (get_user_role() = 'SUPER_ADMIN');

-- COMPANY_ADMIN: CRUD xe thuộc công ty mình
CREATE POLICY "company_admin_all_vehicles"
    ON vehicles FOR ALL TO authenticated
    USING (
        get_user_role() = 'COMPANY_ADMIN'
        AND company_id = get_user_company_id()
    )
    WITH CHECK (
        get_user_role() = 'COMPANY_ADMIN'
        AND company_id = get_user_company_id()
    );

-- DRIVER: chỉ đọc xe được gán cho mình
CREATE POLICY "driver_read_assigned_vehicle"
    ON vehicles FOR SELECT TO authenticated
    USING (
        get_user_role() = 'DRIVER'
        AND assigned_driver_id = auth.uid()
    );

-- ---------------------------------------------------------------------------
-- USER_SETTINGS policies
-- ---------------------------------------------------------------------------
-- SUPER_ADMIN: đọc tất cả settings
CREATE POLICY "super_admin_all_settings"
    ON user_settings FOR ALL TO authenticated
    USING (get_user_role() = 'SUPER_ADMIN')
    WITH CHECK (get_user_role() = 'SUPER_ADMIN');

-- Mọi user: đọc/sửa settings của chính mình
CREATE POLICY "user_own_settings"
    ON user_settings FOR ALL TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- ---------------------------------------------------------------------------
-- MONITORING_SESSIONS policies
-- ---------------------------------------------------------------------------
-- SUPER_ADMIN: đọc tất cả sessions
CREATE POLICY "super_admin_all_sessions"
    ON monitoring_sessions FOR ALL TO authenticated
    USING (get_user_role() = 'SUPER_ADMIN')
    WITH CHECK (get_user_role() = 'SUPER_ADMIN');

-- COMPANY_ADMIN: đọc sessions thuộc công ty mình
CREATE POLICY "company_admin_read_sessions"
    ON monitoring_sessions FOR SELECT TO authenticated
    USING (
        get_user_role() = 'COMPANY_ADMIN'
        AND company_id = get_user_company_id()
    );

-- DRIVER: đọc/ghi sessions của chính mình
CREATE POLICY "driver_own_sessions"
    ON monitoring_sessions FOR ALL TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- ---------------------------------------------------------------------------
-- ALERTS policies
-- ---------------------------------------------------------------------------
-- SUPER_ADMIN: đọc tất cả alerts
CREATE POLICY "super_admin_all_alerts"
    ON alerts FOR ALL TO authenticated
    USING (get_user_role() = 'SUPER_ADMIN')
    WITH CHECK (get_user_role() = 'SUPER_ADMIN');

-- COMPANY_ADMIN: đọc alerts thuộc công ty mình
CREATE POLICY "company_admin_read_alerts"
    ON alerts FOR SELECT TO authenticated
    USING (
        get_user_role() = 'COMPANY_ADMIN'
        AND company_id = get_user_company_id()
    );

-- DRIVER: đọc/ghi alerts của chính mình
CREATE POLICY "driver_own_alerts"
    ON alerts FOR ALL TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- ---------------------------------------------------------------------------
-- AI_MODELS policies
-- ---------------------------------------------------------------------------
-- SUPER_ADMIN: full access AI models
CREATE POLICY "super_admin_all_ai_models"
    ON ai_models FOR ALL TO authenticated
    USING (get_user_role() = 'SUPER_ADMIN')
    WITH CHECK (get_user_role() = 'SUPER_ADMIN');

-- Các role khác: chỉ đọc model active
CREATE POLICY "read_active_ai_models"
    ON ai_models FOR SELECT TO authenticated
    USING (status = 'active');

-- ---------------------------------------------------------------------------
-- SYSTEM_SETTINGS policies
-- ---------------------------------------------------------------------------
-- SUPER_ADMIN: full access system settings
CREATE POLICY "super_admin_all_system_settings"
    ON system_settings FOR ALL TO authenticated
    USING (get_user_role() = 'SUPER_ADMIN')
    WITH CHECK (get_user_role() = 'SUPER_ADMIN');

-- Các role khác: chỉ đọc
CREATE POLICY "read_system_settings"
    ON system_settings FOR SELECT TO authenticated
    USING (true);

-- =============================================================================
-- 11. VIEWS — Tiện ích cho thống kê
-- =============================================================================

-- View: thống kê tổng quan cho SUPER_ADMIN
CREATE OR REPLACE VIEW system_overview AS
SELECT
    (SELECT COUNT(*) FROM companies WHERE status = 'active') AS active_companies,
    (SELECT COUNT(*) FROM profiles WHERE role = 'COMPANY_ADMIN' AND status = 'active') AS active_company_admins,
    (SELECT COUNT(*) FROM profiles WHERE role = 'DRIVER' AND status = 'active') AS active_drivers,
    (SELECT COUNT(*) FROM vehicles WHERE status IN ('available', 'assigned')) AS total_vehicles,
    (SELECT COUNT(*) FROM monitoring_sessions) AS total_sessions,
    (SELECT COUNT(*) FROM monitoring_sessions WHERE status = 'running') AS active_sessions,
    (SELECT COUNT(*) FROM alerts) AS total_alerts,
    (SELECT COUNT(*) FROM alerts WHERE triggered_at >= CURRENT_DATE) AS alerts_today;

-- View: thống kê cảnh báo theo ngày (30 ngày gần nhất)
CREATE OR REPLACE VIEW daily_alert_stats AS
SELECT
    DATE(triggered_at) AS alert_date,
    company_id,
    alert_type,
    risk_level,
    COUNT(*) AS alert_count
FROM alerts
WHERE triggered_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(triggered_at), company_id, alert_type, risk_level
ORDER BY alert_date DESC;

-- =============================================================================
-- 12. SEED DATA — Dữ liệu ngưỡng mặc định
-- =============================================================================

-- Cấu hình ngưỡng mặc định cho hệ thống
INSERT INTO system_settings (key, value, data_type, description) VALUES
    ('default_ear_threshold', '0.23', 'float', 'Nguong EAR mac dinh de phat hien mat nham'),
    ('default_ear_consec_frames', '20', 'int', 'So frame lien tiep mat nham de canh bao'),
    ('default_mar_threshold', '0.65', 'float', 'Nguong MAR mac dinh de phat hien ngap'),
    ('default_yawn_consec_frames', '15', 'int', 'So frame lien tiep ngap de canh bao'),
    ('default_ai_prediction_interval', '5', 'int', 'So frame giua moi lan predict AI'),
    ('default_drowsy_alert_seconds', '2', 'int', 'So giay drowsy lien tuc de canh bao muc cao'),
    ('head_yaw_threshold', '30.0', 'float', 'Nguong goc quay mat ngang (do) de phat hien mat tap trung'),
    ('head_pitch_threshold', '25.0', 'float', 'Nguong goc cui/ngua mat (do) de phat hien mat tap trung'),
    ('distraction_seconds', '3', 'int', 'So giay quay mat lien tuc de canh bao mat tap trung'),
    ('face_not_detected_seconds', '5', 'int', 'So giay khong tim thay khuon mat de canh bao')
ON CONFLICT (key) DO NOTHING;

-- =============================================================================
-- GHI CHÚ
-- =============================================================================
-- 1. Sau khi chạy schema này trên Supabase SQL Editor, cần tạo user
--    SUPER_ADMIN đầu tiên bằng cách:
--    a) Tạo user trong Supabase Auth (Authentication > Users > Add User)
--    b) Cập nhật role trong profiles:
--       UPDATE profiles SET role = 'SUPER_ADMIN' WHERE email = 'your@email.com';
--
-- 2. COMPANY_ADMIN được tạo bởi SUPER_ADMIN thông qua Web Admin.
--    Flow: SUPER_ADMIN tạo company → tạo user qua Supabase Admin API →
--          update profile.role = 'COMPANY_ADMIN', profile.company_id = <company_id>
--
-- 3. DRIVER được tạo bởi COMPANY_ADMIN thông qua Web Admin.
--    Flow: COMPANY_ADMIN tạo user qua Supabase Admin API →
--          update profile.role = 'DRIVER', profile.company_id = <company_id>
--
-- 4. Để tạo user bằng Supabase Admin API (server-side), cần sử dụng
--    SUPABASE_SERVICE_ROLE_KEY thay vì ANON_KEY.
--    Key này KHÔNG được đưa vào desktop app, chỉ dùng trong Web Admin backend
--    hoặc Supabase Edge Function.
-- =============================================================================
