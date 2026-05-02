WITH ranked_defaults AS (
    SELECT
        id,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC, id DESC) AS rn
    FROM addresses
    WHERE is_default = TRUE
)
UPDATE addresses a
SET is_default = FALSE
FROM ranked_defaults r
WHERE a.id = r.id
  AND r.rn > 1;

CREATE UNIQUE INDEX IF NOT EXISTS idx_one_default_address_per_user
ON addresses(user_id)
WHERE is_default = TRUE;

ALTER TABLE bookings
    DROP CONSTRAINT IF EXISTS chk_bookings_status,
    ADD CONSTRAINT chk_bookings_status
    CHECK (booking_status IN ('pending', 'assigned', 'accepted', 'in_progress', 'completed', 'cancelled'));

ALTER TABLE booking_assignments
    DROP CONSTRAINT IF EXISTS chk_assignment_status,
    ADD CONSTRAINT chk_assignment_status
    CHECK (assignment_status IN ('assigned', 'accepted', 'in_progress', 'rejected', 'completed', 'cancelled'));

ALTER TABLE cleaner_profiles
    DROP CONSTRAINT IF EXISTS chk_cleaner_approval_status,
    ADD CONSTRAINT chk_cleaner_approval_status
    CHECK (approval_status IN ('pending', 'approved', 'rejected', 'suspended'));

ALTER TABLE cleaner_profiles
    DROP CONSTRAINT IF EXISTS chk_cleaner_availability_status,
    ADD CONSTRAINT chk_cleaner_availability_status
    CHECK (availability_status IN ('offline', 'available', 'busy'));

ALTER TABLE payments
    DROP CONSTRAINT IF EXISTS chk_payment_status,
    ADD CONSTRAINT chk_payment_status
    CHECK (payment_status IN ('pending', 'paid', 'failed'));
