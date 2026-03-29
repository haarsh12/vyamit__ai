#!/usr/bin/env python3
"""
🔧 Fixed API Keys & Models Test
Tests if Gemini and Hugging Face APIs are working with correct model names
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API with available models"""
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
        
        # Test with available models (from list_available_models.py output)
        test_models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro", 
            "gemini-2.0-flash",
            "gemini-flash-latest",
            "gemini-pro-latest"
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
                print(f"❌ {model_name} failed: {str(e)[:100]}...")
                continue
        
        print("❌ All Gemini models failed!")
        return False
        
    except Exception as e:
        print(f"❌ Gemini setup failed: {e}")
        return False

def test_huggingface_api():
    """Test Hugging Face API with working models"""
    print("\n🧪 TESTING HUGGING FACE API")
    print("=" * 30)
    
    api_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not api_token:
        print("❌ HUGGINGFACE_API_TOKEN not found!")
        return False
    
    print(f"✅ API Token found: {api_token[:10]}...")
    
    # Test with popular working models
    test_models = [
        "microsoft/DialoGPT-medium",
        "facebook/blenderbot-400M-distill",
        "google/flan-t5-small",
        "microsoft/DialoGPT-small",
        "gpt2"
    ]
    
    for model_name in test_models:
        try:
            print(f"🔄 Testing {model_name}...")
            
            # Use the new router endpoint
            url = f"https://router.huggingface.co/models/{model_name}"
            headers = {"Authorization": f"Bearer {api_token}"}
            
            payload = {
                "inputs": "Hello, how are you?",
                "parameters": {
                    "max_new_tokens": 50,
                    "temperature": 0.7,
                    "return_full_text": False
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": False
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {model_name} WORKS!")
                print(f"   Response: {str(result)[:100]}...")
                return True
            elif response.status_code == 503:
                print(f"⚠️ {model_name} is loading, trying next...")
            elif response.status_code == 404:
                print(f"⚠️ {model_name} not found, trying next...")
            else:
                print(f"❌ {model_name} failed: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text[:100]}")
                    
        except Exception as e:
            print(f"❌ {model_name} error: {str(e)[:100]}...")
            continue
    
    # Try alternative approach with Inference API
    print("\n🔄 Trying alternative Hugging Face Inference API...")
    try:
        url = "https://api-inference.huggingface.co/models/gpt2"
        headers = {"Authorization": f"Bearer {api_token}"}
        payload = {"inputs": "Hello, how are you?"}
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Hugging Face Inference API WORKS!")
            print(f"   Response: {str(result)[:100]}...")
            return True
        else:
            print(f"❌ Inference API failed: HTTP {response.status_code}")
            print(f"   Error: {response.text[:100]}")
            
    except Exception as e:
        print(f"❌ Inference API error: {str(e)[:100]}...")
    
    print("❌ All Hugging Face approaches failed!")
    return False

def test_langchain_integration():
    """Test LangChain integration with both APIs"""
    print("\n🧪 TESTING LANGCHAIN INTEGRATION")
    print("=" * 30)
    
    try:
        # Test LangChain Gemini
        print("🔄 Testing LangChain + Gemini...")
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=gemini_api_key,
                temperature=0.1
            )
            response = llm.invoke("Say hello in one word")
            print(f"✅ LangChain + Gemini WORKS!")
            print(f"   Response: {response.content[:50]}...")
            return True
        else:
            print("⚠️ No Gemini API key for LangChain test")
            
    except Exception as e:
        print(f"❌ LangChain + Gemini failed: {str(e)[:100]}...")
    
    try:
        # Test LangChain Hugging Face
        print("🔄 Testing LangChain + Hugging Face...")
        from langchain_huggingface import HuggingFaceEndpoint
        
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if hf_token:
            llm = HuggingFaceEndpoint(
                repo_id="microsoft/DialoGPT-medium",
                huggingfacehub_api_token=hf_token,
                temperature=0.1,
                max_new_tokens=50
            )
            response = llm.invoke("Hello")
            print(f"✅ LangChain + Hugging Face WORKS!")
            print(f"   Response: {response[:50]}...")
            return True
        else:
            print("⚠️ No Hugging Face token for LangChain test")
            
    except Exception as e:
        print(f"❌ LangChain + Hugging Face failed: {str(e)[:100]}...")
    
    return False

def main():
    print("🚀 FIXED API KEYS & MODELS TEST")
    print("=" * 50)
    
    gemini_works = test_gemini_api()
    hf_works = test_huggingface_api()
    langchain_works = test_langchain_integration()
    
    print(f"\n🏆 RESULTS:")
    print(f"   Gemini API: {'✅ WORKING' if gemini_works else '❌ FAILED'}")
    print(f"   Hugging Face API: {'✅ WORKING' if hf_works else '❌ FAILED'}")
    print(f"   LangChain Integration: {'✅ WORKING' if langchain_works else '❌ FAILED'}")
    
    if gemini_works or hf_works or langchain_works:
        print(f"\n✅ At least one API is working - system should function!")
        
        if gemini_works and hf_works:
            print("🎉 Both APIs working - Full sequential system available!")
        elif gemini_works:
            print("📝 Only Gemini working - System will use Gemini as fallback")
        elif hf_works:
            print("📝 Only Hugging Face working - System will use HF as primary")
            
    else:
        print(f"\n❌ All APIs failed - check your API keys and internet connection!")
        print("💡 Make sure you have valid API keys in your .env file:")
        print("   - GEMINI_API_KEY=your_gemini_key")
        print("   - HUGGINGFACE_API_TOKEN=your_hf_token")

if __name__ == "__main__":
    main()