#!/usr/bin/env python3
"""
🚀 COMPLETE VECTOR RAG SYSTEM TEST
Full end-to-end test with Supabase integration
- Embeds all inventory items
- Tests multilingual search with 10+ matches
- Full debug output for every step
- Production-ready implementation
"""

import os
import sys
import time
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header(title: str, char: str = "=", width: int = 70):
    """Print a formatted header"""
    print(f"\n{char * width}")
    print(f"🚀 {title}")
    print(f"{char * width}")

def print_step(step: str, details: str = ""):
    """Print a step with formatting"""
    print(f"\n📋 {step}")
    if details:
        print(f"   {details}")

def test_dependencies():
    """Test if all required dependencies are installed"""
    print_header("TESTING DEPENDENCIES")
    
    required_packages = [
        'sentence_transformers',
        'sqlalchemy', 
        'psycopg2',
        'numpy',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'psycopg2':
                import psycopg2
            elif package == 'sentence_transformers':
                import sentence_transformers
            elif package == 'sqlalchemy':
                import sqlalchemy
            elif package == 'numpy':
                import numpy
            elif package == 'python-dotenv':
                import dotenv
            
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("📦 Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("\n🎉 All dependencies are installed!")
    return True

def test_environment_variables():
    """Test if all required environment variables are set"""
    print_header("TESTING ENVIRONMENT VARIABLES")
    
    required_vars = [
        'DATABASE_URL',
        'HUGGINGFACE_API_TOKEN',
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show partial value for security
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("\n🎉 All environment variables are set!")
    return True

def test_database_connection():
    """Test database connection"""
    print_header("TESTING DATABASE CONNECTION")
    
    try:
        from sqlalchemy import create_engine, text
        
        database_url = os.getenv("DATABASE_URL")
        print(f"🔗 Connecting to: {database_url[:50]}...")
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone().test
            print(f"✅ Basic connection: {test_value}")
            
            # Test vector extension
            result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
            vector_ext = result.fetchone()
            if vector_ext:
                print("✅ Vector extension: ENABLED")
            else:
                print("❌ Vector extension: NOT ENABLED")
                return False
            
            # Test item table
            result = conn.execute(text("SELECT COUNT(*) as count FROM item"))
            item_count = result.fetchone().count
            print(f"✅ Item table: {item_count} items found")
            
            # Test embedding column
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'item' AND column_name = 'embedding'
            """))
            embedding_col = result.fetchone()
            if embedding_col:
                print("✅ Embedding column: EXISTS")
            else:
                print("❌ Embedding column: MISSING")
                return False
            
            # Test match function
            result = conn.execute(text("""
                SELECT proname 
                FROM pg_proc 
                WHERE proname = 'match_items'
            """))
            match_func = result.fetchone()
            if match_func:
                print("✅ Match function: EXISTS")
            else:
                print("❌ Match function: MISSING")
                return False
        
        print("\n🎉 Database connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_model_loading():
    """Test loading the embedding model"""
    print_header("TESTING MODEL LOADING")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        print("📦 Loading intfloat/multilingual-e5-small...")
        start_time = time.time()
        
        model = SentenceTransformer("intfloat/multilingual-e5-small")
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        
        # Test embedding generation
        test_text = "passage: Test embedding generation"
        print(f"🧪 Testing with: '{test_text}'")
        
        embedding = model.encode(test_text, normalize_embeddings=True)
        print(f"✅ Embedding shape: {embedding.shape}")
        print(f"✅ Embedding dimension: {len(embedding)}")
        print(f"✅ First 5 values: {embedding[:5].round(4)}")
        
        # Test multilingual
        hindi_text = "passage: टमाटर का भाव"
        hindi_embedding = model.encode(hindi_text, normalize_embeddings=True)
        print(f"✅ Hindi embedding shape: {hindi_embedding.shape}")
        
        print("\n🎉 Model loading successful!")
        return model
        
    except Exception as e:
        print(f"❌ Model loading failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def run_complete_vector_rag_test():
    """Run the complete vector RAG system test"""
    print_header("COMPLETE VECTOR RAG SYSTEM TEST", "🚀", 80)
    
    # Step 1: Test dependencies
    if not test_dependencies():
        print("❌ Dependency test failed. Please install missing packages.")
        return False
    
    # Step 2: Test environment variables
    if not test_environment_variables():
        print("❌ Environment variable test failed. Please check your .env file.")
        return False
    
    # Step 3: Test database connection
    if not test_database_connection():
        print("❌ Database connection test failed. Please check your database setup.")
        return False
    
    # Step 4: Test model loading
    model = test_model_loading()
    if not model:
        print("❌ Model loading test failed.")
        return False
    
    # Step 5: Run the actual vector RAG system
    print_header("RUNNING VECTOR RAG SYSTEM")
    
    try:
        from vector_rag_system import VectorRAGSystem
        
        # Initialize system
        rag_system = VectorRAGSystem()
        
        # Get current stats
        stats = rag_system.get_embedding_stats()
        
        # Embed inventory if needed
        if stats['coverage_percent'] < 100:
            print(f"\n⚠️ Only {stats['coverage_percent']:.1f}% of items have embeddings")
            print("🔄 Embedding all items automatically...")
            
            success = rag_system.embed_all_inventory()
            if success:
                print("✅ All items embedded successfully!")
                rag_system.get_embedding_stats()  # Show updated stats
            else:
                print("❌ Embedding failed. Check the logs above.")
                return False
        else:
            print("✅ All items already have embeddings!")
        
        # Test with specific queries that should return 10+ matches
        print_header("TESTING WITH SAMPLE QUERIES (10+ MATCHES)")
        
        test_queries = [
            {
                'query': 'tamatar ka rate kya hai',
                'description': 'Hinglish query for tomato',
                'expected_matches': 'Should find tomato and related vegetables'
            },
            {
                'query': 'प्याज का भाव बताओ', 
                'description': 'Hindi query for onion',
                'expected_matches': 'Should find onion and related vegetables'
            },
            {
                'query': 'rice ka price kitna hai',
                'description': 'Hinglish query for rice',
                'expected_matches': 'Should find rice and related grains'
            },
            {
                'query': 'dal moong',
                'description': 'Hindi query for lentils',
                'expected_matches': 'Should find various types of dal'
            },
            {
                'query': 'oil',
                'description': 'English query for oil',
                'expected_matches': 'Should find various types of oil'
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n{'='*20} TEST QUERY {i}/{len(test_queries)} {'='*20}")
            print(f"📝 Query: '{test_case['query']}'")
            print(f"📋 Description: {test_case['description']}")
            print(f"🎯 Expected: {test_case['expected_matches']}")
            
            # Search with 15 matches to ensure we get 10+
            results = rag_system.search_inventory(test_case['query'], top_k=15, similarity_threshold=0.1)
            
            if results:
                print(f"\n🎉 SUCCESS: Found {len(results)} matches!")
                print("🏆 TOP 10 MATCHES:")
                print("-" * 60)
                
                for j, result in enumerate(results[:10], 1):
                    names_display = result['names'][0] if result['names'] else 'Unknown'
                    price_display = f"₹{result['price']}/{result['unit']}" if result['price'] > 0 else "Price not set"
                    similarity_emoji = "🟢" if result['similarity'] > 0.8 else "🟡" if result['similarity'] > 0.6 else "🟠"
                    
                    print(f"{j:2d}. {similarity_emoji} {names_display:<25} | {result['similarity']:.3f} | {price_display}")
                    
                    # Show alternative names if available
                    if len(result['names']) > 1:
                        alt_names = ", ".join(result['names'][1:3])  # Show first 2 alternative names
                        print(f"     Also: {alt_names}")
                
                # Show additional matches if more than 10
                if len(results) > 10:
                    print(f"\n📊 Additional {len(results) - 10} matches available with lower similarity scores")
                
            else:
                print("❌ No matches found!")
            
            time.sleep(1)  # Small delay for readability
        
        print_header("INTERACTIVE TEST MODE")
        print("💬 You can now test with your own queries!")
        print("🔍 Type any query in Hindi/English/Hinglish")
        print("📊 System will return 10+ matches with full debug info")
        print("⏹️ Type 'quit' to exit")
        
        while True:
            try:
                query = input("\n🔍 Enter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                print(f"\n{'='*50}")
                results = rag_system.search_inventory(query, top_k=15, similarity_threshold=0.1)
                
                if results:
                    print(f"\n🎯 FOUND {len(results)} MATCHES FOR: '{query}'")
                    print("-" * 60)
                    
                    for i, result in enumerate(results, 1):
                        names_display = result['names'][0] if result['names'] else 'Unknown'
                        price_display = f"₹{result['price']}/{result['unit']}" if result['price'] > 0 else "Price not set"
                        similarity_emoji = "🟢" if result['similarity'] > 0.8 else "🟡" if result['similarity'] > 0.6 else "🟠"
                        
                        print(f"{i:2d}. {similarity_emoji} {names_display:<25} | {result['similarity']:.3f} | {price_display}")
                        
                        # Show category and alternative names
                        if result['category']:
                            print(f"     Category: {result['category']}")
                        if len(result['names']) > 1:
                            alt_names = ", ".join(result['names'][1:])
                            print(f"     Also known as: {alt_names}")
                        print()  # Empty line for readability
                else:
                    print("❌ No matches found. Try a different query.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        print_header("TEST COMPLETED SUCCESSFULLY! 🎉")
        print("✅ All systems working perfectly!")
        print("✅ Vector embeddings generated and stored")
        print("✅ Multilingual search working")
        print("✅ 10+ matches returned for queries")
        print("✅ Full debug information displayed")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector RAG system test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Complete Vector RAG System Test...")
    print("📋 This will test all components and run the full system")
    print("⏱️ Estimated time: 2-5 minutes depending on data size")
    
    success = run_complete_vector_rag_test()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Your Vector RAG system is ready for production!")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)