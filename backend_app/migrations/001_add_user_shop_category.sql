-- Run once on Supabase SQL editor (PostgreSQL).
-- Adds shop type for Vyamit merchants. Safe to re-run: IF NOT EXISTS.

ALTER TABLE "user" ADD COLUMN IF NOT EXISTS shop_category VARCHAR(64) NOT NULL DEFAULT 'General';

CREATE INDEX IF NOT EXISTS ix_user_shop_category ON "user" (shop_category);

-- Backfill any NULL (defensive)
UPDATE "user" SET shop_category = 'General' WHERE shop_category IS NULL OR trim(shop_category) = '';
