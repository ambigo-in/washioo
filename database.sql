-- Car Washing Service Portal - Scalable PostgreSQL Database Schema

--sql
-- ============================================================
-- CAr WASHING SERVICE PORTAL DATABASE SETUP
-- PostgreSQL Scalable Production Schema
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. ROLES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default roles
INSERT INTO roles (role_name, description) VALUES
('customer', 'Customer booking wash services'),
('cleaner', 'Cleaner providing wash services'),
('admin', 'System administrator')
ON CONFLICT (role_name) DO NOTHING;

-- ============================================================
-- 2. USERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(150),
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    profile_image_url TEXT,
    last_login TIMESTAMP,
    terms_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    terms_accepted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_terms_accepted ON users(terms_accepted);

-- ============================================================
-- 3. USER ROLES MAPPING
-- ============================================================
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE(user_id, role_id)
);

-- ============================================================
-- 4. OTP MANAGEMENT TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS otp_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(20) NOT NULL,
    otp_code_hash VARCHAR(255) NOT NULL,
    purpose VARCHAR(30) NOT NULL DEFAULT 'login', -- signup/login
    attempts INTEGER DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    consumed_at TIMESTAMP,
    created_ip VARCHAR(64),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_otp_phone ON otp_codes(phone);
CREATE INDEX idx_otp_expiry ON otp_codes(expires_at);

-- ============================================================
-- 5. REFRESH TOKENS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    jti VARCHAR(255) UNIQUE NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP,
    created_ip VARCHAR(64),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_refresh_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_jti ON refresh_tokens(jti);

-- ============================================================
-- 6. USER ADDRESSES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    address_label VARCHAR(50), -- Home/Office/Other
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    landmark TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',
    latitude NUMERIC(10,8),
    longitude NUMERIC(11,8),
    is_default BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_addresses_user ON addresses(user_id);
CREATE INDEX idx_addresses_user_active ON addresses(user_id, is_deleted);
CREATE INDEX idx_addresses_location ON addresses(latitude, longitude);
CREATE UNIQUE INDEX idx_one_default_address_per_user ON addresses(user_id) WHERE is_default = TRUE AND is_deleted = FALSE;

-- ============================================================
-- 7. CLEANER PROFILES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS cleaner_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL,
    vehicle_type VARCHAR(50), -- bike/car for transport
    aadhaar_number VARCHAR(20),
    aadhaar_number_hash VARCHAR(64),
    driving_license_number VARCHAR(100),
    driving_license_number_hash VARCHAR(64),
    government_id_number VARCHAR(100),
    service_radius_km NUMERIC(8,2),
    approval_status VARCHAR(30) DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected', 'suspended')),
    availability_status VARCHAR(30) DEFAULT 'offline' CHECK (availability_status IN ('offline', 'available', 'busy')),
    rating NUMERIC(3,2) DEFAULT 0,
    total_jobs_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_cleaner_status ON cleaner_profiles(approval_status, availability_status);
CREATE UNIQUE INDEX idx_cleaner_aadhaar_hash ON cleaner_profiles(aadhaar_number_hash) WHERE aadhaar_number_hash IS NOT NULL;
CREATE UNIQUE INDEX idx_cleaner_driving_license_hash ON cleaner_profiles(driving_license_number_hash) WHERE driving_license_number_hash IS NOT NULL;

-- ============================================================
-- 8. SERVICE CATEGORIES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS service_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(50) UNIQUE NOT NULL, -- Car Wash / Bike Wash
    description TEXT,
    base_price NUMERIC(10,2) NOT NULL,
    estimated_duration_minutes INTEGER,
    image_url VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO service_categories (service_name, description, base_price, estimated_duration_minutes)
VALUES
('Car Wash', 'Exterior and interior car wash service', 199.00, 60),
('Bike Wash', 'Complete bike wash service', 59.00, 30)
ON CONFLICT (service_name) DO NOTHING;

UPDATE service_categories
SET base_price = 199.00
WHERE service_name = 'Car Wash';

-- ============================================================
-- 9. BOOKINGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_reference VARCHAR(30) UNIQUE NOT NULL,
    customer_id UUID NOT NULL,
    service_category_id UUID NOT NULL,
    address_id UUID NOT NULL,
    scheduled_date DATE,
    scheduled_time TIME,
    special_instructions TEXT,
    booking_status VARCHAR(30) DEFAULT 'pending' CHECK (booking_status IN ('pending', 'assigned', 'accepted', 'in_progress', 'completed', 'cancelled')),
    -- pending, assigned, accepted, in_progress, completed, cancelled
    estimated_price NUMERIC(10,2) NOT NULL,
    final_price NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (service_category_id) REFERENCES service_categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (address_id) REFERENCES addresses(id) ON DELETE RESTRICT
);

CREATE INDEX idx_bookings_customer ON bookings(customer_id);
CREATE INDEX idx_bookings_status ON bookings(booking_status);
CREATE INDEX idx_bookings_date ON bookings(scheduled_date);
CREATE INDEX idx_bookings_customer_created ON bookings(customer_id, created_at DESC);
CREATE INDEX idx_bookings_status_created ON bookings(booking_status, created_at DESC);

-- ============================================================
-- 10. BOOKING ASSIGNMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS booking_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID UNIQUE NOT NULL,
    cleaner_id UUID NOT NULL,
    assigned_by_admin UUID NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    assignment_status VARCHAR(30) DEFAULT 'assigned' CHECK (assignment_status IN ('assigned', 'accepted', 'in_progress', 'rejected', 'completed', 'cancelled')),
    -- assigned, accepted, rejected, completed
    cleaner_notes TEXT,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (cleaner_id) REFERENCES cleaner_profiles(id) ON DELETE RESTRICT,
    FOREIGN KEY (assigned_by_admin) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX idx_assignments_cleaner ON booking_assignments(cleaner_id);
CREATE INDEX idx_assignments_status ON booking_assignments(assignment_status);
CREATE INDEX idx_assignments_cleaner_status_assigned ON booking_assignments(cleaner_id, assignment_status, assigned_at DESC);
CREATE INDEX idx_assignments_status_assigned ON booking_assignments(assignment_status, assigned_at DESC);

-- ============================================================
-- 11. PAYMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID UNIQUE NOT NULL,
    customer_id UUID NOT NULL,
    payment_method VARCHAR(30),
    -- Legacy UPI / Cash field
    transaction_reference VARCHAR(255),
    amount NUMERIC(10,2),
    payment_status VARCHAR(30) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed')),
    -- Legacy pending, paid, failed status
    collected_by_cleaner BOOLEAN DEFAULT FALSE,
    paid_at TIMESTAMP,
    collected_amount NUMERIC(10,2),
    payment_type VARCHAR(20) CHECK (payment_type IS NULL OR payment_type IN ('cash', 'upi')),
    collected_by UUID,
    collected_at TIMESTAMP,
    cleaner_share NUMERIC(10,2),
    admin_share NUMERIC(10,2),
    split_updated_by UUID,
    split_updated_at TIMESTAMP,
    payout_released BOOLEAN NOT NULL DEFAULT FALSE,
    cleaner_handover_status VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (cleaner_handover_status IN ('pending', 'settled')),
    status VARCHAR(30) NOT NULL DEFAULT 'pending_collection' CHECK (status IN ('pending_collection', 'collected', 'split_done')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (collected_by) REFERENCES cleaner_profiles(id) ON DELETE RESTRICT,
    FOREIGN KEY (split_updated_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_payments_status ON payments(payment_status);
CREATE INDEX idx_payments_method ON payments(payment_method);
CREATE INDEX idx_payments_collection_status ON payments(status);
CREATE INDEX idx_payments_collected_by ON payments(collected_by);
CREATE INDEX idx_payments_status_created ON payments(payment_status, created_at DESC);
CREATE INDEX idx_payments_customer_created ON payments(customer_id, created_at DESC);
CREATE INDEX idx_payments_collection_status_created ON payments(status, created_at DESC);
CREATE INDEX idx_payments_handover_status_created ON payments(cleaner_handover_status, created_at DESC);

-- ============================================================
-- 12. CLEANER EARNINGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS cleaner_earnings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cleaner_id UUID UNIQUE NOT NULL,
    total_earned NUMERIC(10,2) NOT NULL DEFAULT 0,
    pending_payout NUMERIC(10,2) NOT NULL DEFAULT 0,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cleaner_id) REFERENCES cleaner_profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_cleaner_earnings_cleaner ON cleaner_earnings(cleaner_id);

-- ============================================================
-- 13. CLEANER SETTLEMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS cleaner_settlements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cleaner_id UUID NOT NULL,
    booking_id UUID UNIQUE NOT NULL,
    payment_id UUID NOT NULL,
    collected_amount NUMERIC(10,2) NOT NULL,
    admin_received_amount NUMERIC(10,2),
    settlement_status VARCHAR(30) DEFAULT 'pending',
    -- pending, submitted, verified
    submitted_at TIMESTAMP,
    verified_at TIMESTAMP,
    verified_by_admin UUID,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cleaner_id) REFERENCES cleaner_profiles(id) ON DELETE RESTRICT,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by_admin) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_settlements_status ON cleaner_settlements(settlement_status);

-- ============================================================
-- 14. NOTIFICATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    notification_type VARCHAR(50),
    title VARCHAR(255),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_user_read_created ON notifications(user_id, is_read, created_at DESC);

CREATE TABLE IF NOT EXISTS push_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    endpoint TEXT NOT NULL,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    user_agent TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    CONSTRAINT uq_push_subscriptions_endpoint UNIQUE(endpoint),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_push_subscriptions_user_active ON push_subscriptions(user_id, is_active);

-- ============================================================
-- 15. REVIEWS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID UNIQUE NOT NULL,
    customer_id UUID NOT NULL,
    cleaner_id UUID NOT NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (cleaner_id) REFERENCES cleaner_profiles(id) ON DELETE CASCADE
);

-- ============================================================
-- 16. AUDIT LOGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

-- ============================================================
-- OPTIONAL TRIGGER FUNCTION FOR updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

-- Example triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- END OF SCHEMA
-- ============================================================


--# Scalability Highlights

-- ### This design supports:

-- * OTP-first authentication
-- * JWT refresh token lifecycle
-- * Multiple roles per user
-- * Live geolocation support
-- * Cleaner management
-- * Booking workflow lifecycle
-- * Admin assignment controls
-- * Cash + UPI payment tracking
-- * Settlement reconciliation
-- * Reviews & ratings
-- * Notifications
-- * Full audit logging
-- * Easy feature expansion (subscriptions, offers, franchises, analytics)

-- # Future Expansion Ready

-- You can later add:

-- * Coupon systems
-- * Wallet system
-- * Franchise branches
-- * Dynamic pricing
-- * Real-time cleaner tracking
-- * Subscription wash packages
-- * GST invoices
-- * Cleaner commissions
-- * Analytics dashboards
