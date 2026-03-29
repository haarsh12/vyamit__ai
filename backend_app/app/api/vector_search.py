"""
🔍 Vector Search API Endpoints
RAG-based inventory search with multilingual support
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.services.vector_search_service import vector_search_service
import time

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 15
    similarity_threshold: Optional[float] = 0.2
    debug: Optional[bool] = False

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_matches: int
    search_time_ms: float
    debug_info: Optional[Dict[str, Any]] = None

class EmbedItemRequest(BaseModel):
    item_id: int
    names: List[str]
    category: str
    unit: str
    price: Optional[float] = 0.0

@router.post("/search", response_model=SearchResponse)
async def search_inventory(request: SearchRequest):
    """
    🔍 Search inventory using vector similarity
    
    Supports multilingual queries in Hindi, English, Hinglish, and Marathi
    """
    start_time = time.time()
    
    try:
        # Validate input
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if request.top_k < 1 or request.top_k > 50:
            raise HTTPException(status_code=400, detail="top_k must be between 1 and 50")
        
        # Perform vector search
        results = vector_search_service.search_items(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            debug=request.debug
        )
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Prepare debug info if requested
        debug_info = None
        if request.debug:
            debug_info = {
                "model": "intfloat/multilingual-e5-small",
                "embedding_dimension": 384,
                "similarity_threshold": request.similarity_threshold,
                "query_processed": f"query: {request.query}"
            }
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_matches=len(results),
            search_time_ms=round(search_time, 2),
            debug_info=debug_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/search")
async def search_inventory_get(
    q: str = Query(..., description="Search query in any language"),
    top_k: int = Query(15, ge=1, le=50, description="Number of results to return"),
    threshold: float = Query(0.2, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    debug: bool = Query(False, description="Enable debug output")
):
    """
    🔍 Search inventory using GET request (for easy testing)
    """
    request = SearchRequest(
        query=q,
        top_k=top_k,
        similarity_threshold=threshold,
        debug=debug
    )
    
    return await search_inventory(request)

@router.post("/embed-item")
async def embed_single_item(request: EmbedItemRequest):
    """
    🧠 Generate and store embedding for a single item
    """
    try:
        item_data = {
            'names': request.names,
            'category': request.category,
            'unit': request.unit,
            'price': request.price or 0.0
        }
        
        success = vector_search_service.update_item_embedding(
            item_id=request.item_id,
            item_data=item_data
        )
        
        if success:
            return {
                "success": True,
                "message": f"Embedding updated for item {request.item_id}",
                "item_data": item_data
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate or store embedding")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

@router.get("/similar/{item_id}")
async def get_similar_items(
    item_id: int,
    top_k: int = Query(5, ge=1, le=20, description="Number of similar items to return")
):
    """
    🔗 Find items similar to a given item
    """
    try:
        similar_items = vector_search_service.get_similar_items(
            item_id=item_id,
            top_k=top_k
        )
        
        return {
            "reference_item_id": item_id,
            "similar_items": similar_items,
            "total_found": len(similar_items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar items search failed: {str(e)}")

@router.get("/test-queries")
async def test_multilingual_queries():
    """
    🧪 Test the system with predefined multilingual queries
    """
    test_queries = [
        "tamatar ka rate kya hai",           # Hinglish - tomato
        "प्याज का भाव बताओ",                # Hindi - onion
        "rice ka price kitna hai",           # Hinglish - rice
        "what is wheat cost",                # English - wheat
        "चीनी का रेट क्या है",               # Hindi - sugar
        "dal moong ka bhav",                 # Hinglish - lentils
        "milk powder price",                 # English - milk powder
        "आटा कितने का है",                   # Hindi - flour
        "oil ka rate batao",                 # Hinglish - oil
        "टोमॅटो किती रुपये"                  # Marathi - tomato
    ]
    
    results = {}
    
    for query in test_queries:
        try:
            search_results = vector_search_service.search_items(
                query=query,
                top_k=5,
                similarity_threshold=0.3
            )
            
            results[query] = {
                "matches": len(search_results),
                "top_match": search_results[0] if search_results else None
            }
            
        except Exception as e:
            results[query] = {
                "error": str(e)
            }
    
    return {
        "test_results": results,
        "total_queries": len(test_queries),
        "model": "intfloat/multilingual-e5-small"
    }

@router.get("/health")
async def health_check():
    """
    ❤️ Health check for vector search service
    """
    try:
        # Test a simple search
        test_results = vector_search_service.search_items(
            query="test",
            top_k=1,
            similarity_threshold=0.0
        )
        
        return {
            "status": "healthy",
            "model": "intfloat/multilingual-e5-small",
            "embedding_dimension": 384,
            "test_search": "passed",
            "database_connection": "active"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }