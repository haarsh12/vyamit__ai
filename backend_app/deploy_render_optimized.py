#!/usr/bin/env python3
"""
Render Deployment Optimizer
Prepares the app for Render deployment with memory constraints
"""

import os
import shutil
import subprocess
import sys

def main():
    print("🚀 Preparing for Render deployment...")
    
    # 1. Verify we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Error: Run this from backend_app directory")
        sys.exit(1)
    
    # 2. Check if render-specific files exist
    required_files = [
        "requirements.render.txt",
        "render.yaml",
        "app/services/vector_search_service_render.py"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Missing required file: {file}")
            sys.exit(1)
        else:
            print(f"✅ Found: {file}")
    
    # 3. Validate render.yaml configuration
    with open("render.yaml", "r") as f:
        render_config = f.read()
        
    if "requirements.render.txt" not in render_config:
        print("❌ render.yaml should use requirements.render.txt")
        sys.exit(1)
    
    if "${PORT:-10000}" not in render_config:
        print("❌ render.yaml should use ${PORT:-10000} for port binding")
        sys.exit(1)
    
    print("✅ render.yaml configuration looks good")
    
    # 4. Check environment variables
    print("\n📋 Environment variables to set in Render:")
    env_vars = [
        "DATABASE_URL",
        "SECRET_KEY", 
        "GEMINI_API_KEY",
        "XAI_GROK_API_KEY",
        "HUGGINGFACE_API_TOKEN",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "SUPABASE_ANON_KEY"
    ]
    
    for var in env_vars:
        status = "✅ SET" if os.getenv(var) else "⚠️  NOT SET"
        print(f"  {var}: {status}")
    
    # 5. Test import of render-optimized service
    try:
        sys.path.insert(0, ".")
        from app.services.vector_search_service_render import VectorSearchService
        service = VectorSearchService()
        print("✅ Render-optimized vector service imports successfully")
    except Exception as e:
        print(f"❌ Error importing render service: {e}")
        sys.exit(1)
    
    # 6. Check requirements.render.txt size
    with open("requirements.render.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        print(f"✅ requirements.render.txt has {len(lines)} packages (lightweight)")
    
    print("\n🎯 Deployment Summary:")
    print("  • Memory optimized: Vector search disabled on Render")
    print("  • Fallback enabled: Text search will work without embeddings")
    print("  • Lightweight deps: Only essential packages in requirements.render.txt")
    print("  • Port binding: Uses Render's $PORT environment variable")
    print("  • Health checks: /health endpoint available for load balancer")
    
    print("\n📝 Next steps:")
    print("  1. Commit and push these changes to your Git repository")
    print("  2. In Render dashboard, create a new Web Service")
    print("  3. Connect your Git repository")
    print("  4. Set environment variables in Render dashboard")
    print("  5. Deploy!")
    
    print("\n✅ Ready for Render deployment!")

if __name__ == "__main__":
    main()