#!/usr/bin/env python3
"""Quick test of Vector RAG system"""

print("🚀 Starting Vector RAG System Test...")

try:
    from vector_rag_system import VectorRAGSystem
    
    print("📦 Initializing system...")
    rag_system = VectorRAGSystem()
    
    print("📊 Getting stats...")
    stats = rag_system.get_embedding_stats()
    coverage = stats['coverage_percent']
    print(f"📊 Coverage: {coverage:.1f}%")
    
    if coverage < 100:
        print("🔄 Embedding items...")
        success = rag_system.embed_all_inventory()
        if success:
            print("✅ Embedding completed!")
        else:
            print("❌ Embedding failed!")
            exit(1)
    
    print("🧪 Testing search...")
    results = rag_system.search_inventory('tamatar ka rate', top_k=10)
    print(f"✅ Found {len(results)} matches!")
    
    for i, r in enumerate(results[:5], 1):
        name = r['primary_name']
        sim = r['similarity']
        print(f"{i}. {name} - {sim:.3f}")
    
    print("🎉 Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()