#!/usr/bin/env python3
"""
🚀 COMPLETE VECTOR RAG SYSTEM
Supabase + intfloat/multilingual-e5-small + Full Debug
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

class VectorRAGSystem:
    def __init__(self):
        """Initialize the Vector RAG System"""
        print("🚀 Initializing Vector RAG System...")
        print("=" * 60)
        
        # Database connection
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("❌ DATABASE_URL not found in environment variables")
        
        print(f"🔗 Database URL: {self.database_url[:50]}...")
        
        # Initialize database engine
        self.engine = create_engine(self.database_url)
        print("✅ Database connection initialized")
        
        # Initialize embedding model
        print("📦 Loading intfloat/multilingual-e5-small model...")
        start_time = time.time()
        self.model = SentenceTransformer("intfloat/multilingual-e5-small")
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        print(f"📊 Model embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        
        print("🎉 Vector RAG System initialized successfully!")
        print("=" * 60)
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get current embedding statistics from database"""
        print("\n📊 Getting embedding statistics...")
        
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM get_embedding_stats()"))
            stats = result.fetchone()
            
            stats_dict = {
                'total_items': stats.total_items,
                'items_with_embeddings': stats.items_with_embeddings,
                'coverage_percent': float(stats.embedding_coverage_percent)
            }
            
            print(f"   📦 Total items: {stats_dict['total_items']}")
            print(f"   🧠 Items with embeddings: {stats_dict['items_with_embeddings']}")
            print(f"   📈 Coverage: {stats_dict['coverage_percent']:.1f}%")
            
            return stats_dict
    
    def create_embedding_text(self, item_data: Dict[str, Any]) -> str:
        """Create optimized text for embedding generation"""
        names_list = json.loads(item_data['names']) if isinstance(item_data['names'], str) else item_data['names']
        
        # Create rich text with all names and metadata
        text_parts = [
            f"passage: {' '.join(names_list)}",  # All names
            f"category: {item_data['category']}",
            f"unit: {item_data['unit']}"
        ]
        
        # Add price if available
        if item_data.get('price') and item_data['price'] > 0:
            text_parts.append(f"price: ₹{item_data['price']}")
        
        return " | ".join(text_parts)
    
    def embed_all_inventory(self, batch_size: int = 50) -> bool:
        """Embed all inventory items in batches with full debug output"""
        print("\n🚀 EMBEDDING ALL INVENTORY ITEMS")
        print("=" * 50)
        
        try:
            with self.engine.connect() as conn:
                # Get all items without embeddings
                result = conn.execute(text("""
                    SELECT id, master_id, names, category, price, unit 
                    FROM item 
                    WHERE embedding IS NULL
                    ORDER BY id
                """))
                
                items = result.fetchall()
                total_items = len(items)
                
                if total_items == 0:
                    print("✅ All items already have embeddings!")
                    return True
                
                print(f"📦 Found {total_items} items to embed")
                print(f"🔄 Processing in batches of {batch_size}")
                
                # Process in batches
                for i in range(0, total_items, batch_size):
                    batch = items[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    total_batches = (total_items + batch_size - 1) // batch_size
                    
                    print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} items)")
                    
                    # Prepare texts for embedding
                    texts = []
                    item_ids = []
                    
                    for item in batch:
                        item_dict = {
                            'names': item.names,
                            'category': item.category,
                            'price': item.price,
                            'unit': item.unit
                        }
                        
                        embedding_text = self.create_embedding_text(item_dict)
                        texts.append(embedding_text)
                        item_ids.append(item.id)
                        
                        print(f"   📝 Item {item.id}: {embedding_text[:80]}...")
                    
                    # Generate embeddings
                    print(f"   🧠 Generating {len(texts)} embeddings...")
                    start_time = time.time()
                    embeddings = self.model.encode(texts, normalize_embeddings=True)
                    embed_time = time.time() - start_time
                    
                    print(f"   ⚡ Generated in {embed_time:.2f}s ({len(texts)/embed_time:.1f} items/sec)")
                    
                    # Update database
                    print(f"   💾 Saving embeddings to database...")
                    for item_id, embedding in zip(item_ids, embeddings):
                        embedding_list = embedding.tolist()
                        conn.execute(text("""
                            UPDATE item 
                            SET embedding = :embedding 
                            WHERE id = :id
                        """), {
                            "embedding": embedding_list,
                            "id": item_id
                        })
                    
                    conn.commit()
                    print(f"   ✅ Batch {batch_num} completed")
                
                print(f"\n🎉 Successfully embedded {total_items} items!")
                return True
                
        except Exception as e:
            print(f"❌ Error during embedding: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def search_inventory(self, query: str, top_k: int = 15, similarity_threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Search inventory using vector similarity with full debug output"""
        print(f"\n🔍 SEARCHING INVENTORY")
        print("=" * 40)
        print(f"❓ Query: '{query}'")
        print(f"🎯 Requesting top {top_k} matches")
        print(f"📊 Similarity threshold: {similarity_threshold}")
        
        # Generate query embedding
        query_text = f"query: {query}"
        print(f"🧠 Embedding text: '{query_text}'")
        
        start_time = time.time()
        query_embedding = self.model.encode(query_text, normalize_embeddings=True)
        embed_time = time.time() - start_time
        
        print(f"⚡ Query embedded in {embed_time:.3f}s")
        print(f"📏 Query embedding shape: {query_embedding.shape}")
        print(f"🔢 First 5 values: {query_embedding[:5].round(4)}")
        
        # Search database
        print(f"\n🔍 Searching database...")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM match_items(:embedding, :count, :threshold)
                """), {
                    "embedding": query_embedding.tolist(),
                    "count": top_k,
                    "threshold": similarity_threshold
                })
                
                matches = result.fetchall()
                
                print(f"📊 Found {len(matches)} matches above threshold {similarity_threshold}")
                
                # Convert to list of dictionaries with debug info
                results = []
                for i, match in enumerate(matches):
                    names_list = json.loads(match.names) if isinstance(match.names, str) else [match.names]
                    
                    result_dict = {
                        'id': match.id,
                        'master_id': match.master_id,
                        'names': names_list,
                        'primary_name': names_list[0] if names_list else "Unknown",
                        'category': match.category,
                        'price': match.price,
                        'unit': match.unit,
                        'similarity': float(match.similarity)
                    }
                    
                    results.append(result_dict)
                    
                    # Debug output
                    similarity_status = "🟢" if match.similarity > 0.8 else "🟡" if match.similarity > 0.6 else "🟠" if match.similarity > 0.4 else "🔴"
                    print(f"   {i+1:2d}. {similarity_status} {result_dict['primary_name']:<20} | {match.similarity:.3f} | {match.category}")
                
                return results
                
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def test_multilingual_queries(self):
        """Test the system with various multilingual queries"""
        print(f"\n🧪 TESTING MULTILINGUAL QUERIES")
        print("=" * 50)
        
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
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*20} TEST {i}/{len(test_queries)} {'='*20}")
            results = self.search_inventory(query, top_k=10)
            
            if results:
                print(f"✅ Found {len(results)} matches")
                print("🏆 Top 3 matches:")
                for j, result in enumerate(results[:3], 1):
                    print(f"   {j}. {result['primary_name']} ({result['similarity']:.3f}) - ₹{result['price']}/{result['unit']}")
            else:
                print("❌ No matches found")
            
            time.sleep(0.5)  # Small delay for readability
    
    def interactive_search(self):
        """Interactive search mode"""
        print(f"\n💬 INTERACTIVE SEARCH MODE")
        print("=" * 40)
        print("Type your queries in any language (Hindi/English/Hinglish/Marathi)")
        print("Type 'quit' to exit")
        
        while True:
            try:
                query = input("\n🔍 Enter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                results = self.search_inventory(query, top_k=12)
                
                if results:
                    print(f"\n🎯 TOP MATCHES FOR: '{query}'")
                    print("-" * 50)
                    for i, result in enumerate(results, 1):
                        price_info = f"₹{result['price']}/{result['unit']}" if result['price'] > 0 else "Price not set"
                        print(f"{i:2d}. {result['primary_name']:<20} | {result['similarity']:.3f} | {price_info}")
                        if len(result['names']) > 1:
                            other_names = ", ".join(result['names'][1:])
                            print(f"     Also known as: {other_names}")
                else:
                    print("❌ No matches found. Try a different query.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    """Main function to run the complete system"""
    try:
        # Initialize system
        rag_system = VectorRAGSystem()
        
        # Get current stats
        stats = rag_system.get_embedding_stats()
        
        # Embed inventory if needed
        if stats['coverage_percent'] < 100:
            print(f"\n⚠️ Only {stats['coverage_percent']:.1f}% of items have embeddings")
            embed_choice = input("🤔 Do you want to embed all items now? (y/n): ").strip().lower()
            
            if embed_choice in ['y', 'yes']:
                success = rag_system.embed_all_inventory()
                if success:
                    print("✅ All items embedded successfully!")
                    rag_system.get_embedding_stats()  # Show updated stats
                else:
                    print("❌ Embedding failed. Check the logs above.")
                    return
        else:
            print("✅ All items already have embeddings!")
        
        # Test multilingual queries
        test_choice = input("\n🧪 Run multilingual test queries? (y/n): ").strip().lower()
        if test_choice in ['y', 'yes']:
            rag_system.test_multilingual_queries()
        
        # Interactive search
        interactive_choice = input("\n💬 Start interactive search? (y/n): ").strip().lower()
        if interactive_choice in ['y', 'yes']:
            rag_system.interactive_search()
        
        print("\n🎉 Vector RAG System test completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️ System interrupted by user")
    except Exception as e:
        print(f"\n❌ System error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()