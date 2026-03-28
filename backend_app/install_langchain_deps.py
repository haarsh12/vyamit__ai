#!/usr/bin/env python3
"""
Installation script for LangChain + Hugging Face dependencies
Run this script to install all required packages for the AI migration
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return success status"""
    try:
        print(f"🔄 Running: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Installing LangChain + Hugging Face Dependencies for Vyamit AI")
    print("=" * 60)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  WARNING: You're not in a virtual environment!")
        print("💡 It's recommended to activate your virtual environment first:")
        print("   Windows: .\\venv\\Scripts\\activate")
        print("   Linux/Mac: source venv/bin/activate")
        
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Installation cancelled.")
            return
    
    # List of packages to install
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
    
    print(f"\n📦 Installing {len(packages)} packages...")
    
    failed_packages = []
    
    for package in packages:
        if not run_command(f"pip install {package}"):
            failed_packages.append(package)
    
    print("\n" + "=" * 60)
    
    if failed_packages:
        print(f"❌ {len(failed_packages)} packages failed to install:")
        for pkg in failed_packages:
            print(f"   - {pkg}")
        print("\n💡 Try installing them manually:")
        print(f"   pip install {' '.join(failed_packages)}")
    else:
        print("✅ All packages installed successfully!")
    
    print("\n🔧 Next steps:")
    print("1. Make sure HUGGINGFACE_API_TOKEN is set in your .env file")
    print("2. Test the installation by running: python test_langchain_setup.py")
    print("3. Start your server: python start_server.py")
    
    print("\n🎉 LangChain + Hugging Face setup complete!")

if __name__ == "__main__":
    main()