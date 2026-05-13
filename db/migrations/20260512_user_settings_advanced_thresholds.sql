-- Add advanced driver monitoring thresholds used by the desktop app.

ALTER TABLE public.user_settings
    ADD COLUMN IF NOT EXISTS head_yaw_threshold FLOAT NOT NULL DEFAULT 30.0,
    ADD COLUMN IF NOT EXISTS head_pitch_threshold FLOAT NOT NULL DEFAULT 25.0,
    ADD COLUMN IF NOT EXISTS distraction_seconds INT NOT NULL DEFAULT 3,
    ADD COLUMN IF NOT EXISTS face_not_detected_seconds INT NOT NULL DEFAULT 5;
