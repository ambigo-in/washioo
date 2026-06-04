ALTER TABLE cleaner_profiles
    ADD COLUMN IF NOT EXISTS profile_photo_url TEXT,
    ADD COLUMN IF NOT EXISTS aadhaar_image_url TEXT,
    ADD COLUMN IF NOT EXISTS driving_license_image_url TEXT,
    ADD COLUMN IF NOT EXISTS verification_status VARCHAR(40) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS document_review_status VARCHAR(40) DEFAULT 'not_submitted',
    ADD COLUMN IF NOT EXISTS document_rejection_reason TEXT,
    ADD COLUMN IF NOT EXISTS document_resubmission_required BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS documents_submitted_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS documents_verified_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS documents_reviewed_by UUID,
    ADD COLUMN IF NOT EXISTS pending_aadhaar_number VARCHAR(20),
    ADD COLUMN IF NOT EXISTS pending_aadhaar_number_hash VARCHAR(64),
    ADD COLUMN IF NOT EXISTS pending_aadhaar_image_url TEXT,
    ADD COLUMN IF NOT EXISTS pending_driving_license_number VARCHAR(100),
    ADD COLUMN IF NOT EXISTS pending_driving_license_number_hash VARCHAR(64),
    ADD COLUMN IF NOT EXISTS pending_driving_license_image_url TEXT;

UPDATE cleaner_profiles
SET verification_status = CASE
        WHEN approval_status = 'approved' THEN 'approved'
        WHEN approval_status = 'rejected' THEN 'rejected'
        ELSE COALESCE(verification_status, 'pending')
    END,
    document_review_status = CASE
        WHEN approval_status = 'approved' THEN 'approved'
        WHEN approval_status = 'rejected' THEN 'rejected'
        ELSE COALESCE(document_review_status, 'not_submitted')
    END
WHERE verification_status IS NULL
   OR document_review_status IS NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_cleaner_documents_reviewed_by'
    ) THEN
        ALTER TABLE cleaner_profiles
            ADD CONSTRAINT fk_cleaner_documents_reviewed_by
            FOREIGN KEY (documents_reviewed_by)
            REFERENCES users(id)
            ON DELETE SET NULL;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'chk_cleaner_verification_status'
    ) THEN
        ALTER TABLE cleaner_profiles
            ADD CONSTRAINT chk_cleaner_verification_status
            CHECK (verification_status IN (
                'pending',
                'pending_reverification',
                'approved',
                'rejected',
                'resubmission_required'
            ));
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'chk_cleaner_document_review_status'
    ) THEN
        ALTER TABLE cleaner_profiles
            ADD CONSTRAINT chk_cleaner_document_review_status
            CHECK (document_review_status IN (
                'not_submitted',
                'pending_review',
                'approved',
                'rejected',
                'resubmission_required'
            ));
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_cleaner_verification_status
    ON cleaner_profiles(verification_status, document_review_status);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cleaner_pending_aadhaar_hash
    ON cleaner_profiles(pending_aadhaar_number_hash)
    WHERE pending_aadhaar_number_hash IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_cleaner_pending_driving_license_hash
    ON cleaner_profiles(pending_driving_license_number_hash)
    WHERE pending_driving_license_number_hash IS NOT NULL;
