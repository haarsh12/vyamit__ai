-- Vyamit AI Database Schema for NEW Supabase Project
-- Database: lhafpdiovrxxvxyqemtg.supabase.co
-- Run this in your NEW Supabase SQL Editor

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Shop details table
CREATE TABLE IF NOT EXISTS shop_details (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    shop_name VARCHAR(200) NOT NULL,
    address TEXT,
    phone1 VARCHAR(15),
    phone2 VARCHAR(15),
    gst_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Items table
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    alternative_names TEXT, -- JSON string of alternative names
    price DECIMAL(10,2) DEFAULT 0.0,
    unit VARCHAR(50) DEFAULT 'kg',
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bills table
CREATE TABLE IF NOT EXISTS bills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    bill_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(200),
    customer_phone VARCHAR(15),
    total_amount DECIMAL(10,2) DEFAULT 0.0,
    discount DECIMAL(10,2) DEFAULT 0.0,
    final_amount DECIMAL(10,2) DEFAULT 0.0,
    payment_method VARCHAR(50) DEFAULT 'cash',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bill items table
CREATE TABLE IF NOT EXISTS bill_items (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id),
    item_name VARCHAR(200) NOT NULL, -- Store name at time of billing
    quantity DECIMAL(10,3) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_items_user_id ON items(user_id);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at);
CREATE INDEX IF NOT EXISTS idx_bill_items_bill_id ON bill_items(bill_id);

-- Insert some sample data
INSERT INTO users (phone_number, name, email) VALUES 
('9876543210', 'Test Shop Owner', 'test@example.com')
ON CONFLICT (phone_number) DO NOTHING;

-- Sample shop details
INSERT INTO shop_details (user_id, shop_name, address, phone1) 
SELECT id, 'My Kirana Store', '123 Main Street, City', '9876543210' 
FROM users WHERE phone_number = '9876543210'
ON CONFLICT (user_id) DO NOTHING;

-- Sample items
INSERT INTO items (user_id, name, alternative_names, price, unit, category) 
SELECT id, 'Rice', '["Chawal", "चावल"]', 50.0, 'kg', 'Anaaj' 
FROM users WHERE phone_number = '9876543210'
ON CONFLICT DO NOTHING;

INSERT INTO items (user_id, name, alternative_names, price, unit, category) 
SELECT id, 'Wheat Flour', '["Atta", "आटा"]', 40.0, 'kg', 'Atta' 
FROM users WHERE phone_number = '9876543210'
ON CONFLICT DO NOTHING;

INSERT INTO items (user_id, name, alternative_names, price, unit, category) 
SELECT id, 'Sugar', '["Chini", "चीनी"]', 45.0, 'kg', 'Other' 
FROM users WHERE phone_number = '9876543210'
ON CONFLICT DO NOTHING;