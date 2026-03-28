from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
import logging
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from core.config import settings
from db.database import get_db, test_database_connection, create_tables
from db.models import User, ShopDetails, Item, Bill

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI backend for My Kirana app with Supabase PostgreSQL",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 Starting Vyamit AI Backend...")
    
    # Test database connection
    if test_database_connection():
        logger.info("✅ Database connection established")
        
        # Create tables
        if create_tables():
            logger.info("✅ Database tables ready")
        else:
            logger.error("❌ Failed to create tables")
    else:
        logger.error("❌ Database connection failed")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vyamit AI Backend is running!",
        "status": "success",
        "database": "Supabase PostgreSQL",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database test"""
    try:
        # Test database query
        user_count = db.query(User).count()
        return {
            "status": "healthy",
            "message": "Backend is operational",
            "database": "connected",
            "users_count": user_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": "Database connection issue",
            "error": str(e)
        }

@app.get("/api/test")
async def test_endpoint():
    """Test API endpoint"""
    return {
        "message": "API is working!",
        "data": {
            "backend": "FastAPI",
            "database": "Supabase PostgreSQL",
            "version": "1.0.0",
            "status": "active"
        }
    }

@app.get("/api/database/test")
async def test_database(db: Session = Depends(get_db)):
    """Test database operations"""
    try:
        # Test basic queries
        user_count = db.query(User).count()
        item_count = db.query(Item).count()
        bill_count = db.query(Bill).count()
        
        return {
            "status": "success",
            "message": "Database is working properly",
            "statistics": {
                "users": user_count,
                "items": item_count,
                "bills": bill_count
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Database test failed",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )