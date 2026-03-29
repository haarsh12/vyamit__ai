#!/usr/bin/env python3
"""
🚀 Simple Test: Qwen → Gemini Fallback Chain
Tests the updated router with Qwen3.5-9B and specified Gemini models
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_mock_inventory():
    """Create mock inventory for testing"""
    class MockItem:
        def __init__(self, names, price, unit, category="grocery"):
            self.names = json.dumps(names) if isinstance(names, list) else names
            self.price = price
            self.unit = unit
            self.category = category
    
    return [
        MockItem(["chawal", "rice", "basmati"], 120.0, "kg"),
        MockItem(["maggie", "noodles"], 5.0, "pic"),
        MockItem(["sugar", "cheeni"], 45.0, "kg"),
    ]

def test_simple_cases():
    """Test simple cases to verify the system works"""
    print("\n🚀 TESTING QWEN → GEMINI FALLBACK CHAIN")
    print("=" * 50)
    
    try:
        from app.services.ai_service_router import AdaptiveMultiLLMService
        
        # Initialize service
        service = AdaptiveMultiLLMService()
        inventory = create_mock_inventory()
        
        # Test cases
        test_cases = [
            "namaste",
            "2 kilo chawal",
            "customer raju 5rs wali 6 maggie packet"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 TEST {i}: \"{test_case}\"")
            print("-" * 30)
            
            try:
                result = service.process_voice_command(test_case, inventory)
                print(f"✅ SUCCESS: {result.get('type', 'UNKNOWN')}")
                print(f"💬 Message: {result.get('msg', '')}")
                
                if result.get('items'):
                    print(f"📦 Items: {len(result['items'])}")
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
        
        print(f"\n🏆 SIMPLE TEST COMPLETE")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_cases()