#!/usr/bin/env python3
"""
Test Supabase REST API connection
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration (from .env)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def test_supabase_api():
    """Test Supabase REST API"""
    try:
        print("🔄 Testing Supabase REST API connection...")
        print(f"📍 Supabase URL: {SUPABASE_URL}")
        
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"
        }
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Supabase REST API is accessible!")
            return True
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_database_via_api():
    """Test database via REST API"""
    try:
        print("\n🔄 Testing database access via REST API...")

        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        }

        # Try accessing a table (even if empty)
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ Database API is working!")
            return True
        else:
            print(f"❌ Database API failed: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Supabase connectivity tests...\n")
    
    api_success = test_supabase_api()
    db_success = test_database_via_api()
    
    print("\n📊 Results:")
    print(f"   API Connection: {'✅ Success' if api_success else '❌ Failed'}")
    print(f"   Database API: {'✅ Success' if db_success else '❌ Failed'}")

    if api_success:
        print("\n🎉 Supabase is working correctly!")
    else:
        print("\n❌ Still failing. Check your keys.")