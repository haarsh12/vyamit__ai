"""One-shot: add user.shop_category on PostgreSQL. Run from backend_app: python apply_shop_category_migration.py"""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(Path(__file__).resolve().parent / ".env")
url = os.getenv("DATABASE_URL")
if not url:
    raise SystemExit("DATABASE_URL not set")
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(url, pool_pre_ping=True)
stmts = [
    'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS shop_category VARCHAR(64) NOT NULL DEFAULT \'General\'',
    'CREATE INDEX IF NOT EXISTS ix_user_shop_category ON "user" (shop_category)',
    'UPDATE "user" SET shop_category = \'General\' WHERE shop_category IS NULL OR trim(shop_category) = \'\'',
]
with engine.connect() as conn:
    for s in stmts:
        conn.execute(text(s))
    conn.commit()
print("OK: shop_category migration applied.")
