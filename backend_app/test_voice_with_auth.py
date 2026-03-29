#!/usr/bin/env python3
"""
Test voice processing with authentication
"""

import requests
import json
import time

class VoiceTestWithAuth:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
    
    def create_test_user(self):
        """Create a test user and get authentication token"""
        print("🔐 Creating test user...")
        
        test_phone = "9999999999"  # Test phone number
        
        try:
            # Step 1: Send OTP for registration
            print("   📱 Sending OTP for registration...")
            otp_response = requests.post(
                f"{self.base_url}/auth/send-otp",
                json={
                    "phone_number": test_phone,
                    "is_login": False  # Registration
                }
            )
            
            if otp_response.status_code == 200:
                otp_data = otp_response.json()
                otp_code = otp_data.get("dev_hint", "123456")  # Use dev hint or default
                print(f"   ✅ OTP sent: {otp_code}")
            else:
                # User might already exist, try login
                print("   ⚠️ Registration failed, trying login...")
                otp_response = requests.post(
                    f"{self.base_url}/auth/send-otp",
                    json={
                        "phone_number": test_phone,
                        "is_login": True  # Login
                    }
                )
                
                if otp_response.status_code == 200:
                    otp_data = otp_response.json()
                    otp_code = otp_data.get("dev_hint", "123456")
                    print(f"   ✅ Login OTP sent: {otp_code}")
                else:
                    print(f"   ❌ Failed to send OTP: {otp_response.text}")
                    return False
            
            # Step 2: Verify OTP and get token
            print("   🔑 Verifying OTP...")
            verify_response = requests.post(
                f"{self.base_url}/auth/verify-otp",
                json={
                    "phone_number": test_phone,
                    "otp_code": otp_code,
                    "shop_name": "Test Shop",
                    "owner_name": "Test Owner",
                    "address": "Test Address"
                }
            )
            
            if verify_response.status_code == 200:
                auth_data = verify_response.json()
                self.token = auth_data["access_token"]
                self.user_id = auth_data["user_id"]
                print(f"   ✅ Authentication successful! User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ OTP verification failed: {verify_response.text}")
                return False
                
        except Exception as e:
            print(f"   💥 Authentication error: {str(e)}")
            return False
    
    def test_voice_processing(self):
        """Test voice processing with authentication"""
        if not self.token:
            print("❌ No authentication token available")
            return False
        
        print("\n🧪 TESTING VOICE PROCESSING WITH AUTH")
        print("=" * 50)
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Test voice inputs
        test_inputs = [
            "hello hi",
            "category anaaj gehun 25 rupees kilo",
            "tomato 50 rs kg onion 30 rupees kilo",
            "2 kilo chawal 60 rupaye kilo"
        ]
        
        results = []
        
        for i, voice_input in enumerate(test_inputs, 1):
            print(f"\n🔄 Test {i}: '{voice_input}'")
            
            try:
                payload = {
                    "text": voice_input  # Note: using 'text' not 'voice_text'
                }
                
                response = requests.post(
                    f"{self.base_url}/voice/process",
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS: {response.status_code}")
                    
                    # Show response details
                    if 'type' in data:
                        print(f"   📋 Type: {data['type']}")
                        print(f"   💬 Message: {data.get('msg', 'No message')[:100]}...")
                        
                        if 'bill' in data and data['bill']:
                            print(f"   🧾 Bill items: {len(data['bill'])}")
                            for item in data['bill'][:2]:  # Show first 2 items
                                name = item.get('item_name', 'Unknown')
                                qty = item.get('quantity', 0)
                                price = item.get('price_per_unit', 0)
                                total = item.get('total_price', 0)
                                print(f"      • {name}: {qty} × ₹{price} = ₹{total}")
                    else:
                        print(f"   📄 Response: {str(data)[:200]}...")
                    
                    results.append(True)
                else:
                    print(f"   ❌ FAILED: HTTP {response.status_code}")
                    print(f"   Error: {response.text[:200]}")
                    results.append(False)
                    
            except Exception as e:
                print(f"   💥 ERROR: {str(e)}")
                results.append(False)
            
            time.sleep(1)  # Small delay between requests
        
        # Summary
        success_count = sum(results)
        total_count = len(results)
        success_rate = (success_count / total_count) * 100
        
        print(f"\n📊 VOICE PROCESSING RESULTS:")
        print(f"   Success Rate: {success_rate:.1f}% ({success_count}/{total_count})")
        
        return success_rate > 50  # Consider successful if > 50% pass
    
    def run_complete_test(self):
        """Run complete test with authentication and voice processing"""
        print("🚀 VOICE PROCESSING TEST WITH AUTHENTICATION")
        print("=" * 60)
        
        # Check server
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Server is running")
            else:
                print("⚠️ Server responded with non-200 status")
                return False
        except:
            print("❌ Server is not running!")
            return False
        
        # Create test user and authenticate
        if not self.create_test_user():
            print("❌ Failed to create test user or authenticate")
            return False
        
        # Test voice processing
        voice_success = self.test_voice_processing()
        
        print(f"\n🏆 FINAL RESULTS:")
        print(f"   Authentication: ✅ SUCCESS")
        print(f"   Voice Processing: {'✅ SUCCESS' if voice_success else '❌ FAILED'}")
        
        if voice_success:
            print(f"\n🎉 VOICE PROCESSING IS WORKING!")
            print(f"💡 The MessageToJson issue appears to be resolved")
        else:
            print(f"\n⚠️ Voice processing has issues - check the logs above")
        
        return voice_success

def main():
    tester = VoiceTestWithAuth()
    success = tester.run_complete_test()
    
    if success:
        print("\n🚀 Ready for voice-based inventory management!")
    else:
        print("\n🔧 Fix voice processing issues before production use")

if __name__ == "__main__":
    main()