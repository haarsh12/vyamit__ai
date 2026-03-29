"""
Startup Script for Sequential Multi-LLM Orchestration System
Hackathon Demo Launcher
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking Environment Configuration...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("💡 Create .env file with required API keys")
        return False
    
    # Check required environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "HUGGINGFACE_API_TOKEN",
        "GEMINI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Add these to your .env file")
        return False
    
    print("✅ Environment configuration OK")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking Dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "langchain",
        "langchain-huggingface",
        "langchain-google-genai",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ Dependencies OK")
    return True

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Sequential Multi-LLM System...")
    print("=" * 60)
    
    try:
        # Start uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        print("🌐 Server starting at: http://localhost:8000")
        print("📋 API Documentation: http://localhost:8000/docs")
        print("🔗 Sequential LLM API: http://localhost:8000/sequential-llm")
        print("=" * 60)
        print("🎯 Ready for Hackathon Demo!")
        print("=" * 60)
        
        # Start the server
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {str(e)}")

def run_quick_test():
    """Run a quick test to verify system works"""
    print("🧪 Running Quick System Test...")
    
    try:
        # Import and test the service
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        from app.services.sequential_multi_llm_service import SequentialMultiLLMService
        
        # Initialize service
        service = SequentialMultiLLMService()
        print("✅ Service initialized successfully")
        
        # Test a simple query
        import asyncio
        
        async def test_query():
            result = await service.process_query("Hello, test query")
            return result['success']
        
        success = asyncio.run(test_query())
        
        if success:
            print("✅ Quick test passed - System ready!")
            return True
        else:
            print("⚠️  Quick test failed - Check configuration")
            return False
            
    except Exception as e:
        print(f"❌ Quick test error: {str(e)}")
        return False

def main():
    """Main startup sequence"""
    print("🚀 SEQUENTIAL MULTI-LLM ORCHESTRATION SYSTEM")
    print("🏆 Hackathon Demo Launcher")
    print("=" * 60)
    
    # Step 1: Check environment
    if not check_environment():
        print("\n🔧 Fix environment issues and try again")
        return
    
    # Step 2: Check dependencies
    if not check_dependencies():
        print("\n🔧 Install missing dependencies and try again")
        return
    
    # Step 3: Run quick test
    print("\n🧪 Testing System...")
    if not run_quick_test():
        print("\n⚠️  System test failed - Check logs for details")
        choice = input("Continue anyway? (y/n): ").strip().lower()
        if choice != 'y':
            return
    
    # Step 4: Start server
    print("\n🚀 All checks passed - Starting server...")
    time.sleep(2)
    start_server()

if __name__ == "__main__":
    main()