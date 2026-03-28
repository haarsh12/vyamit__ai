#!/usr/bin/env python3
"""
Startup script for Vyamit AI Backend
"""
import os
import sys
import subprocess
import time

def check_virtual_env():
    """Check if we're in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def main():
    """Start the backend server"""
    print("🚀 Starting Vyamit AI Backend Server...")
    print("=" * 50)
    
    # Check virtual environment
    if check_virtual_env():
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Warning: Not in virtual environment")
        print("   Run: .\\venv\\Scripts\\Activate.ps1")
    
    # Change to app directory
    app_dir = os.path.join(os.path.dirname(__file__), "app")
    os.chdir(app_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Starting server...\n")
    
    try:
        # Start the server
        subprocess.run([
            "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())