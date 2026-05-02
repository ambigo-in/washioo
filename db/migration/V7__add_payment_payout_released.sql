ALTER TABLE payments
    ADD COLUMN IF NOT EXISTS payout_released BOOLEAN NOT NULL DEFAULT FALSE;

UPDATE payments
SET payout_released = FALSE
WHERE payout_released IS NULL;
