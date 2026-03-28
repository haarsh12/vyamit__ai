#!/usr/bin/env python3
"""
Verify all configuration is properly loaded
"""
import os
from dotenv import load_dotenv

# Load environment variables from the correct path
load_dotenv(dotenv_path=".env")

def verify_configuration():
    """Verify all environment variables are loaded"""
    print("🔍 Verifying Configuration...")
    print("=" * 50)
    
    # Database Configuration
    database_url = os.getenv("DATABASE_URL")
    print(f"📊 Database URL: {database_url[:50]}..." if database_url else "❌ DATABASE_URL not found")
    
    # Supabase Configuration
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    print(f"🔗 Supabase URL: {supabase_url}")
    print(f"🔑 Supabase Key: {supabase_key[:30]}..." if supabase_key else "❌ SUPABASE_KEY not found")
    
    # API Keys
    fast2sms_key = os.getenv("FAST2SMS_API_KEY")
    print(f"📱 Fast2SMS Key: {fast2sms_key[:20]}..." if fast2sms_key else "❌ FAST2SMS_API_KEY not found")
    
    # Twilio Configuration
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    print(f"📞 Twilio SID: {twilio_sid}")
    print(f"🔐 Twilio Token: {twilio_token[:20]}..." if twilio_token else "❌ TWILIO_AUTH_TOKEN not found")
    
    # Other Configuration
    secret_key = os.getenv("SECRET_KEY")
    environment = os.getenv("ENVIRONMENT")
    print(f"🔒 Secret Key: {secret_key[:20]}..." if secret_key else "❌ SECRET_KEY not found")
    print(f"🌍 Environment: {environment}")
    
    print("\n✅ Configuration verification complete!")
    
    # Check if all critical values are present
    critical_vars = [database_url, supabase_url, supabase_key, secret_key]
    if all(critical_vars):
        print("🎉 All critical configuration values are present!")
        return True
    else:
        print("⚠️  Some critical configuration values are missing!")
        return False

if __name__ == "__main__":
    verify_configuration()