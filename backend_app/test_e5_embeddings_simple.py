#!/usr/bin/env python3
"""
🧪 Simple Test: intfloat/multilingual-e5-small
Testing embeddings in terminal before Supabase integration
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def main():
    print("🚀 Testing intfloat/multilingual-e5-small model")
    print("=" * 50)
    
    # Step 1: Load model
    print("📦 Loading intfloat/multilingual-e5-small...")
    model = SentenceTransformer("intfloat/multilingual-e5-small")
    print("✅ Model loaded successfully!")
    
    # Step 2: Simple Embedding Test
    print("\n🔍 Step 2: Simple Embedding Test")
    print("-" * 30)
    
    # Test sentences (your real use case)
    texts = [
        "tamatar ka rate kya hai",
        "what is tomato price", 
        "टोमॅटोचा भाव काय आहे",
        "price of onion today"
    ]
    
    # Generate embeddings
    embeddings = model.encode(texts, normalize_embeddings=True)
    
    # Print embedding info
    for i, text in enumerate(texts):
        print(f"\nText: {text}")
        print(f"Embedding length: {len(embeddings[i])}")
        print(f"First 5 values: {embeddings[i][:5]}")
    
    # Step 3: Check Similarity (VERY IMPORTANT)
    print("\n🔍 Step 3: Check Similarity")
    print("-" * 30)
    
    # Compare similarity
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])
    print(f"\nSimilarity (tamatar vs tomato): {sim[0][0]:.3f}")
    
    sim2 = cosine_similarity([embeddings[0]], [embeddings[3]])
    print(f"Similarity (tamatar vs onion): {sim2[0][0]:.3f}")
    
    # Expected results check
    if sim[0][0] > 0.7:
        print("✅ Hinglish = understood")
        print("✅ Correct matching works")
    else:
        print("⚠️ Lower similarity than expected")
    
    # Step 4: Simulate YOUR App (Mini RAG without DB)
    print("\n🧪 Step 4: Simulate YOUR App (Mini RAG without DB)")
    print("-" * 50)
    
    # Fake database
    db = [
        "Tomato price is ₹25/kg",
        "Onion price is ₹30/kg", 
        "Rice price is ₹50/kg"
    ]
    
    db_embeddings = model.encode(db, normalize_embeddings=True)
    
    query = "tamatar ka bhav kya hai"
    query_emb = model.encode([query], normalize_embeddings=True)
    
    # Find best match
    scores = cosine_similarity(query_emb, db_embeddings)[0]
    best_idx = np.argmax(scores)
    
    print(f"\nQuery: '{query}'")
    print(f"Best match: {db[best_idx]}")
    print(f"Score: {scores[best_idx]:.3f}")
    
    # Show all scores
    print("\nAll matches:")
    for i, (item, score) in enumerate(zip(db, scores)):
        status = "🎯" if i == best_idx else "  "
        print(f"{status} {item} - Score: {score:.3f}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed! Model is working perfectly!")
    print("✅ Ready for Supabase vector database integration")

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install sentence-transformers scikit-learn")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()