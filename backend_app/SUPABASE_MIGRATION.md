# Supabase Migration Guide

## Overview
This document outlines the database tables needed for migrating from SQLite to Supabase for your Kirana Shop Management system.

## Tables Structure

### 1. `users` Table (Shop Owners)
- **Primary Key**: `id` (BIGSERIAL)
- **Unique Fields**: `phone_number` (VARCHAR(15))
- **Purpose**: Store shop owner information
- **Key Fields**:
  - `phone_number`: Primary login identifier (READ ONLY)
  - `shop_name`: Name of the shop
  - `owner_name`: Owner's name
  - `address`: Shop address
  - `phone2`: Secondary phone number (EDITABLE)
  - `is_active`: Account status
  - `role`: User role (default: 'owner')

### 2. `otps` Table (Authentication)
- **Primary Key**: `id` (BIGSERIAL)
- **Purpose**: Store temporary OTP codes for phone-based authentication
- **Key Fields**:
  - `phone_number`: Phone number for OTP
  - `otp_code`: 6-digit OTP code
  - `expires_at`: Expiration timestamp
  - `is_used`: Whether OTP has been used

### 3. `items` Table (Inventory)
- **Primary Key**: `id` (BIGSERIAL)
- **Purpose**: Store inventory items with multi-language support
- **Key Fields**:
  - `master_id`: Frontend master list ID (e.g., "101", "FB1")
  - `names`: JSON array of names in multiple languages
  - `category`: Item category (e.g., "Anaaj", "Dal", "Masale")
  - `price`: Item price (DECIMAL(10,2))
  - `unit`: Unit of measurement (e.g., "kg", "litre")
  - `owner_id`: Foreign key to users table

### 4. `bills` Table (Saved Bills)
- **Primary Key**: `id` (BIGSERIAL)
- **Purpose**: Store complete bill information
- **Key Fields**:
  - `owner_id`: Foreign key to users table
  - `total_amount`: Total bill amount
  - `total_items`: Number of items in bill
  - `items_json`: JSON string of all bill items
  - `customer_phone`: Optional customer phone
  - `customer_name`: Optional customer name
  - `bill_date`: Date of bill creation
  - `payment_method`: Payment method (default: 'cash')

### 5. `sale_items` Table (Analytics)
- **Primary Key**: `id` (BIGSERIAL)
- **Purpose**: Store individual sale items for analytics and reporting
- **Key Fields**:
  - `owner_id`: Foreign key to users table
  - `bill_id`: Foreign key to bills table
  - `item_name`: Name of sold item
  - `item_category`: Category for analytics
  - `quantity`: Quantity sold
  - `unit`: Unit of measurement
  - `price_per_unit`: Price per unit
  - `total_price`: Total price for this item
  - `sale_date`: Sale timestamp
  - `hour_of_day`: Hour (0-23) for peak time analysis

## Key Features

### Data Types
- **BIGSERIAL**: Auto-incrementing primary keys
- **VARCHAR**: Text fields with length limits
- **TEXT**: Unlimited text fields (for JSON and long text)
- **DECIMAL(10,2)**: Precise decimal numbers for prices
- **TIMESTAMP WITH TIME ZONE**: Timezone-aware timestamps
- **BOOLEAN**: True/false values
- **INTEGER**: Whole numbers

### Indexes
- Phone number lookups
- Category-based searches
- Date-based queries
- Owner-based data filtering
- Analytics queries (hour of day, categories)

### Row Level Security (RLS)
- Users can only access their own data
- Automatic data isolation by owner
- Secure multi-tenant architecture

### Automatic Timestamps
- `created_at`: Set automatically on insert
- `updated_at`: Updated automatically on every update
- Triggers handle timestamp updates

## Migration Steps

1. **Create Tables**: Run `supabase_tables.sql` in your Supabase SQL Editor
2. **Update Backend**: Modify database connection to use Supabase
3. **Test Connection**: Verify all CRUD operations work
4. **Migrate Data**: Transfer existing SQLite data (if needed)
5. **Update Environment**: Configure Supabase credentials

## JSON Field Examples

### Items Names Field
```json
["Rice", "Chawal", "चावल", "तांदूळ"]
```

### Bills Items JSON Field
```json
[
  {
    "name": "Rice",
    "quantity": 2,
    "unit": "kg", 
    "price": 50,
    "total": 100
  },
  {
    "name": "Sugar",
    "quantity": 1,
    "unit": "kg",
    "price": 45,
    "total": 45
  }
]
```

## Security Notes
- All tables have Row Level Security enabled
- Users can only access their own data
- OTP table allows public insert for registration
- Phone number is used as the primary identifier for RLS policies

## Performance Optimizations
- Indexes on frequently queried fields
- Composite indexes for complex queries
- Efficient JSON field usage
- Proper foreign key relationships