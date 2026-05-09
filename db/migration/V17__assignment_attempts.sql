CREATE TABLE IF NOT EXISTS booking_assignment_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL,
    cleaner_id UUID NOT NULL,
    assignment_id UUID,
    status VARCHAR(30) NOT NULL DEFAULT 'offered',
    score NUMERIC(8,2),
    distance_km NUMERIC(8,2),
    reason TEXT,
    offered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    responded_at TIMESTAMP,
    CONSTRAINT chk_assignment_attempt_status
        CHECK (status IN ('offered', 'accepted', 'rejected', 'expired', 'skipped')),
    CONSTRAINT fk_assignment_attempt_booking
        FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    CONSTRAINT fk_assignment_attempt_cleaner
        FOREIGN KEY (cleaner_id) REFERENCES cleaner_profiles(id) ON DELETE RESTRICT,
    CONSTRAINT fk_assignment_attempt_assignment
        FOREIGN KEY (assignment_id) REFERENCES booking_assignments(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_assignment_attempts_booking
    ON booking_assignment_attempts(booking_id);

CREATE INDEX IF NOT EXISTS idx_assignment_attempts_cleaner
    ON booking_assignment_attempts(cleaner_id);

CREATE INDEX IF NOT EXISTS idx_assignment_attempts_status
    ON booking_assignment_attempts(status);

CREATE INDEX IF NOT EXISTS idx_assignment_attempts_booking_cleaner
    ON booking_assignment_attempts(booking_id, cleaner_id);
