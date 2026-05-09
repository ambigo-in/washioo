ALTER TABLE cleaner_profiles
    ADD COLUMN IF NOT EXISTS current_latitude NUMERIC(10,8),
    ADD COLUMN IF NOT EXISTS current_longitude NUMERIC(11,8),
    ADD COLUMN IF NOT EXISTS last_location_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS last_available_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS auto_assign_enabled BOOLEAN NOT NULL DEFAULT TRUE;

CREATE INDEX IF NOT EXISTS idx_cleaner_auto_assign
    ON cleaner_profiles(approval_status, availability_status, auto_assign_enabled);

ALTER TABLE booking_assignments
    ALTER COLUMN assigned_by_admin DROP NOT NULL,
    ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS rejected_reason TEXT,
    ADD COLUMN IF NOT EXISTS auto_assigned BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS assignment_rank INTEGER,
    ADD COLUMN IF NOT EXISTS assignment_score NUMERIC(8,2),
    ADD COLUMN IF NOT EXISTS distance_km NUMERIC(8,2);

CREATE INDEX IF NOT EXISTS idx_assignments_auto_assigned
    ON booking_assignments(auto_assigned, assignment_status);

ALTER TABLE notifications
    ADD COLUMN IF NOT EXISTS url TEXT;
