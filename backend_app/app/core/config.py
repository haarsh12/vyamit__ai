from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

class Settings(BaseSettings):
    # NEW Supabase Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:VyamitAI12fgco@db.lhafpdiovrxxvxyqemtg.supabase.co:5432/postgres")
    
    # NEW Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://lhafpdiovrxxvxyqemtg.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxoYWZwZGlvdnJ4eHZ4eXFlbXRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MDgzNDEsImV4cCI6MjA5MDI4NDM0MX0.Td5ELvaDoOW3ek1yAUARTkuUrZSKOGAUSk477DzveyA")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "vyamit-ai-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # API
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Vyamit AI Backend")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

    class Config:
        case_sensitive = True

settings = Settings()