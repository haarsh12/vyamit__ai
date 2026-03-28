#!/usr/bin/env python3
"""
Simple script to test Supabase PostgreSQL connection
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env_config")

# NEW Supabase Database URL
DATABASE_URL = "postgresql://postgres:VyamitAI12fgco@db.lhafpdiovrxxvxyqemtg.supabase.co:5432/postgres"

def test_connection():
    """Test database connection"""
    try:
        print("🔄 Testing Supabase PostgreSQL connection...")
        print(f"📍 Database URL: {DATABASE_URL.replace('VarietyChowk12', '***')}")
        
        # Create engine
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"📊 PostgreSQL Version: {version}")
            
            # Test basic query
            result = connection.execute(text("SELECT current_database(), current_user"))
            db_info = result.fetchone()
            print(f"🗄️  Database: {db_info[0]}")
            print(f"👤 User: {db_info[1]}")
            
            # Test table creation
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert test data
            connection.execute(text("""
                INSERT INTO test_connection (message) 
                VALUES ('Vyamit AI Backend Connection Test')
            """))
            
            # Query test data
            result = connection.execute(text("SELECT * FROM test_connection ORDER BY id DESC LIMIT 1"))
            test_data = result.fetchone()
            print(f"🧪 Test Data: {test_data}")
            
            # Clean up
            connection.execute(text("DROP TABLE IF EXISTS test_connection"))
            connection.commit()
            
            print("🎉 All database tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)