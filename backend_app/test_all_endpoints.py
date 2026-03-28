#!/usr/bin/env python3
"""
Test all API endpoints for Vyamit AI Backend
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a single endpoint"""
    try:
        print(f"🔄 Testing {description}...")
        
        if method.upper() == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        elif method.upper() == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=5)
        elif method.upper() == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", json=data, timeout=5)
        elif method.upper() == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}", timeout=5)
        
        if response.status_code in [200, 201]:
            print(f"✅ {description}: SUCCESS")
            return True, response.json()
        else:
            print(f"❌ {description}: FAILED (Status: {response.status_code})")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {description}: CONNECTION FAILED")
        return False, None
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False, None

def main():
    """Test all endpoints"""
    print("🚀 Testing All Vyamit AI Backend Endpoints...\n")
    
    results = []
    
    # Basic endpoints
    success, _ = test_endpoint("GET", "/", description="Root Endpoint")
    results.append(("Root", success))
    
    success, _ = test_endpoint("GET", "/health", description="Health Check")
    results.append(("Health", success))
    
    # Authentication flow
    success, otp_response = test_endpoint("POST", "/auth/send-otp", 
                                        {"phone_number": "9876543210"}, 
                                        "Send OTP")
    results.append(("Send OTP", success))
    
    success, verify_response = test_endpoint("POST", "/auth/verify-otp", 
                                           {"phone_number": "9876543210", "otp": "123456"}, 
                                           "Verify OTP")
    results.append(("Verify OTP", success))
    
    success, _ = test_endpoint("POST", "/auth/register", 
                             {"phone_number": "9876543210", "name": "Test User", "email": "test@example.com"}, 
                             "Register User")
    results.append(("Register", success))
    
    # Shop details
    success, _ = test_endpoint("POST", "/api/v1/shop-details", 
                             {"shop_name": "My Test Shop", "address": "123 Test Street"}, 
                             "Create Shop Details")
    results.append(("Shop Details", success))
    
    success, _ = test_endpoint("GET", "/api/v1/shop-details", description="Get Shop Details")
    results.append(("Get Shop", success))
    
    # Items management
    success, item_response = test_endpoint("POST", "/api/v1/items", 
                                         {"name": "Test Item", "price": 100.0, "unit": "kg", "category": "Test"}, 
                                         "Create Item")
    results.append(("Create Item", success))
    
    success, _ = test_endpoint("GET", "/api/v1/items", description="Get Items")
    results.append(("Get Items", success))
    
    success, _ = test_endpoint("GET", "/api/v1/items/search?q=rice", description="Search Items")
    results.append(("Search Items", success))
    
    # Bills management
    success, _ = test_endpoint("POST", "/api/v1/bills", 
                             {
                                 "customer_name": "Test Customer",
                                 "items": [{"item_id": "1", "item_name": "Rice", "quantity": 2, "unit_price": 50, "total_price": 100}],
                                 "total_amount": 100,
                                 "final_amount": 100
                             }, 
                             "Create Bill")
    results.append(("Create Bill", success))
    
    success, _ = test_endpoint("GET", "/api/v1/bills", description="Get Bills")
    results.append(("Get Bills", success))
    
    # Analytics
    success, _ = test_endpoint("GET", "/api/v1/analytics/dashboard", description="Dashboard Analytics")
    results.append(("Analytics", success))
    
    # Voice command
    success, _ = test_endpoint("POST", "/api/v1/voice/process", 
                             {"command": "add new item"}, 
                             "Voice Command")
    results.append(("Voice Command", success))
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {name:<20} {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All endpoints are working! Backend is ready for frontend integration.")
    else:
        print("⚠️  Some endpoints failed. Check the server logs.")

if __name__ == "__main__":
    main()