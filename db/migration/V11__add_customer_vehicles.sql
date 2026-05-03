CREATE TABLE IF NOT EXISTS customer_vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vehicle_type VARCHAR(30) NOT NULL,
    make VARCHAR(100),
    model VARCHAR(100),
    license_plate VARCHAR(30),
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_customer_vehicles_type CHECK (vehicle_type IN ('bike', 'car'))
);

CREATE INDEX IF NOT EXISTS idx_customer_vehicles_customer
    ON customer_vehicles(customer_id);

CREATE INDEX IF NOT EXISTS idx_customer_vehicles_default
    ON customer_vehicles(customer_id, is_default);

ALTER TABLE bookings
    ADD COLUMN IF NOT EXISTS vehicle_id UUID REFERENCES customer_vehicles(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_bookings_vehicle
    ON bookings(vehicle_id);
