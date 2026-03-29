"""
Vector Search Service - Render Optimized (Memory Efficient)
Lazy loading to avoid OOM on Render free tier
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text

class VectorSearchService:
    _instance = None
    _model = None
    _engine = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorSearchService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize()
    
    def _initialize(self):
        """Initialize the service - Memory optimized for Render"""
        print("[INFO] Initializing Vector Search Service (Render Optimized)...")
        
        try:
            # Database connection
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                print("[WARN] DATABASE_URL not found - vector search disabled")
                self._initialized = True
                return
                
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            
            self._engine = create_engine(database_url, pool_pre_ping=True, pool_recycle=300)
            print("[OK] Database connection established")
            
            # Test basic connection only
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("[OK] Database connection verified")
            
            # Don't load model during startup - save memory
            print("[OK] Vector Search Service initialized (lazy loading enabled)")
            self._initialized = True
            
        except Exception as e:
            print(f"[WARN] Vector Search Service initialization: {str(e)}")
            self._initialized = True  # Don't fail startup
    
    def _ensure_model_loaded(self):
        """Load model only when needed (lazy loading) - Skip on Render to save memory"""
        # Skip model loading on Render to avoid OOM
        if os.getenv("RENDER") or os.getenv("PORT"):
            print("[INFO] Render deployment detected - vector search disabled to save memory")
            print("[INFO] Using fallback text search instead")
            return False
            
        if self._model is None:
            try:
                print("[INFO] Loading embedding model on demand...")
                # Check if sentence-transformers is available
                try:
                    from sentence_transformers import SentenceTransformer
                except ImportError:
                    print("[WARN] sentence-transformers not available - using fallback search")
                    return False
                    
                self._model = SentenceTransformer("intfloat/multilingual-e5-small")
                print("[OK] Model loaded successfully")
            except Exception as e:
                print(f"[ERROR] Failed to load model: {e}")
                return False
        return True
    
    def search_items(
        self, 
        query: str, 
        top_k: int = 15, 
        similarity_threshold: float = 0.1,
        debug: bool = False
    ) -> List[Dict[str, Any]]:
        """Search inventory items - with fallback if model unavailable"""
        
        if not self._engine:
            return []
        
        # Try to load model if not loaded
        if not self._ensure_model_loaded():
            # Fallback to basic text search
            return self._fallback_text_search(query, top_k)
        
        try:
            # Generate query embedding
            query_text = f"query: {query}"
            query_embedding = self._model.encode(query_text, normalize_embeddings=True)
            
            # Search database
            with self._engine.connect() as conn:
                embedding_str = '[' + ','.join(map(str, query_embedding.tolist())) + ']'
                
                result = conn.execute(text(f"""
                    SELECT 
                        item.id,
                        item.master_id,
                        item.names,
                        item.category,
                        item.price,
                        item.unit,
                        1 - (item.embedding <=> '{embedding_str}'::vector) as similarity
                    FROM item
                    WHERE item.embedding IS NOT NULL
                        AND 1 - (item.embedding <=> '{embedding_str}'::vector) > {similarity_threshold}
                    ORDER BY item.embedding <=> '{embedding_str}'::vector
                    LIMIT {top_k}
                """))
                
                matches = result.fetchall()
                return self._format_results(matches)
                
        except Exception as e:
            print(f"[WARN] Vector search failed, using fallback: {e}")
            return self._fallback_text_search(query, top_k)
    
    def _fallback_text_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback text search when vector search unavailable"""
        try:
            with self._engine.connect() as conn:
                # Simple text search using ILIKE
                result = conn.execute(text("""
                    SELECT 
                        item.id,
                        item.master_id,
                        item.names,
                        item.category,
                        item.price,
                        item.unit,
                        0.5 as similarity
                    FROM item
                    WHERE item.names ILIKE :query
                       OR item.category ILIKE :query
                    ORDER BY item.id
                    LIMIT :limit
                """), {
                    "query": f"%{query}%",
                    "limit": top_k
                })
                
                matches = result.fetchall()
                return self._format_results(matches)
                
        except Exception as e:
            print(f"[ERROR] Fallback search failed: {e}")
            return []
    
    def _format_results(self, matches) -> List[Dict[str, Any]]:
        """Format database results"""
        results = []
        for i, match in enumerate(matches):
            try:
                if match.names:
                    try:
                        names_list = json.loads(match.names) if isinstance(match.names, str) and match.names.startswith('[') else [match.names]
                    except json.JSONDecodeError:
                        names_list = [match.names]
                else:
                    names_list = ["Unknown"]
                
                result_dict = {
                    'id': match.id,
                    'master_id': match.master_id,
                    'names': names_list,
                    'primary_name': names_list[0] if names_list else "Unknown",
                    'category': match.category,
                    'price': float(match.price) if match.price else 0.0,
                    'unit': match.unit,
                    'similarity': float(match.similarity),
                    'confidence': self._get_confidence_level(match.similarity),
                    'rank': i + 1
                }
                
                results.append(result_dict)
                
            except Exception as e:
                print(f"[WARN] Error processing match {i}: {str(e)}")
                continue
        
        return results
    
    def _get_confidence_level(self, similarity: float) -> str:
        """Convert similarity score to confidence level"""
        if similarity >= 0.8:
            return "high"
        elif similarity >= 0.6:
            return "medium"
        elif similarity >= 0.4:
            return "low"
        else:
            return "very_low"
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get current embedding statistics"""
        if not self._engine:
            return {
                'total_items': 0,
                'items_with_embeddings': 0,
                'coverage_percent': 0,
                'missing_embeddings': 0,
                'error': 'Database not available'
            }
        
        try:
            with self._engine.connect() as conn:
                # Total items
                result = conn.execute(text("SELECT COUNT(*) as count FROM item"))
                total_items = result.fetchone().count
                
                # Items with embeddings
                result = conn.execute(text("SELECT COUNT(*) as count FROM item WHERE embedding IS NOT NULL"))
                items_with_embeddings = result.fetchone().count
                
                coverage = (items_with_embeddings / total_items * 100) if total_items > 0 else 0
                
                return {
                    'total_items': total_items,
                    'items_with_embeddings': items_with_embeddings,
                    'coverage_percent': round(coverage, 2),
                    'missing_embeddings': total_items - items_with_embeddings
                }
                
        except Exception as e:
            return {
                'total_items': 0,
                'items_with_embeddings': 0,
                'coverage_percent': 0,
                'missing_embeddings': 0,
                'error': str(e)
            }
    
    def embed_item(self, item_data: Dict[str, Any]) -> Optional[List[float]]:
        """Generate embedding for a single item - Returns None on Render"""
        # Skip embedding generation on Render
        if os.getenv("RENDER") or os.getenv("PORT"):
            print("[INFO] Embedding generation skipped on Render deployment")
            return None
            
        if not self._ensure_model_loaded():
            return None
        
        try:
            # Create embedding text
            names_list = item_data.get('names', [])
            if isinstance(names_list, str):
                try:
                    names_list = json.loads(names_list) if names_list.startswith('[') else [names_list]
                except json.JSONDecodeError:
                    names_list = [names_list]
            
            text_parts = [
                f"passage: {' '.join(names_list)}",
                f"category: {item_data.get('category', '')}",
                f"unit: {item_data.get('unit', '')}"
            ]
            
            price = item_data.get('price', 0)
            if price and price > 0:
                text_parts.append(f"price: ₹{price}")
            
            embedding_text = " | ".join(text_parts)
            embedding = self._model.encode(embedding_text, normalize_embeddings=True)
            return embedding.tolist()
            
        except Exception as e:
            print(f"[ERROR] Embedding generation error: {str(e)}")
            return None
    
    def update_item_embedding(self, item_id: int, item_data: Dict[str, Any]) -> bool:
        """Update embedding for a specific item"""
        if not self._engine:
            return False
        
        embedding = self.embed_item(item_data)
        if embedding is None:
            return False
        
        try:
            with self._engine.connect() as conn:
                conn.execute(text("""
                    UPDATE item 
                    SET embedding = :embedding 
                    WHERE id = :id
                """), {
                    "embedding": embedding,
                    "id": item_id
                })
                conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Update embedding error: {str(e)}")
            return False

# Global instance - Memory optimized for Render
vector_search_service = VectorSearchService()