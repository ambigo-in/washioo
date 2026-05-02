ALTER TABLE payments
    ADD COLUMN IF NOT EXISTS cleaner_handover_status VARCHAR(30) NOT NULL DEFAULT 'pending';

UPDATE payments
SET cleaner_handover_status = 'pending'
WHERE cleaner_handover_status IS NULL;

ALTER TABLE payments
    DROP CONSTRAINT IF EXISTS chk_payments_cleaner_handover_status,
    ADD CONSTRAINT chk_payments_cleaner_handover_status
        CHECK (cleaner_handover_status IN ('pending', 'settled'));
