CREATE INDEX IF NOT EXISTS idx_bookings_customer_created
    ON bookings(customer_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_bookings_status_created
    ON bookings(booking_status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_assignments_cleaner_status_assigned
    ON booking_assignments(cleaner_id, assignment_status, assigned_at DESC);

CREATE INDEX IF NOT EXISTS idx_assignments_status_assigned
    ON booking_assignments(assignment_status, assigned_at DESC);

CREATE INDEX IF NOT EXISTS idx_payments_status_created
    ON payments(payment_status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_payments_customer_created
    ON payments(customer_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_payments_collection_status_created
    ON payments(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_payments_handover_status_created
    ON payments(cleaner_handover_status, created_at DESC);
