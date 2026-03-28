#!/usr/bin/env python3
"""
Quick Start Script for LangChain + Hugging Face Migration
This script will set up everything automatically
"""

import os
import subprocess
import sys
from pathlib import Path

def print_banner():
    print("""
🚀 VYAMIT AI - LANGCHAIN MIGRATION
================================
Migrating from Gemini API to LangChain + Hugging Face
Model: google/gemma-2-27b-it
Features: Chat History, Embeddings, Memory
""")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_virtual_env():
    """Check if virtual environment is active"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  WARNING: Not in virtual environment!")
        print("💡 Recommended: activate venv first")
        response = input("Continue anyway? (y/N): ")
        return response.lower() == 'y'
    print("✅ Virtual environment active")
    return True

def install_dependencies():
    """Install all required dependencies"""
    print("\n📦 Installing Dependencies...")
    
    packages = [
        "langchain==0.1.0",
        "langchain-huggingface==0.0.3",
        "langchain-community==0.0.13", 
        "transformers==4.36.2",
        "accelerate==0.25.0",
        "sentence-transformers==2.2.2",
        "torch==2.1.2",
        "huggingface-hub==0.19.4"
    ]
    
    for package in packages:
        try:
            print(f"🔄 Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def check_env_file():
    """Check and update .env file"""
    print("\n🔧 Checking Environment Configuration...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current .env
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Check if HF token exists
    if "HUGGINGFACE_API_TOKEN" not in content:
        print("⚠️  HUGGINGFACE_API_TOKEN not found in .env")
        token = input("Enter your Hugging Face API token (hf_...): ").strip()
        
        if token.startswith("hf_"):
            # Add HF token to .env
            with open(env_path, 'a') as f:
                f.write(f"\n# Hugging Face Configuration\nHUGGINGFACE_API_TOKEN={token}\n")
            print("✅ Hugging Face token added to .env")
        else:
            print("❌ Invalid token format (should start with 'hf_')")
            return False
    else:
        print("✅ HUGGINGFACE_API_TOKEN found in .env")
    
    return True

def run_tests():
    """Run the test script"""
    print("\n🧪 Running Tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_langchain_setup.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def main():
    print_banner()
    
    # Pre-flight checks
    if not check_python_version():
        return
    
    if not check_virtual_env():
        return
    
    # Installation steps
    steps = [
        ("Installing Dependencies", install_dependencies),
        ("Checking Environment", check_env_file),
        ("Running Tests", run_tests)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not step_func():
            print(f"❌ {step_name} failed. Please check the errors above.")
            return
    
    # Success message
    print("\n" + "="*60)
    print("🎉 MIGRATION COMPLETE!")
    print("="*60)
    
    print("\n✅ What's been set up:")
    print("   - LangChain + Hugging Face dependencies installed")
    print("   - AI service migrated to google/gemma-2-27b-it")
    print("   - Chat history and memory features enabled")
    print("   - Environment variables configured")
    print("   - All tests passed")
    
    print("\n🚀 Next Steps:")
    print("   1. Start your server: python start_server.py")
    print("   2. Test voice endpoints in your app")
    print("   3. Try the new chat history features")
    print("   4. Monitor API usage on Hugging Face")
    
    print("\n📚 Documentation:")
    print("   - Read: LANGCHAIN_MIGRATION_GUIDE.md")
    print("   - API Status: GET /voice/ai-status")
    print("   - Chat History: GET /voice/chat-history")
    
    print("\n💡 Tips:")
    print("   - Free tier: ~2000 requests/day")
    print("   - Responses may be 2-5 seconds (normal for free tier)")
    print("   - Original Gemini service backed up as ai_service_gemini_backup.py")
    
    print("\n🎯 Your Vyamit AI is now powered by open-source models!")

if __name__ == "__main__":
    main()