-- Allow the desktop app alert type names used by app/shared/config/constants.py.
-- Run this once in Supabase SQL Editor.

ALTER TABLE public.alerts
DROP CONSTRAINT IF EXISTS alerts_alert_type_check;

ALTER TABLE public.alerts
ADD CONSTRAINT alerts_alert_type_check
CHECK (
    alert_type IN (
        'closed_eyes',
        'yawning',
        'drowsy',
        'distracted',
        'face_not_detected'
    )
);
