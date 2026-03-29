#!/usr/bin/env python3
"""
🔧 API Keys & Models Test
Tests if Gemini and Hugging Face APIs are working
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API with working models"""
    print("🧪 TESTING GEMINI API")
    print("=" * 30)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key, transport="rest")
        
        # Test with working models
        test_models = [
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest", 
            "gemini-pro-vision",
            "gemini-pro"
        ]
        
        for model_name in test_models:
            try:
                print(f"🔄 Testing {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'Hello' in JSON format: {\"msg\": \"Hello\"}")
                
                if response and response.text:
                    print(f"✅ {model_name} WORKS!")
                    print(f"   Response: {response.text[:50]}...")
                    return True
                else:
                    print(f"⚠️ {model_name} empty response")
                    
            except Exception as e:
                print(f"❌ {model_name} failed: {e}")
                continue
        
        print("❌ All Gemini models failed!")
        return False
        
    except Exception as e:
        print(f"❌ Gemini setup failed: {e}")
        return False

def test_huggingface_api():
    """Test Hugging Face API with Qwen models"""
    print("\n🧪 TESTING HUGGING FACE API")
    print("=" * 30)
    
    api_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not api_token:
        print("❌ HUGGINGFACE_API_TOKEN not found!")
        return False
    
    print(f"✅ API Token found: {api_token[:10]}...")
    
    # Test with Qwen models
    test_models = [
        "Qwen/Qwen3.5-9B",
        "Qwen/Qwen2.5-7B-Instruct",
        "Qwen/Qwen2-7B-Instruct"
    ]
    
    for model_name in test_models:
        try:
            print(f"🔄 Testing {model_name}...")
            url = f"https://router.huggingface.co/models/{model_name}"
            headers = {"Authorization": f"Bearer {api_token}"}
            
            payload = {
                "inputs": "Say hello in JSON: {\"msg\": \"Hello\"}",
                "parameters": {
                    "max_new_tokens": 50,
                    "temperature": 0.1,
                    "return_full_text": False
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": False
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {model_name} WORKS!")
                print(f"   Response: {result}")
                return True
            elif response.status_code == 503:
                print(f"⚠️ {model_name} is loading...")
            else:
                print(f"❌ {model_name} failed: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ {model_name} error: {e}")
            continue
    
    print("❌ All Qwen models failed!")
    return False

def main():
    print("🚀 API KEYS & MODELS TEST")
    print("=" * 50)
    
    gemini_works = test_gemini_api()
    hf_works = test_huggingface_api()
    
    print(f"\n🏆 RESULTS:")
    print(f"   Gemini API: {'✅ WORKING' if gemini_works else '❌ FAILED'}")
    print(f"   Hugging Face API: {'✅ WORKING' if hf_works else '❌ FAILED'}")
    
    if gemini_works or hf_works:
        print(f"\n✅ At least one API is working - system should function!")
    else:
        print(f"\n❌ Both APIs failed - check your API keys!")

if __name__ == "__main__":
    main()