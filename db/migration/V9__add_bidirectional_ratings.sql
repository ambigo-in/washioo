CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    reviewee_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    reviewer_role VARCHAR(20) NOT NULL,
    rating NUMERIC(2,1) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_ratings_reviewer_role
        CHECK (reviewer_role IN ('customer', 'cleaner')),
    CONSTRAINT chk_ratings_rating_range
        CHECK (rating >= 1 AND rating <= 5),
    CONSTRAINT chk_ratings_comment_length
        CHECK (comment IS NULL OR char_length(comment) <= 500),
    CONSTRAINT chk_ratings_not_self_review
        CHECK (reviewer_id <> reviewee_id),
    CONSTRAINT uq_ratings_booking_reviewer
        UNIQUE (booking_id, reviewer_id)
);

CREATE INDEX IF NOT EXISTS idx_ratings_booking ON ratings(booking_id);
CREATE INDEX IF NOT EXISTS idx_ratings_reviewee ON ratings(reviewee_id);
CREATE INDEX IF NOT EXISTS idx_ratings_reviewer_role ON ratings(reviewer_role);
CREATE INDEX IF NOT EXISTS idx_ratings_created_at ON ratings(created_at);

ALTER TABLE cleaner_profiles
    ADD COLUMN IF NOT EXISTS average_rating NUMERIC(3,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS total_ratings INTEGER NOT NULL DEFAULT 0;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS average_rating NUMERIC(3,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS total_ratings INTEGER NOT NULL DEFAULT 0;

DO $$
BEGIN
    IF to_regclass('public.customer_profiles') IS NOT NULL THEN
        EXECUTE 'ALTER TABLE customer_profiles
            ADD COLUMN IF NOT EXISTS average_rating NUMERIC(3,2) NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS total_ratings INTEGER NOT NULL DEFAULT 0';
    END IF;
END $$;
