from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uvicorn
import logging
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from core.config import settings
from db.database import get_db, test_database_connection, create_tables, engine
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
    logger.info("🚀 Starting Vyamit AI Backend with Database...")
    
    # Test database connection
    if test_database_connection():
        logger.info("✅ Database connection established")
        
        # Create tables
        if create_tables():
            logger.info("✅ Database tables ready")
        else:
            logger.error("❌ Failed to create tables")
    else:
        logger.error("❌ Database connection failed - continuing with limited functionality")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vyamit AI Backend with Database is running!",
        "status": "success",
        "version": "1.0.0",
        "database": "Supabase PostgreSQL (lhafpdiovrxxvxyqemtg)",
        "supabase_url": settings.SUPABASE_URL
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database test"""
    try:
        # Test database query
        result = db.execute(text("SELECT 1"))
        user_count = db.query(User).count()
        return {
            "status": "healthy",
            "message": "Backend and database operational",
            "database": "connected",
            "users_count": user_count,
            "database_test": "passed"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": "Database connection issue",
            "error": str(e),
            "database_test": "failed"
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
        
        # Test a simple query
        result = db.execute(text("SELECT version()"))
        db_version = result.fetchone()[0] if result else "Unknown"
        
        return {
            "status": "success",
            "message": "Database is working properly",
            "database_version": db_version,
            "statistics": {
                "users": user_count,
                "items": item_count,
                "bills": bill_count
            }
        }
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {
            "status": "error",
            "message": "Database test failed",
            "error": str(e)
        }

@app.get("/api/v1/users")
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    try:
        users = db.query(User).all()
        return {
            "status": "success",
            "data": [{"id": user.id, "phone": user.phone_number, "name": user.name} for user in users],
            "count": len(users)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to fetch users",
            "error": str(e)
        }

@app.get("/api/v1/items")
async def get_items(db: Session = Depends(get_db)):
    """Get all items"""
    try:
        items = db.query(Item).all()
        return {
            "status": "success",
            "data": [{"id": item.id, "name": item.name, "price": item.price, "unit": item.unit} for item in items],
            "count": len(items)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to fetch items",
            "error": str(e)
        }

@app.get("/api/v1/bills")
async def get_bills(db: Session = Depends(get_db)):
    """Get all bills"""
    try:
        bills = db.query(Bill).all()
        return {
            "status": "success",
            "data": [{"id": bill.id, "bill_number": bill.bill_number, "total": bill.final_amount} for bill in bills],
            "count": len(bills)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to fetch bills",
            "error": str(e)
        }

if __name__ == "__main__":
    logger.info("🚀 Starting Vyamit AI Backend with Database...")
    uvicorn.run(
        "main_with_db:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )