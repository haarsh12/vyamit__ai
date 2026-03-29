#!/usr/bin/env python3
"""
Production Deployment Script for Render
Validates environment and prepares for deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        "requirements.txt",
        "app/main.py",
        "app/db/database.py",
        "app/services/vector_search_service.py",
        ".env.production.template"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"[ERROR] Missing required files: {missing_files}")
        return False
    
    print("[OK] All required files present")
    return True

def validate_environment():
    """Validate environment variables"""
    required_env_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "HUGGINGFACE_API_TOKEN",
        "GEMINI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[WARN] Missing environment variables: {missing_vars}")
        print("[INFO] These should be set in Render Dashboard > Environment")
        return False
    
    print("[OK] All critical environment variables present")
    return True

def test_imports():
    """Test critical imports"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import sentence_transformers
        import psycopg2
        print("[OK] All critical packages can be imported")
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("[FIX] Run: pip install -r requirements.txt")
        return False

def run_tests():
    """Run basic functionality tests"""
    try:
        # Test database models
        from app.db.models import User, Item, Bill
        print("[OK] Database models import successfully")
        
        # Test API routes
        from app.api import auth, items, voice, vector_search
        print("[OK] API routes import successfully")
        
        # Test services
        from app.services.vector_search_service import vector_search_service
        print("[OK] Vector search service imports successfully")
        
        return True
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

def create_deployment_checklist():
    """Create deployment checklist"""
    checklist = """
# Render Deployment Checklist

## Pre-deployment
- [ ] All code committed to Git repository
- [ ] Environment variables set in Render Dashboard
- [ ] Database created in Render
- [ ] Domain configured (if using custom domain)

## Environment Variables to Set in Render:
- [ ] DATABASE_URL (from Render PostgreSQL)
- [ ] SECRET_KEY (generate secure key)
- [ ] HUGGINGFACE_API_TOKEN
- [ ] XAI_GROK_API_KEY
- [ ] GEMINI_API_KEY
- [ ] SUPABASE_URL
- [ ] SUPABASE_SERVICE_KEY
- [ ] SUPABASE_ANON_KEY
- [ ] FAST2SMS_API_KEY
- [ ] TWILIO_ACCOUNT_SID
- [ ] TWILIO_AUTH_TOKEN
- [ ] TWILIO_VERIFY_SERVICE_SID
- [ ] BACKEND_CORS_ORIGINS

## Post-deployment
- [ ] Test health endpoint: https://your-app.onrender.com/health
- [ ] Test vector search: https://your-app.onrender.com/vector/health
- [ ] Run embedding setup: POST https://your-app.onrender.com/vector/embed-all
- [ ] Test API endpoints
- [ ] Monitor logs for errors

## Build Command (Render):
pip install -r requirements.txt

## Start Command (Render):
uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""
    
    with open("DEPLOYMENT_CHECKLIST.md", "w") as f:
        f.write(checklist)
    
    print("[OK] Created DEPLOYMENT_CHECKLIST.md")

def main():
    """Main deployment validation"""
    print("SnapBill Backend - Production Deployment Validation")
    print("=" * 60)
    
    checks = [
        ("Checking required files", check_requirements),
        ("Testing imports", test_imports),
        ("Running functionality tests", run_tests),
        ("Validating environment", validate_environment),
    ]
    
    all_passed = True
    for description, check_func in checks:
        print(f"\n{description}...")
        if not check_func():
            all_passed = False
    
    create_deployment_checklist()
    
    if all_passed:
        print("\n" + "=" * 60)
        print("[SUCCESS] All checks passed! Ready for Render deployment.")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Push code to Git repository")
        print("2. Create new Web Service in Render")
        print("3. Connect your Git repository")
        print("4. Set environment variables in Render Dashboard")
        print("5. Deploy!")
        return True
    else:
        print("\n" + "=" * 60)
        print("[FAILURE] Some checks failed. Fix issues before deployment.")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)