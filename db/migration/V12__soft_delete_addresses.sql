ALTER TABLE addresses
    ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_addresses_user_active
    ON addresses(user_id, is_deleted);

DROP INDEX IF EXISTS idx_one_default_address_per_user;

CREATE UNIQUE INDEX IF NOT EXISTS idx_one_default_address_per_user
    ON addresses(user_id)
    WHERE is_default = TRUE AND is_deleted = FALSE;
