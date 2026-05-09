ALTER TABLE service_categories
    ADD COLUMN IF NOT EXISTS allow_extra_payment BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS max_extra_amount NUMERIC(10,2),
    ADD COLUMN IF NOT EXISTS extra_payment_instructions TEXT;

ALTER TABLE service_categories
    DROP CONSTRAINT IF EXISTS chk_service_categories_max_extra_amount,
    ADD CONSTRAINT chk_service_categories_max_extra_amount
        CHECK (max_extra_amount IS NULL OR max_extra_amount >= 0);
