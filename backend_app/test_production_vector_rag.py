#!/usr/bin/env python3
"""
🚀 PRODUCTION VECTOR RAG TEST
Test the integrated production vector RAG system
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your server URL
VECTOR_ENDPOINT = f"{BASE_URL}/vector"

def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def test_health_check():
    """Test the health check endpoint"""
    print_header("TESTING HEALTH CHECK")
    
    try:
        response = requests.get(f"{VECTOR_ENDPOINT}/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {data.get('status')}")
            print(f"   Model: {data.get('model')}")
            print(f"   Service Ready: {data.get('service_ready')}")
            
            if 'embedding_stats' in data:
                stats = data['embedding_stats']
                print(f"   Total Items: {stats.get('total_items')}")
                print(f"   Coverage: {stats.get('coverage_percent')}%")
            
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_embedding_stats():
    """Test the embedding statistics endpoint"""
    print_header("TESTING EMBEDDING STATISTICS")
    
    try:
        response = requests.get(f"{VECTOR_ENDPOINT}/stats")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('embedding_stats', {})
            
            print("✅ Statistics retrieved successfully!")
            print(f"   Total Items: {stats.get('total_items')}")
            print(f"   Items with Embeddings: {stats.get('items_with_embeddings')}")
            print(f"   Coverage: {stats.get('coverage_percent')}%")
            print(f"   Missing Embeddings: {stats.get('missing_embeddings')}")
            
            recommendations = data.get('recommendations', {})
            print(f"   Coverage Good: {recommendations.get('coverage_good')}")
            print(f"   Action: {recommendations.get('action_needed')}")
            
            return stats
        else:
            print(f"❌ Stats failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Stats error: {str(e)}")
        return None

def test_embed_all():
    """Test the embed all endpoint"""
    print_header("TESTING EMBED ALL ITEMS")
    
    try:
        print("🔄 Starting batch embedding process...")
        response = requests.post(f"{VECTOR_ENDPOINT}/embed-all?batch_size=10")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Batch embedding completed!")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            print(f"   Total Items: {data.get('total_items')}")
            print(f"   Embedded Items: {data.get('embedded_items')}")
            print(f"   Failed Items: {data.get('failed_items')}")
            
            return data.get('success', False)
        else:
            print(f"❌ Embed all failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Embed all error: {str(e)}")
        return False

def test_search_queries():
    """Test multilingual search queries"""
    print_header("TESTING MULTILINGUAL SEARCH")
    
    test_queries = [
        {
            'query': 'tamatar ka rate kya hai',
            'description': 'Hinglish query for tomato',
            'expected': 'Should find tomato and related vegetables'
        },
        {
            'query': 'प्याज का भाव बताओ',
            'description': 'Hindi query for onion',
            'expected': 'Should find onion and related vegetables'
        },
        {
            'query': 'rice ka price kitna hai',
            'description': 'Hinglish query for rice',
            'expected': 'Should find rice and related grains'
        },
        {
            'query': 'dal moong',
            'description': 'Hindi query for lentils',
            'expected': 'Should find various types of dal'
        },
        {
            'query': 'oil price',
            'description': 'English query for oil',
            'expected': 'Should find various types of oil'
        }
    ]
    
    successful_queries = 0
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{'='*20} TEST QUERY {i}/{len(test_queries)} {'='*20}")
        print(f"📝 Query: '{test_case['query']}'")
        print(f"📋 Description: {test_case['description']}")
        print(f"🎯 Expected: {test_case['expected']}")
        
        try:
            # Test with debug enabled
            response = requests.get(f"{VECTOR_ENDPOINT}/search", params={
                'q': test_case['query'],
                'top_k': 15,
                'threshold': 0.1,
                'debug': True
            })
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                print(f"\n🎉 SUCCESS: Found {len(results)} matches!")
                print(f"⚡ Search Time: {data.get('search_time_ms')}ms")
                
                if results:
                    print("🏆 TOP 10 MATCHES:")
                    print("-" * 60)
                    
                    for j, result in enumerate(results[:10], 1):
                        name = result.get('primary_name', 'Unknown')
                        similarity = result.get('similarity', 0)
                        price = result.get('price', 0)
                        unit = result.get('unit', '')
                        confidence = result.get('confidence', 'unknown')
                        
                        price_display = f"₹{price}/{unit}" if price > 0 else "Price not set"
                        confidence_emoji = "🟢" if confidence == "high" else "🟡" if confidence == "medium" else "🟠"
                        
                        print(f"{j:2d}. {confidence_emoji} {name:<25} | {similarity:.3f} | {price_display}")
                        
                        # Show alternative names if available
                        names = result.get('names', [])
                        if len(names) > 1:
                            alt_names = ", ".join(names[1:3])
                            print(f"     Also: {alt_names}")
                    
                    successful_queries += 1
                else:
                    print("❌ No matches found!")
            else:
                print(f"❌ Search failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
        
        time.sleep(0.5)  # Small delay for readability
    
    print(f"\n📊 SEARCH SUMMARY:")
    print(f"   Total Queries: {len(test_queries)}")
    print(f"   Successful: {successful_queries}")
    print(f"   Success Rate: {(successful_queries/len(test_queries)*100):.1f}%")
    
    return successful_queries == len(test_queries)

def test_predefined_queries():
    """Test the predefined test queries endpoint"""
    print_header("TESTING PREDEFINED QUERIES")
    
    try:
        response = requests.get(f"{VECTOR_ENDPOINT}/test-queries")
        
        if response.status_code == 200:
            data = response.json()
            test_results = data.get('test_results', {})
            summary = data.get('summary', {})
            
            print("✅ Predefined queries test completed!")
            print(f"   Total Queries: {summary.get('total_queries')}")
            print(f"   Successful: {summary.get('successful_queries')}")
            print(f"   Success Rate: {summary.get('success_rate')}")
            
            print("\n📋 DETAILED RESULTS:")
            for query, result in test_results.items():
                status = result.get('status', 'unknown')
                matches = result.get('matches', 0)
                
                status_emoji = "✅" if status == "success" else "❌"
                print(f"   {status_emoji} {query:<30} | {matches} matches")
            
            return summary.get('successful_queries', 0) > 0
        else:
            print(f"❌ Predefined queries test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Predefined queries error: {str(e)}")
        return False

def main():
    """Main test function"""
    print_header("PRODUCTION VECTOR RAG SYSTEM TEST")
    print("🧪 Testing the integrated production vector RAG system")
    print("📋 This will test all endpoints and functionality")
    
    # Step 1: Health check
    if not test_health_check():
        print("❌ Health check failed. Please check if the server is running.")
        return False
    
    # Step 2: Check embedding statistics
    stats = test_embedding_stats()
    if not stats:
        print("❌ Could not retrieve embedding statistics.")
        return False
    
    # Step 3: Embed all items if needed
    if stats.get('coverage_percent', 0) < 100:
        print(f"\n⚠️ Only {stats.get('coverage_percent', 0):.1f}% coverage detected")
        print("🔄 Running embed-all to ensure all items have embeddings...")
        
        if not test_embed_all():
            print("❌ Embedding process failed.")
            return False
        
        # Recheck stats
        print("\n🔄 Rechecking statistics after embedding...")
        stats = test_embedding_stats()
    
    # Step 4: Test search functionality
    if not test_search_queries():
        print("❌ Search queries test failed.")
        return False
    
    # Step 5: Test predefined queries
    if not test_predefined_queries():
        print("❌ Predefined queries test failed.")
        return False
    
    print_header("🎉 ALL TESTS PASSED!")
    print("✅ Production Vector RAG system is working perfectly!")
    print("✅ Multilingual search is functional")
    print("✅ All endpoints are responding correctly")
    print("✅ System is ready for production use!")
    
    print(f"\n🚀 READY TO USE:")
    print(f"   Search Endpoint: {VECTOR_ENDPOINT}/search")
    print(f"   Health Check: {VECTOR_ENDPOINT}/health")
    print(f"   Statistics: {VECTOR_ENDPOINT}/stats")
    print(f"   Test Queries: {VECTOR_ENDPOINT}/test-queries")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Production Vector RAG System Test...")
    print("📋 Make sure your server is running on http://localhost:8000")
    print("⏱️ This test will take 1-3 minutes depending on data size")
    
    input("\n🔍 Press Enter to start the test...")
    
    success = main()
    
    if success:
        print("\n🎉 SUCCESS: Your production Vector RAG system is ready!")
    else:
        print("\n❌ FAILURE: Some tests failed. Please check the error messages above.")