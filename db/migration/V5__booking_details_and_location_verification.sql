ALTER TABLE addresses
    ADD COLUMN IF NOT EXISTS location_verified BOOLEAN DEFAULT FALSE;

UPDATE addresses
SET
    latitude = ROUND(latitude::numeric, 6),
    longitude = ROUND(longitude::numeric, 6),
    location_verified = CASE
        WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN TRUE
        ELSE FALSE
    END;

ALTER TABLE addresses
    ALTER COLUMN latitude TYPE NUMERIC(9,6),
    ALTER COLUMN longitude TYPE NUMERIC(9,6);

ALTER TABLE bookings
    ADD COLUMN IF NOT EXISTS vehicle_make VARCHAR(100),
    ADD COLUMN IF NOT EXISTS vehicle_model VARCHAR(100),
    ADD COLUMN IF NOT EXISTS license_plate VARCHAR(30);
