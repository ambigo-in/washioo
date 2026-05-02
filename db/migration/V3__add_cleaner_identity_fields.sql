ALTER TABLE cleaner_profiles
    ADD COLUMN IF NOT EXISTS aadhaar_number VARCHAR(20),
    ADD COLUMN IF NOT EXISTS aadhaar_number_hash VARCHAR(64),
    ADD COLUMN IF NOT EXISTS driving_license_number VARCHAR(100),
    ADD COLUMN IF NOT EXISTS driving_license_number_hash VARCHAR(64);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cleaner_aadhaar_hash
ON cleaner_profiles(aadhaar_number_hash)
WHERE aadhaar_number_hash IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_cleaner_driving_license_hash
ON cleaner_profiles(driving_license_number_hash)
WHERE driving_license_number_hash IS NOT NULL;
