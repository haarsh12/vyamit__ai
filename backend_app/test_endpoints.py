#!/usr/bin/env python3
"""
Test FastAPI backend endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, description):
    """Test a single endpoint"""
    try:
        print(f"🔄 Testing {description}...")
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}: SUCCESS")
            print(f"   📄 Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ {description}: FAILED (Status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {description}: CONNECTION FAILED (Server not running?)")
        return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False

def main():
    """Test all endpoints"""
    print("🚀 Testing Vyamit AI Backend Endpoints...\n")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    endpoints = [
        ("/", "Root Endpoint"),
        ("/health", "Health Check"),
        ("/api/test", "API Test"),
        ("/api/database/test", "Database Test"),
        ("/api/v1/users", "Users API"),
        ("/api/v1/items", "Items API"),
        ("/api/v1/bills", "Bills API")
    ]
    
    results = []
    for endpoint, description in endpoints:
        success = test_endpoint(endpoint, description)
        results.append((description, success))
        print()  # Add spacing
    
    # Summary
    print("📊 Test Results Summary:")
    print("=" * 50)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {description:<20} {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs.")

if __name__ == "__main__":
    main()