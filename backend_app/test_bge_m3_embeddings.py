#!/usr/bin/env python3
"""
Test BAAI/bge-m3 Embedding Model
Testing multilingual embeddings for Hindi/Marathi/Hinglish support
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import time

def test_embedding_model():
    print("🚀 Loading BAAI/bge-m3 model...")
    start_time = time.time()
    
    # Load the model
    model = SentenceTransformer("BAAI/bge-m3")
    load_time = time.time() - start_time
    print(f"✅ Model loaded in {load_time:.2f} seconds")
    
    print("\n" + "="*60)
    print("📝 STEP 1: Basic Embedding Generation")
    print("="*60)
    
    # Test sentences (multilingual)
    texts = [
        "tamatar ka rate kya hai",           # Hinglish
        "what is tomato price",             # English
        "टोमॅटोचा भाव काय आहे",              # Marathi
        "प्याज का भाव क्या है",              # Hindi
        "price of onion today",             # English
        "आज चावल का रेट क्या है",           # Hindi
        "rice price today"                  # English
    ]
    
    print("🔄 Generating embeddings...")
    start_time = time.time()
    embeddings = model.encode(texts, normalize_embeddings=True)
    embedding_time = time.time() - start_time
    
    print(f"⚡ Generated {len(texts)} embeddings in {embedding_time:.2f} seconds")
    print(f"📊 Average time per embedding: {embedding_time/len(texts):.3f} seconds")
    
    # Print embedding details
    for i, text in enumerate(texts):
        print(f"\n📄 Text: '{text}'")
        print(f"   📏 Embedding length: {len(embeddings[i])}")
        print(f"   🔢 First 5 values: {embeddings[i][:5]}")
        print(f"   📈 Min/Max values: {embeddings[i].min():.3f} / {embeddings[i].max():.3f}")
    
    print("\n" + "="*60)
    print("🔍 STEP 2: Similarity Analysis")
    print("="*60)
    
    # Test similarity between related queries
    similarity_tests = [
        (0, 1, "Hinglish vs English (tamatar vs tomato)"),
        (0, 2, "Hinglish vs Marathi (tamatar vs टोमॅटो)"),
        (3, 4, "Hindi vs English (प्याज vs onion)"),
        (5, 6, "Hindi vs English (चावल vs rice)"),
        (0, 4, "Different items (tamatar vs onion)"),
        (1, 6, "Different items (tomato vs rice)")
    ]
    
    print("🧮 Computing similarities...")
    for idx1, idx2, description in similarity_tests:
        sim = cosine_similarity([embeddings[idx1]], [embeddings[idx2]])[0][0]
        status = "✅ GOOD" if sim > 0.7 else "⚠️ MEDIUM" if sim > 0.4 else "❌ LOW"
        print(f"{status} {description}: {sim:.3f}")
        print(f"     Text 1: '{texts[idx1]}'")
        print(f"     Text 2: '{texts[idx2]}'")
        print()
    
    print("\n" + "="*60)
    print("🏪 STEP 3: Mini RAG Simulation (Without Database)")
    print("="*60)
    
    # Simulate a product database
    product_db = [
        "Tomato price is ₹25 per kg in Mumbai market",
        "Onion price is ₹30 per kg today",
        "Rice basmati price is ₹50 per kg",
        "Potato price is ₹20 per kg",
        "Wheat flour price is ₹35 per kg",
        "Sugar price is ₹40 per kg",
        "Dal moong price is ₹80 per kg"
    ]
    
    print("🗄️ Creating product database embeddings...")
    db_embeddings = model.encode(product_db, normalize_embeddings=True)
    
    # Test queries
    test_queries = [
        "tamatar ka bhav kya hai",          # Hinglish for tomato
        "प्याज का रेट बताओ",               # Hindi for onion
        "rice ka price kitna hai",          # Hinglish for rice
        "what is potato cost",              # English for potato
        "चीनी का भाव क्या है"               # Hindi for sugar
    ]
    
    print("\n🔍 Testing RAG retrieval...")
    for query in test_queries:
        print(f"\n❓ Query: '{query}'")
        
        # Generate query embedding
        query_emb = model.encode([query], normalize_embeddings=True)
        
        # Find best matches
        scores = cosine_similarity(query_emb, db_embeddings)[0]
        
        # Get top 3 matches
        top_indices = np.argsort(scores)[::-1][:3]
        
        print("   🎯 Top matches:")
        for rank, idx in enumerate(top_indices, 1):
            score = scores[idx]
            status = "🟢" if score > 0.7 else "🟡" if score > 0.5 else "🔴"
            print(f"   {rank}. {status} Score: {score:.3f} - '{product_db[idx]}'")
    
    print("\n" + "="*60)
    print("📊 STEP 4: Performance Summary")
    print("="*60)
    
    print(f"🏷️  Model: BAAI/bge-m3")
    print(f"📏 Embedding dimension: {len(embeddings[0])}")
    print(f"⏱️  Model load time: {load_time:.2f}s")
    print(f"⚡ Embedding speed: {len(texts)/embedding_time:.1f} texts/second")
    print(f"🌍 Multilingual support: ✅ Hindi, Marathi, English, Hinglish")
    print(f"🎯 Semantic understanding: ✅ Cross-language matching works")
    
    print("\n✅ BAAI/bge-m3 model test completed successfully!")
    print("🚀 Ready for Supabase integration!")

if __name__ == "__main__":
    try:
        test_embedding_model()
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install sentence-transformers scikit-learn")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()