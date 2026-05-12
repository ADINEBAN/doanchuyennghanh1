-- Live driver presence for web admin realtime views.
-- Run this once in Supabase SQL Editor.

CREATE TABLE IF NOT EXISTS public.driver_live_status (
    driver_id UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
    session_id UUID REFERENCES public.monitoring_sessions(id) ON DELETE SET NULL,
    company_id UUID REFERENCES public.companies(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES public.vehicles(id) ON DELETE SET NULL,
    is_app_online BOOLEAN NOT NULL DEFAULT false,
    is_monitoring BOOLEAN NOT NULL DEFAULT false,
    status TEXT NOT NULL DEFAULT 'offline',
    risk_level TEXT NOT NULL DEFAULT 'low',
    ear_value FLOAT,
    mar_value FLOAT,
    head_yaw FLOAT,
    head_pitch FLOAT,
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_driver_live_status_company
    ON public.driver_live_status(company_id);

CREATE INDEX IF NOT EXISTS idx_driver_live_status_last_seen
    ON public.driver_live_status(last_seen_at DESC);

ALTER TABLE public.driver_live_status REPLICA IDENTITY FULL;

ALTER TABLE public.driver_live_status ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "super_admin_all_driver_live_status" ON public.driver_live_status;
CREATE POLICY "super_admin_all_driver_live_status"
    ON public.driver_live_status FOR ALL TO authenticated
    USING (get_user_role() = 'SUPER_ADMIN')
    WITH CHECK (get_user_role() = 'SUPER_ADMIN');

DROP POLICY IF EXISTS "company_admin_read_driver_live_status" ON public.driver_live_status;
CREATE POLICY "company_admin_read_driver_live_status"
    ON public.driver_live_status FOR SELECT TO authenticated
    USING (
        get_user_role() = 'COMPANY_ADMIN'
        AND company_id = get_user_company_id()
    );

DROP POLICY IF EXISTS "driver_own_driver_live_status" ON public.driver_live_status;
CREATE POLICY "driver_own_driver_live_status"
    ON public.driver_live_status FOR ALL TO authenticated
    USING (driver_id = auth.uid())
    WITH CHECK (driver_id = auth.uid());

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'supabase_realtime'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM pg_publication_tables
        WHERE pubname = 'supabase_realtime'
          AND schemaname = 'public'
          AND tablename = 'driver_live_status'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.driver_live_status;
    END IF;
END $$;
