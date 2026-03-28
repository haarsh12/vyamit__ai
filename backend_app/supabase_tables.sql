-- Supabase Database Schema for Kirana Shop Management
-- Run this in your Supabase SQL Editor to create all required tables

-- Enable Row Level Security (RLS) for all tables
-- This ensures users can only access their own data

-- 1. Users Table (Shop Owners)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    shop_name VARCHAR(200),
    owner_name VARCHAR(200),
    address TEXT,
    phone2 VARCHAR(15), -- Secondary phone number (editable)
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'owner',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. OTP Table (Temporary codes for authentication)
CREATE TABLE IF NOT EXISTS otps (
    id BIGSERIAL PRIMARY KEY,
    phone_number VARCHAR(15) NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Items Table (Inventory Management)
CREATE TABLE IF NOT EXISTS items (
    id BIGSERIAL PRIMARY KEY,
    master_id VARCHAR(50) NOT NULL, -- Frontend master list ID (e.g., "101", "FB1")
    names TEXT NOT NULL, -- JSON array of names: ["Chawal", "Rice", "चावल"]
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) DEFAULT 0.0,
    unit VARCHAR(50) NOT NULL,
    owner_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Bills Table (Saved Bills)
CREATE TABLE IF NOT EXISTS bills (
    id BIGSERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_amount DECIMAL(10,2) NOT NULL,
    total_items INTEGER NOT NULL,
    items_json TEXT NOT NULL, -- JSON array of bill items
    customer_phone VARCHAR(15),
    customer_name VARCHAR(200),
    bill_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50) DEFAULT 'cash',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Sale Items Table (Individual items sold - for analytics)
CREATE TABLE IF NOT EXISTS sale_items (
    id BIGSERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bill_id BIGINT NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    item_name VARCHAR(200) NOT NULL,
    item_category VARCHAR(100) NOT NULL,
    quantity DECIMAL(10,3) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    sale_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hour_of_day INTEGER NOT NULL CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for Better Performance
CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_otps_phone_number ON otps(phone_number);
CREATE INDEX IF NOT EXISTS idx_otps_expires_at ON otps(expires_at);
CREATE INDEX IF NOT EXISTS idx_otps_is_used ON otps(is_used);

CREATE INDEX IF NOT EXISTS idx_items_owner_id ON items(owner_id);
CREATE INDEX IF NOT EXISTS idx_items_master_id ON items(master_id);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);

CREATE INDEX IF NOT EXISTS idx_bills_owner_id ON bills(owner_id);
CREATE INDEX IF NOT EXISTS idx_bills_bill_date ON bills(bill_date);
CREATE INDEX IF NOT EXISTS idx_bills_payment_method ON bills(payment_method);

CREATE INDEX IF NOT EXISTS idx_sale_items_owner_id ON sale_items(owner_id);
CREATE INDEX IF NOT EXISTS idx_sale_items_bill_id ON sale_items(bill_id);
CREATE INDEX IF NOT EXISTS idx_sale_items_category ON sale_items(item_category);
CREATE INDEX IF NOT EXISTS idx_sale_items_sale_date ON sale_items(sale_date);
CREATE INDEX IF NOT EXISTS idx_sale_items_hour_of_day ON sale_items(hour_of_day);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE otps ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE bills ENABLE ROW LEVEL SECURITY;
ALTER TABLE sale_items ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Users table
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text OR phone_number = auth.jwt() ->> 'phone');

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text OR phone_number = auth.jwt() ->> 'phone');

CREATE POLICY "Users can insert their own profile" ON users
    FOR INSERT WITH CHECK (true); -- Allow registration

-- RLS Policies for OTPs table
CREATE POLICY "Users can view their own OTPs" ON otps
    FOR SELECT USING (phone_number = auth.jwt() ->> 'phone');

CREATE POLICY "Anyone can insert OTPs" ON otps
    FOR INSERT WITH CHECK (true); -- Allow OTP generation

CREATE POLICY "Users can update their own OTPs" ON otps
    FOR UPDATE USING (phone_number = auth.jwt() ->> 'phone');

-- RLS Policies for Items table
CREATE POLICY "Users can view their own items" ON items
    FOR SELECT USING (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

CREATE POLICY "Users can insert their own items" ON items
    FOR INSERT WITH CHECK (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

CREATE POLICY "Users can update their own items" ON items
    FOR UPDATE USING (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

CREATE POLICY "Users can delete their own items" ON items
    FOR DELETE USING (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

-- RLS Policies for Bills table
CREATE POLICY "Users can view their own bills" ON bills
    FOR SELECT USING (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

CREATE POLICY "Users can insert their own bills" ON bills
    FOR INSERT WITH CHECK (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

CREATE POLICY "Users can update their own bills" ON bills
    FOR UPDATE USING (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

CREATE POLICY "Users can delete their own bills" ON bills
    FOR DELETE USING (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

-- RLS Policies for Sale Items table
CREATE POLICY "Users can view their own sale items" ON sale_items
    FOR SELECT USING (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

CREATE POLICY "Users can insert their own sale items" ON sale_items
    FOR INSERT WITH CHECK (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

CREATE POLICY "Users can update their own sale items" ON sale_items
    FOR UPDATE USING (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

CREATE POLICY "Users can delete their own sale items" ON sale_items
    FOR DELETE USING (owner_id = (SELECT id FROM users WHERE phone_number = auth.jwt() ->> 'phone'));

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_items_updated_at BEFORE UPDATE ON items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bills_updated_at BEFORE UPDATE ON bills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sale_items_updated_at BEFORE UPDATE ON sale_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional)
INSERT INTO users (phone_number, shop_name, owner_name, address) VALUES 
('9876543210', 'Sample Kirana Store', 'Test Owner', '123 Main Street, Sample City')
ON CONFLICT (phone_number) DO NOTHING;

-- Sample items with multi-language names
INSERT INTO items (master_id, names, category, price, unit, owner_id) 
SELECT '101', '["Rice", "Chawal", "चावल"]', 'Anaaj', 50.0, 'kg', id 
FROM users WHERE phone_number = '9876543210'
ON CONFLICT DO NOTHING;

INSERT INTO items (master_id, names, category, price, unit, owner_id) 
SELECT '102', '["Wheat Flour", "Atta", "आटा"]', 'Atta', 40.0, 'kg', id 
FROM users WHERE phone_number = '9876543210'
ON CONFLICT DO NOTHING;

INSERT INTO items (master_id, names, category, price, unit, owner_id) 
SELECT '103', '["Sugar", "Chini", "चीनी"]', 'Other', 45.0, 'kg', id 
FROM users WHERE phone_number = '9876543210'
ON CONFLICT DO NOTHING;