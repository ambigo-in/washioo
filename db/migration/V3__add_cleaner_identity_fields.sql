ALTER TABLE cleaner_profiles
    ADD COLUMN IF NOT EXISTS aadhaar_number VARCHAR(20),
    ADD COLUMN IF NOT EXISTS driving_license_number VARCHAR(100);
    