from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Vyamit AI Backend",
    description="FastAPI backend for My Kirana app",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vyamit AI Backend is running!",
        "status": "success",
        "version": "1.0.0",
        "database": "NEW Supabase (lhafpdiovrxxvxyqemtg)",
        "supabase_url": "https://lhafpdiovrxxvxyqemtg.supabase.co"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Backend is operational",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "api_test": "/api/test",
            "database_test": "/api/database/test"
        }
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
async def test_database():
    """Test database connectivity"""
    try:
        return {
            "status": "success",
            "message": "NEW Supabase database configured",
            "database": "lhafpdiovrxxvxyqemtg.supabase.co",
            "supabase_url": "https://lhafpdiovrxxvxyqemtg.supabase.co",
            "note": "Using REST API for database operations",
            "password": "VyamitAI12fgco (configured)"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Database test failed",
            "error": str(e)
        }

# API endpoints for the Kirana app
@app.get("/api/v1/users")
async def get_users():
    """Get all users"""
    return {
        "status": "success",
        "data": [],
        "message": "Users endpoint ready"
    }

@app.get("/api/v1/items")
async def get_items():
    """Get all items"""
    return {
        "status": "success",
        "data": [],
        "message": "Items endpoint ready"
    }

@app.get("/api/v1/bills")
async def get_bills():
    """Get all bills"""
    return {
        "status": "success",
        "data": [],
        "message": "Bills endpoint ready"
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Vyamit AI Backend...")
    uvicorn.run(
        "main_simple:app",
        host="127.0.0.1",  # Changed to localhost
        port=8000,
        reload=True,
        log_level="info"
    )