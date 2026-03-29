#!/usr/bin/env python3
"""
Test voice processing endpoint to check if the MessageToJson issue is fixed
"""

import requests
import json

def test_voice_processing():
    """Test the voice processing endpoint"""
    print("🧪 TESTING VOICE PROCESSING ENDPOINT")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test voice inputs
    test_inputs = [
        "hello hi",
        "category anaaj gehun 25 rupees kilo",
        "tomato 50 rs kg onion 30 rupees kilo",
        "2 kilo chawal 60 rupaye kilo"
    ]
    
    for i, voice_input in enumerate(test_inputs, 1):
        print(f"\n🔄 Test {i}: '{voice_input}'")
        
        try:
            payload = {
                "voice_text": voice_input
            }
            
            response = requests.post(
                f"{base_url}/voice/process",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS: {response.status_code}")
                
                # Show parsed categories and items
                if 'categories' in data:
                    print(f"   📦 Categories: {len(data['categories'])}")
                    for cat in data['categories']:
                        cat_name = cat.get('name', 'Unknown')
                        items = cat.get('items', [])
                        print(f"      • {cat_name}: {len(items)} items")
                        for item in items[:2]:  # Show first 2 items
                            name = item.get('name', 'Unknown')
                            price = item.get('price', 0)
                            unit = item.get('unit', 'kg')
                            print(f"        - {name}: ₹{price}/{unit}")
                else:
                    print(f"   📄 Response: {str(data)[:100]}...")
                    
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   💥 ERROR: {str(e)}")
    
    print(f"\n🏆 Voice processing test completed!")

def test_voice_endpoint_health():
    """Test if the voice endpoint is accessible"""
    print("\n🔍 CHECKING VOICE ENDPOINT HEALTH")
    print("-" * 40)
    
    try:
        # Test a simple request
        response = requests.post(
            "http://localhost:8000/voice/process",
            json={"voice_text": "test"},
            timeout=10
        )
        
        print(f"✅ Voice endpoint is accessible: HTTP {response.status_code}")
        return True
        
    except Exception as e:
        print(f"❌ Voice endpoint error: {str(e)}")
        return False

def main():
    print("🚀 VOICE PROCESSING TEST")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️  Server responded with non-200 status")
    except:
        print("❌ Server is not running!")
        return
    
    # Test voice endpoint health
    if not test_voice_endpoint_health():
        print("❌ Voice endpoint is not accessible")
        return
    
    # Run voice processing tests
    test_voice_processing()

if __name__ == "__main__":
    main()