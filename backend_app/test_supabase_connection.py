#!/usr/bin/env python3
"""
Test Supabase PostgreSQL Database Connection
Run this script to verify your Supabase database connection works.
"""

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, text

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test connection to Supabase PostgreSQL database"""
    
    # Get the database URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return False
    
    print(f"🔗 Testing connection to: {database_url[:50]}...")
    
    # Fix postgres:// to postgresql:// if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        print("🔧 Fixed postgres:// to postgresql://")
    
    try:
        # Create engine
        engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # Test connection
        with Session(engine) as session:
            result = session.exec(text("SELECT version()")).first()
            print(f"✅ Connection successful!")
            print(f"📊 Database version: {result}")
            
            # Test if our tables exist
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'otps', 'items', 'bills', 'sale_items')
                ORDER BY table_name
            """)
            
            existing_tables = session.exec(tables_query).all()
            
            if existing_tables:
                print(f"📋 Existing tables: {', '.join(existing_tables)}")
            else:
                print("⚠️  No application tables found. Run supabase_tables.sql first!")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n💡 Common issues:")
        print("   - Wrong password in connection string")
        print("   - Database URL format incorrect")
        print("   - Network/firewall issues")
        print("   - Supabase project not active")
        return False

def show_current_config():
    """Show current database configuration"""
    database_url = os.getenv("DATABASE_URL", "Not set")
    
    print("🔧 Current Configuration:")
    print(f"   DATABASE_URL: {database_url}")
    
    if "sqlite" in database_url.lower():
        print("   📁 Using SQLite (local file)")
        print("   ⚠️  To use Supabase, update DATABASE_URL in .env")
    elif "postgresql" in database_url.lower() or "postgres" in database_url.lower():
        print("   ☁️  Configured for PostgreSQL (Supabase)")
    else:
        print("   ❓ Unknown database type")

if __name__ == "__main__":
    print("🚀 Supabase Connection Test")
    print("=" * 40)
    
    show_current_config()
    print()
    
    if test_supabase_connection():
        print("\n✅ All good! Your app should work with Supabase.")
    else:
        print("\n❌ Fix the connection issues before proceeding.")