"""
🔍 Vector Search Service
Integration service for RAG-based inventory search
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
import numpy as np

class VectorSearchService:
    _instance = None
    _model = None
    _engine = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorSearchService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._initialize()
    
    def _initialize(self):
        """Initialize the service (singleton pattern)"""
        print("🚀 Initializing Vector Search Service...")
        
        # Database connection
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        self._engine = create_engine(database_url)
        
        # Load embedding model
        print("📦 Loading multilingual embedding model...")
        start_time = time.time()
        self._model = SentenceTransformer("intfloat/multilingual-e5-small")
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f}s")
    
    def search_items(
        self, 
        query: str, 
        top_k: int = 15, 
        similarity_threshold: float = 0.2,
        debug: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search inventory items using vector similarity
        
        Args:
            query: Search query in any language
            top_k: Number of top matches to return
            similarity_threshold: Minimum similarity score
            debug: Enable debug output
            
        Returns:
            List of matching items with similarity scores
        """
        if debug:
            print(f"🔍 Vector search: '{query}' (top {top_k})")
        
        try:
            # Generate query embedding
            query_text = f"query: {query}"
            query_embedding = self._model.encode(query_text, normalize_embeddings=True)
            
            if debug:
                print(f"🧠 Query embedded: {query_embedding.shape}")
            
            # Search database
            with self._engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM match_items(:embedding, :count, :threshold)
                """), {
                    "embedding": query_embedding.tolist(),
                    "count": top_k,
                    "threshold": similarity_threshold
                })
                
                matches = result.fetchall()
                
                # Convert to structured format
                results = []
                for match in matches:
                    names_list = json.loads(match.names) if isinstance(match.names, str) else [match.names]
                    
                    result_dict = {
                        'id': match.id,
                        'master_id': match.master_id,
                        'names': names_list,
                        'primary_name': names_list[0] if names_list else "Unknown",
                        'category': match.category,
                        'price': match.price,
                        'unit': match.unit,
                        'similarity': float(match.similarity),
                        'confidence': self._get_confidence_level(match.similarity)
                    }
                    
                    results.append(result_dict)
                
                if debug:
                    print(f"📊 Found {len(results)} matches")
                    for i, r in enumerate(results[:5], 1):
                        print(f"   {i}. {r['primary_name']} ({r['similarity']:.3f})")
                
                return results
                
        except Exception as e:
            print(f"❌ Vector search error: {str(e)}")
            return []
    
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
    
    def embed_item(self, item_data: Dict[str, Any]) -> Optional[List[float]]:
        """
        Generate embedding for a single item
        
        Args:
            item_data: Dictionary with item information
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            # Create embedding text
            names_list = item_data.get('names', [])
            if isinstance(names_list, str):
                names_list = json.loads(names_list)
            
            text_parts = [
                f"passage: {' '.join(names_list)}",
                f"category: {item_data.get('category', '')}",
                f"unit: {item_data.get('unit', '')}"
            ]
            
            if item_data.get('price', 0) > 0:
                text_parts.append(f"price: ₹{item_data['price']}")
            
            embedding_text = " | ".join(text_parts)
            
            # Generate embedding
            embedding = self._model.encode(embedding_text, normalize_embeddings=True)
            return embedding.tolist()
            
        except Exception as e:
            print(f"❌ Embedding error: {str(e)}")
            return None
    
    def update_item_embedding(self, item_id: int, item_data: Dict[str, Any]) -> bool:
        """
        Update embedding for a specific item
        
        Args:
            item_id: Item ID to update
            item_data: Item data for embedding generation
            
        Returns:
            Success status
        """
        try:
            embedding = self.embed_item(item_data)
            if embedding is None:
                return False
            
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
            print(f"❌ Update embedding error: {str(e)}")
            return False
    
    def get_similar_items(self, item_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find items similar to a given item
        
        Args:
            item_id: Reference item ID
            top_k: Number of similar items to return
            
        Returns:
            List of similar items
        """
        try:
            with self._engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM find_similar_items(:item_id, :count)
                """), {
                    "item_id": item_id,
                    "count": top_k
                })
                
                matches = result.fetchall()
                
                results = []
                for match in matches:
                    names_list = json.loads(match.names) if isinstance(match.names, str) else [match.names]
                    
                    result_dict = {
                        'id': match.id,
                        'master_id': match.master_id,
                        'names': names_list,
                        'primary_name': names_list[0] if names_list else "Unknown",
                        'similarity': float(match.similarity)
                    }
                    
                    results.append(result_dict)
                
                return results
                
        except Exception as e:
            print(f"❌ Similar items error: {str(e)}")
            return []

# Global instance
vector_search_service = VectorSearchService()