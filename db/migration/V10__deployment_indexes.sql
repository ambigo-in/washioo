CREATE INDEX IF NOT EXISTS idx_bookings_service_category
ON bookings(service_category_id);

CREATE INDEX IF NOT EXISTS idx_bookings_address
ON bookings(address_id);

CREATE INDEX IF NOT EXISTS idx_assignments_booking
ON booking_assignments(booking_id);

CREATE INDEX IF NOT EXISTS idx_payments_booking
ON payments(booking_id);

CREATE INDEX IF NOT EXISTS idx_payments_customer
ON payments(customer_id);

CREATE INDEX IF NOT EXISTS idx_payments_cleaner_handover_status
ON payments(cleaner_handover_status);

CREATE INDEX IF NOT EXISTS idx_ratings_reviewer
ON ratings(reviewer_id);
