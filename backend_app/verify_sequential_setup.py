"""
Verification Script for Sequential Multi-LLM System
Quick setup verification for hackathon demo
"""

import os
import sys
from pathlib import Path
import json

def verify_environment():
    """Verify environment configuration"""
    print("🔍 VERIFYING ENVIRONMENT SETUP")
    print("=" * 50)
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("❌ .env file missing")
        return False
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        "HUGGINGFACE_API_TOKEN": "Hugging Face API access",
        "GEMINI_API_KEY": "Google Gemini API access"
    }
    
    all_good = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask the key for security
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {var}: {masked} ({description})")
        else:
            print(f"❌ {var}: Missing ({description})")
            all_good = False
    
    return all_good

def verify_dependencies():
    """Verify required packages are installed"""
    print("\n🔍 VERIFYING DEPENDENCIES")
    print("=" * 50)
    
    dependencies = {
        "fastapi": "Web framework",
        "uvicorn": "ASGI server",
        "langchain": "LLM framework",
        "langchain_huggingface": "Hugging Face integration",
        "langchain_google_genai": "Google Gemini integration",
        "python-dotenv": "Environment variables",
        "requests": "HTTP client",
        "pydantic": "Data validation"
    }
    
    all_good = True
    
    for package, description in dependencies.items():
        try:
            module_name = package.replace("-", "_")
            __import__(module_name)
            print(f"✅ {package}: Installed ({description})")
        except ImportError:
            print(f"❌ {package}: Missing ({description})")
            all_good = False
    
    return all_good

def verify_service_initialization():
    """Verify the service can be initialized"""
    print("\n🔍 VERIFYING SERVICE INITIALIZATION")
    print("=" * 50)
    
    try:
        # Add app to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        # Try to import the service
        from app.services.sequential_multi_llm_service import SequentialMultiLLMService
        print("✅ Service module imported successfully")
        
        # Try to initialize (this will test API keys)
        print("🔄 Initializing service (testing API connections)...")
        service = SequentialMultiLLMService()
        print("✅ Service initialized successfully")
        
        # Check models are loaded
        if hasattr(service, 'models') and service.models:
            print(f"✅ Models loaded: {len(service.models)} models")
            for name, _ in service.models:
                print(f"   📋 {name}: Ready")
        else:
            print("⚠️  Models not properly loaded")
            return False
        
        # Check memory system
        if hasattr(service, 'memory') and service.memory:
            print("✅ Memory system initialized")
        else:
            print("⚠️  Memory system not initialized")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {str(e)}")
        return False

def verify_api_structure():
    """Verify API files are in place"""
    print("\n🔍 VERIFYING API STRUCTURE")
    print("=" * 50)
    
    required_files = {
        "app/main.py": "Main FastAPI application",
        "app/services/sequential_multi_llm_service.py": "Sequential LLM service",
        "app/api/sequential_llm.py": "Sequential LLM API endpoints",
        "requirements.txt": "Python dependencies",
        "test_sequential_llm_hackathon.py": "Hackathon demo script",
        "test_sequential_api.py": "API test script"
    }
    
    all_good = True
    
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path}: Found ({description})")
        else:
            print(f"❌ {file_path}: Missing ({description})")
            all_good = False
    
    return all_good

def run_quick_functionality_test():
    """Run a quick functionality test"""
    print("\n🔍 RUNNING QUICK FUNCTIONALITY TEST")
    print("=" * 50)
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        from app.services.sequential_multi_llm_service import SequentialMultiLLMService
        import asyncio
        
        async def test_query():
            service = SequentialMultiLLMService()
            
            # Test a simple query
            print("🧪 Testing query: 'Hello, this is a test'")
            result = await service.process_query("Hello, this is a test")
            
            if result['success']:
                print(f"✅ Query processed successfully")
                print(f"   Model used: {result['model_used']}")
                print(f"   Execution time: {result['execution_time']:.3f}s")
                print(f"   Response length: {len(result['response'])} chars")
                return True
            else:
                print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
                return False
        
        success = asyncio.run(test_query())
        return success
        
    except Exception as e:
        print(f"❌ Functionality test failed: {str(e)}")
        return False

def generate_setup_report():
    """Generate a comprehensive setup report"""
    print("\n📊 GENERATING SETUP REPORT")
    print("=" * 50)
    
    checks = [
        ("Environment Variables", verify_environment),
        ("Dependencies", verify_dependencies),
        ("API Structure", verify_api_structure),
        ("Service Initialization", verify_service_initialization),
        ("Functionality Test", run_quick_functionality_test)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}...")
        try:
            result = check_func()
            results[check_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}")
        except Exception as e:
            results[check_name] = False
            print(f"   ❌ ERROR: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SETUP VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    for check_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {check_name}: {status}")
    
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate == 100:
        print("\n🎉 SYSTEM READY FOR HACKATHON!")
        print("🚀 Run: python start_sequential_system.py")
        print("🧪 Test: python test_sequential_llm_hackathon.py")
    elif success_rate >= 80:
        print("\n⚠️  MOSTLY READY - Minor issues detected")
        print("🔧 Fix remaining issues for optimal performance")
    else:
        print("\n❌ SETUP INCOMPLETE - Major issues detected")
        print("🔧 Fix critical issues before proceeding")
    
    return success_rate >= 80

def main():
    """Main verification process"""
    print("🔍 SEQUENTIAL MULTI-LLM SYSTEM VERIFICATION")
    print("🏆 Hackathon Setup Checker")
    print("=" * 60)
    
    success = generate_setup_report()
    
    if success:
        print("\n✅ Verification completed successfully!")
        
        # Offer to run demo
        choice = input("\n🎤 Run hackathon demo now? (y/n): ").strip().lower()
        if choice == 'y':
            print("\n🚀 Starting hackathon demo...")
            os.system("python test_sequential_llm_hackathon.py")
    else:
        print("\n🔧 Please fix the issues above and run verification again")

if __name__ == "__main__":
    main()