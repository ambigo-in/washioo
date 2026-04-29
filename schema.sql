-- On-Demand Vehicle Wash MVP - PostgreSQL Schema

-- ENUMS
CREATE TYPE user_role AS ENUM ('customer', 'admin', 'cleaner');
CREATE TYPE vehicle_type AS ENUM ('car', 'bike');
CREATE TYPE booking_status AS ENUM ('pending', 'assigned', 'en_route', 'in_progress', 'completed', 'cancelled', 'failed');
CREATE TYPE payment_status AS ENUM ('unpaid', 'paid');
CREATE TYPE payment_method AS ENUM ('cash', 'upi');

-- USERS TABLE
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    role user_role NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VEHICLES TABLE
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    vehicle_type vehicle_type NOT NULL,
    vehicle_model VARCHAR(100) NOT NULL,
    vehicle_number VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PACKAGES TABLE
CREATE TABLE packages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_type vehicle_type NOT NULL,
    package_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    duration_minutes INTEGER NOT NULL
);

-- BOOKINGS TABLE
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    package_id UUID REFERENCES packages(id) ON DELETE SET NULL,
    cleaner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    scheduled_at TIMESTAMP,
    status booking_status DEFAULT 'pending',
    payment_status payment_status DEFAULT 'unpaid',
    payment_method payment_method,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CLEANER LOCATIONS TABLE
CREATE TABLE cleaner_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cleaner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SEED DATA FOR PACKAGES
INSERT INTO packages (vehicle_type, package_name, description, price, duration_minutes) VALUES
('car', 'Basic Wash', 'Exterior wash and dry', 149, 30),
('car', 'Deep Clean', 'Interior + exterior deep cleaning', 349, 60),
('car', 'Premium Detail', 'Full detailing and polish', 599, 90),
('bike', 'Basic Wash', 'Exterior wash and dry', 79, 20),
('bike', 'Deep Clean', 'Full bike cleaning', 199, 40);
