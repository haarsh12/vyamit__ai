#!/usr/bin/env python3
"""
Test script for LangChain + Hugging Face setup
Run this to verify everything is working correctly
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Variables...")
    
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not hf_token:
        print("❌ HUGGINGFACE_API_TOKEN not found in .env file")
        return False
    elif hf_token.startswith("hf_"):
        print("✅ HUGGINGFACE_API_TOKEN found and looks valid")
        return True
    else:
        print("⚠️  HUGGINGFACE_API_TOKEN found but doesn't start with 'hf_'")
        return False

def test_imports():
    """Test if all required packages can be imported"""
    print("\n📦 Testing Package Imports...")
    
    packages = [
        ("langchain", "LangChain core"),
        ("langchain_huggingface", "LangChain Hugging Face integration"),
        ("langchain_community", "LangChain community packages"),
        ("transformers", "Hugging Face Transformers"),
        ("sentence_transformers", "Sentence Transformers"),
        ("torch", "PyTorch"),
        ("huggingface_hub", "Hugging Face Hub")
    ]
    
    failed_imports = []
    
    for package, description in packages:
        try:
            __import__(package)
            print(f"✅ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_ai_service():
    """Test the AI service initialization"""
    print("\n🤖 Testing AI Service...")
    
    try:
        # Add the app directory to Python path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        from app.services.ai_service_langchain import LangChainAIService
        
        print("🔄 Initializing LangChain AI Service...")
        service = LangChainAIService()
        print("✅ AI Service initialized successfully!")
        
        # Test embeddings
        print("🔄 Testing embeddings...")
        test_texts = ["rice", "wheat", "sugar"]
        embeddings = service.get_embeddings(test_texts)
        if embeddings:
            print(f"✅ Embeddings generated for {len(test_texts)} texts")
        else:
            print("⚠️  Embeddings test failed")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Service test failed: {e}")
        return False

def test_model_connection():
    """Test connection to Hugging Face model"""
    print("\n🌐 Testing Model Connection...")
    
    try:
        from langchain_huggingface import HuggingFaceEndpoint
        
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token
        
        print("🔄 Connecting to google/gemma-2-27b-it...")
        
        llm = HuggingFaceEndpoint(
            repo_id="google/gemma-2-27b-it",
            task="text-generation",
            max_new_tokens=50,
            temperature=0.3,
            huggingfacehub_api_token=hf_token
        )
        
        # Test with a simple prompt
        test_prompt = "Hello, my name is"
        print(f"🔄 Testing with prompt: '{test_prompt}'")
        
        response = llm.invoke(test_prompt)
        print(f"✅ Model response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Model connection test failed: {e}")
        print("💡 This might be due to:")
        print("   - Invalid API token")
        print("   - Network connectivity issues")
        print("   - Hugging Face API rate limits")
        return False

def main():
    print("🧪 LangChain + Hugging Face Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Package Imports", test_imports),
        ("AI Service", test_ai_service),
        ("Model Connection", test_model_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your LangChain + Hugging Face setup is ready!")
        print("\n🚀 You can now:")
        print("   - Start your server: python start_server.py")
        print("   - Test voice endpoints with the new AI service")
        print("   - Use chat history features")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 Common solutions:")
        print("   - Run: pip install -r requirements.txt")
        print("   - Check your HUGGINGFACE_API_TOKEN in .env")
        print("   - Ensure you have internet connectivity")

if __name__ == "__main__":
    main()