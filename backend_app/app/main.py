import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import create_db_and_tables
from app.api import auth, items, voice, voice_inventory, sms_share, analytics, vector_search

# CORS - allow frontend to call API (set FRONTEND_URL in Render for production)
ALLOWED_ORIGINS = os.getenv("FRONTEND_URL", "http://localhost:3000").split(",")
for origin in ["http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:8080"]:
    if origin not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(origin)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup: Checking database connection...")
    try:
        create_db_and_tables()
        print("[OK] Database connected successfully.")
    except Exception as e:
        print(f"[WARN] Database connection failed: {str(e)[:100]}")
        print("[WARN] Server will start but database operations will fail.")
        print("[TIP] See DATABASE_CONNECTION_FIX.md or set DATABASE_URL in the host environment.")
    
    # Initialize Vector Search Service
    print("Startup: Initializing Vector Search Service...")
    try:
        from app.services.vector_search_service import vector_search_service
        # The service will initialize itself when first accessed
        stats = vector_search_service.get_embedding_stats()
        print(f"[OK] Vector Search Service ready. Coverage: {stats['coverage_percent']:.1f}%")
        
        if stats['coverage_percent'] < 100:
            print(f"[WARN] {stats['missing_embeddings']} items need embeddings.")
            print("[TIP] Use POST /vector/embed-all to generate missing embeddings.")
        
    except Exception as e:
        print(f"[WARN] Vector Search Service initialization: {str(e)[:100]}")
        print("[WARN] Vector search may need pgvector setup or DATABASE_URL.")
        print("[TIP] Check GET /vector/health after deployment.")
    
    yield
    print("Shutdown: Closing connections...")

app = FastAPI(lifespan=lifespan, title="SnapBill API", version="1.0.0")

# CORS middleware for production (frontend on different origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(items.router, prefix="/items", tags=["Inventory"])
app.include_router(voice.router, prefix="/voice", tags=["Voice AI"])
app.include_router(voice_inventory.router, prefix="/inventory", tags=["Voice Inventory"])
app.include_router(sms_share.router, prefix="/sms", tags=["SMS Sharing"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Dashboard"])
app.include_router(vector_search.router, prefix="/vector", tags=["Vector Search & RAG"])

@app.get("/")
def root():
    return {"status": "active", "system": "SnapBill Backend"}


@app.get("/health")
def health_check():
    """Load balancer / Render health check (no DB probe — keeps checks fast)."""
    return {"status": "ok"}