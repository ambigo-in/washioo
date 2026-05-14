ALTER TABLE users
    ADD COLUMN IF NOT EXISTS terms_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS terms_accepted_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_users_terms_accepted
    ON users(terms_accepted);
