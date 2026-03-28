#!/usr/bin/env python3
"""
Test script for voice processing with Hybrid AI Service
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
        MockItem(["oil", "tel", "cooking oil"], 150.0, "litre"),
        MockItem(["atta", "wheat flour"], 40.0, "kg")
    ]

def test_voice_commands():
    """Test various voice commands"""
    print("🎤 Testing Voice Commands with Hybrid AI Service")
    print("=" * 60)
    
    try:
        from app.services.ai_service_hybrid import HybridAIService
        
        # Initialize service
        service = HybridAIService()
        inventory = create_mock_inventory()
        
        # Test commands
        test_cases = [
            "namaste",
            "hello vyamit ai",
            "2kg chawal",
            "customer raju charde 5rs wali 6 maggie packet",
            "1kg sugar 45 rupaye kilo",
            "aam"  # Not in inventory
        ]
        
        for i, command in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: '{command}'")
            print("-" * 30)
            
            try:
                result = service.process_voice_command(command, inventory)
                service_used = result.pop("_service_used", "unknown")
                print(f"🔧 Service used: {service_used}")
                print(f"✅ Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Test chat history
        print(f"\n💬 Chat History:")
        print("-" * 30)
        history = service.get_chat_history()
        for msg in history[-4:]:  # Show last 4 messages
            print(f"{msg['role']}: {msg['content']}")
        
        print(f"\n📊 Total messages in history: {len(history)}")
        
        # Test service info
        print(f"\n🔧 Service Info:")
        print("-" * 30)
        info = service.get_service_info()
        print(json.dumps(info, indent=2))
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        print("\n💡 Make sure to:")
        print("   1. Set HUGGINGFACE_API_TOKEN and/or GEMINI_API_KEY in .env")
        print("   2. Install dependencies: pip install google-generativeai")
        print("   3. Check your internet connection")

if __name__ == "__main__":
    test_voice_commands()