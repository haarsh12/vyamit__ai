#!/usr/bin/env python3
"""
Test the AI service directly to see what's causing the system error
"""

import os
import sys
sys.path.append('.')

from app.services.ai_service import AIService
from app.db.models import Item

def test_ai_service_directly():
    """Test the AI service directly without going through the API"""
    print("🧪 TESTING AI SERVICE DIRECTLY")
    print("=" * 50)
    
    try:
        # Initialize AI service
        print("🔧 Initializing AI service...")
        ai_service = AIService()
        print("✅ AI service initialized")
        
        # Create mock inventory items
        mock_items = [
            type('Item', (), {
                'id': 1,
                'names': ['चावल', 'Rice', 'Chawal'],
                'price': 60,
                'unit': 'kg',
                'category': 'Grains',
                'owner_id': 1
            })(),
            type('Item', (), {
                'id': 2,
                'names': ['टमाटर', 'Tomato', 'Tamatar'],
                'price': 50,
                'unit': 'kg',
                'category': 'Vegetables',
                'owner_id': 1
            })()
        ]
        
        print(f"📦 Created {len(mock_items)} mock inventory items")
        
        # Test voice commands
        test_commands = [
            "hello hi",
            "2 kilo chawal",
            "tomato 1 kg",
            "chawal 2 kilo aur tamatar 1 kg"
        ]
        
        for i, command in enumerate(test_commands, 1):
            print(f"\n🔄 Test {i}: '{command}'")
            
            try:
                result = ai_service.process_voice_command(command, mock_items)
                
                print(f"   ✅ SUCCESS")
                print(f"   📋 Type: {result.get('type', 'Unknown')}")
                print(f"   💬 Message: {result.get('msg', 'No message')[:100]}...")
                
                if 'bill' in result and result['bill']:
                    print(f"   🧾 Bill items: {len(result['bill'])}")
                    for item in result['bill']:
                        name = item.get('item_name', 'Unknown')
                        qty = item.get('quantity', 0)
                        price = item.get('price_per_unit', 0)
                        total = item.get('total_price', 0)
                        print(f"      • {name}: {qty} × ₹{price} = ₹{total}")
                
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n✅ AI Service direct testing completed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize or test AI service: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_gemini_models_directly():
    """Test Gemini models directly to see if MessageToJson issue persists"""
    print("\n🧪 TESTING GEMINI MODELS DIRECTLY")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found")
            return False
        
        genai.configure(api_key=api_key, transport="rest")
        
        test_models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-flash-latest"
        ]
        
        simple_prompt = "Say hello in JSON format: {\"message\": \"hello\"}"
        
        for model_name in test_models:
            print(f"\n🔄 Testing {model_name}...")
            
            try:
                model = genai.GenerativeModel(model_name)
                
                # Test with generation config
                generation_config = {
                    "temperature": 0.1,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 100,
                }
                
                response = model.generate_content(
                    simple_prompt,
                    generation_config=generation_config
                )
                
                if response and response.text:
                    print(f"   ✅ SUCCESS: {model_name}")
                    print(f"   📝 Response: {response.text[:100]}...")
                    return True
                else:
                    print(f"   ⚠️ Empty response from {model_name}")
                    
            except Exception as e:
                print(f"   ❌ {model_name} failed: {str(e)}")
                if "MessageToJson" in str(e):
                    print(f"   🚨 MessageToJson error detected!")
        
        print("❌ All Gemini models failed")
        return False
        
    except Exception as e:
        print(f"❌ Gemini setup failed: {str(e)}")
        return False

def main():
    print("🚀 DIRECT AI SERVICE TESTING")
    print("=" * 60)
    
    # Test Gemini models directly first
    gemini_works = test_gemini_models_directly()
    
    # Test AI service
    ai_service_works = test_ai_service_directly()
    
    print(f"\n🏆 RESULTS:")
    print(f"   Gemini Direct: {'✅ WORKING' if gemini_works else '❌ FAILED'}")
    print(f"   AI Service: {'✅ WORKING' if ai_service_works else '❌ FAILED'}")
    
    if gemini_works and ai_service_works:
        print(f"\n🎉 Both Gemini and AI Service are working!")
    elif gemini_works:
        print(f"\n⚠️ Gemini works but AI Service has issues")
    else:
        print(f"\n❌ Gemini models are failing - this is the root cause")
        print(f"💡 The MessageToJson issue may still be present")

if __name__ == "__main__":
    main()