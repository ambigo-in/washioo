ALTER TABLE payments
    ALTER COLUMN payment_method DROP NOT NULL,
    ALTER COLUMN amount DROP NOT NULL;

ALTER TABLE payments
    ADD COLUMN IF NOT EXISTS collected_amount NUMERIC(10,2),
    ADD COLUMN IF NOT EXISTS payment_type VARCHAR(20),
    ADD COLUMN IF NOT EXISTS collected_by UUID,
    ADD COLUMN IF NOT EXISTS collected_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS cleaner_share NUMERIC(10,2),
    ADD COLUMN IF NOT EXISTS admin_share NUMERIC(10,2),
    ADD COLUMN IF NOT EXISTS split_updated_by UUID,
    ADD COLUMN IF NOT EXISTS split_updated_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS status VARCHAR(30) DEFAULT 'pending_collection';

UPDATE payments
SET
    collected_amount = COALESCE(collected_amount, amount),
    payment_type = COALESCE(
        payment_type,
        CASE
            WHEN LOWER(payment_method) IN ('cash', 'upi') THEN LOWER(payment_method)
            ELSE NULL
        END
    ),
    status = CASE
        WHEN payment_status = 'paid' THEN 'split_done'
        WHEN amount IS NOT NULL THEN 'collected'
        ELSE 'pending_collection'
    END
WHERE status IS NULL OR status = 'pending_collection';

ALTER TABLE payments
    ALTER COLUMN status SET DEFAULT 'pending_collection',
    ALTER COLUMN status SET NOT NULL;

ALTER TABLE payments
    ADD CONSTRAINT chk_payments_payment_type
        CHECK (payment_type IS NULL OR payment_type IN ('cash', 'upi')),
    ADD CONSTRAINT chk_payments_collection_status
        CHECK (status IN ('pending_collection', 'collected', 'split_done'));

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_payments_collected_by'
          AND table_name = 'payments'
    ) THEN
        ALTER TABLE payments
            ADD CONSTRAINT fk_payments_collected_by
            FOREIGN KEY (collected_by) REFERENCES cleaner_profiles(id) ON DELETE RESTRICT;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_payments_split_updated_by'
          AND table_name = 'payments'
    ) THEN
        ALTER TABLE payments
            ADD CONSTRAINT fk_payments_split_updated_by
            FOREIGN KEY (split_updated_by) REFERENCES users(id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_payments_collection_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_collected_by ON payments(collected_by);

CREATE TABLE IF NOT EXISTS cleaner_earnings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cleaner_id UUID UNIQUE NOT NULL,
    total_earned NUMERIC(10,2) NOT NULL DEFAULT 0,
    pending_payout NUMERIC(10,2) NOT NULL DEFAULT 0,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cleaner_id) REFERENCES cleaner_profiles(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cleaner_earnings_cleaner ON cleaner_earnings(cleaner_id);

UPDATE service_categories
SET base_price = CASE
    WHEN service_name = 'Bike Wash' THEN 59.00
    WHEN service_name = 'Car Wash' THEN 199.00
    ELSE base_price
END
WHERE service_name IN ('Bike Wash', 'Car Wash');
