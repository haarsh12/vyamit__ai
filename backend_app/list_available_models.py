#!/usr/bin/env python3
"""
🔍 List Available Models
Find out which models actually work with current API keys
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_gemini_models():
    """List available Gemini models"""
    print("🔍 LISTING GEMINI MODELS")
    print("=" * 30)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        return
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key, transport="rest")
        
        # List available models
        models = genai.list_models()
        print("✅ Available Gemini models:")
        for model in models:
            print(f"   • {model.name}")
            
    except Exception as e:
        print(f"❌ Failed to list Gemini models: {e}")

def test_simple_huggingface():
    """Test simple Hugging Face models"""
    print("\n🔍 TESTING SIMPLE HUGGING FACE MODELS")
    print("=" * 40)
    
    api_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not api_token:
        print("❌ HUGGINGFACE_API_TOKEN not found!")
        return
    
    # Try simple, reliable models
    simple_models = [
        "microsoft/DialoGPT-medium",
        "facebook/blenderbot-400M-distill",
        "google/flan-t5-small"
    ]
    
    for model_name in simple_models:
        try:
            print(f"🔄 Testing {model_name}...")
            
            # Try both endpoints
            endpoints = [
                f"https://api-inference.huggingface.co/models/{model_name}",
                f"https://router.huggingface.co/models/{model_name}"
            ]
            
            for url in endpoints:
                try:
                    headers = {"Authorization": f"Bearer {api_token}"}
                    payload = {
                        "inputs": "Hello",
                        "parameters": {"max_new_tokens": 20}
                    }
                    
                    response = requests.post(url, headers=headers, json=payload, timeout=10)
                    print(f"   {url}: HTTP {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ SUCCESS: {result}")
                        return True
                    else:
                        try:
                            error = response.json()
                            print(f"   Error: {error}")
                        except:
                            print(f"   Error: {response.text[:100]}")
                            
                except Exception as e:
                    print(f"   ❌ {url}: {e}")
                    
        except Exception as e:
            print(f"❌ {model_name} failed: {e}")

def main():
    print("🚀 AVAILABLE MODELS DISCOVERY")
    print("=" * 50)
    
    list_gemini_models()
    test_simple_huggingface()

if __name__ == "__main__":
    main()