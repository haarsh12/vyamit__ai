#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
"""

def test_imports():
    print("=== Testing Critical Imports ===")
    
    # Test LangChain imports
    try:
        from langchain.memory import ConversationBufferMemory
        from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
        from langchain_huggingface import HuggingFaceEndpoint
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ LangChain imports successful")
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False
    
    # Test Google GenAI import
    try:
        import google.generativeai as genai
        print("✅ Google GenerativeAI import successful")
    except ImportError as e:
        print(f"❌ Google GenerativeAI import failed: {e}")
        return False
    
    # Test FastAPI imports
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        print("✅ FastAPI imports successful")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    # Test app imports
    try:
        from app.db.database import create_db_and_tables
        from app.api import auth, items, voice, voice_inventory, sms_share, analytics, sequential_llm
        print("✅ App module imports successful")
    except ImportError as e:
        print(f"❌ App module import failed: {e}")
        return False
    
    print("\n🎉 All imports working correctly!")
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ Server should start without import errors")
        print("Run: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("\n❌ Fix the import errors before starting the server")