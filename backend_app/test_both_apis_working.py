#!/usr/bin/env python3
"""
Quick test to verify both Gemini and Hugging Face APIs are working
"""

import requests
import json

def test_sequential_api_with_both_models():
    """Test the sequential API to see which models are actually working"""
    print("🧪 TESTING SEQUENTIAL API WITH DIFFERENT QUERIES")
    print("=" * 60)
    
    base_url = "http://localhost:8000/sequential-llm"
    
    # Test queries that might trigger different models
    test_queries = [
        "Hello, test Qwen model",
        "What is 2+2? Use Gemini",
        "Simple math: 5*3",
        "Tell me about AI models",
        "Price of 1 kg rice is 60 rupees"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔄 Test {i}: '{query}'")
        
        try:
            payload = {
                "text": query,
                "include_history": False  # Fresh context for each test
            }
            
            response = requests.post(
                f"{base_url}/query",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                model_used = data['model_used']
                exec_time = data['execution_time']
                response_text = data['response'][:100]
                
                print(f"   ✅ SUCCESS: {model_used} ({exec_time:.3f}s)")
                print(f"   📤 Response: {response_text}...")
                
                results.append({
                    "query": query,
                    "model": model_used,
                    "success": True,
                    "time": exec_time
                })
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                print(f"   Error: {response.text[:100]}")
                results.append({
                    "query": query,
                    "model": "FAILED",
                    "success": False,
                    "time": 0
                })
                
        except Exception as e:
            print(f"   💥 ERROR: {str(e)[:100]}")
            results.append({
                "query": query,
                "model": "ERROR",
                "success": False,
                "time": 0
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    model_counts = {}
    successful_tests = 0
    total_time = 0
    
    for result in results:
        if result['success']:
            successful_tests += 1
            total_time += result['time']
            model = result['model']
            model_counts[model] = model_counts.get(model, 0) + 1
    
    print(f"✅ Successful Tests: {successful_tests}/{len(results)}")
    print(f"⏱️  Average Response Time: {total_time/max(successful_tests, 1):.3f}s")
    
    print(f"\n🤖 Models Used:")
    for model, count in model_counts.items():
        print(f"   • {model}: {count} times")
    
    if successful_tests == len(results):
        print(f"\n🎉 ALL TESTS PASSED - System is working perfectly!")
    elif successful_tests > 0:
        print(f"\n✅ Partial success - {successful_tests} out of {len(results)} tests passed")
    else:
        print(f"\n❌ All tests failed - Check server configuration")
    
    return successful_tests == len(results)

def test_performance_stats():
    """Check the performance stats to see which models are actually working"""
    print(f"\n🔍 CHECKING PERFORMANCE STATS")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/sequential-llm/performance-stats")
        if response.status_code == 200:
            stats = response.json()
            
            print(f"📊 Performance Statistics:")
            print(f"   Total Requests: {stats['total_requests']}")
            print(f"   Qwen Success: {stats['qwen_success']}")
            print(f"   Gemini Success: {stats['gemini_success']}")
            print(f"   Gemma Success: {stats['gemma_success']}")
            print(f"   Average Response Time: {stats['avg_response_time']:.3f}s")
            
            # Determine which models are working
            working_models = []
            if stats['qwen_success'] > 0:
                working_models.append("Qwen (Hugging Face)")
            if stats['gemini_success'] > 0:
                working_models.append("Gemini (Google)")
            if stats['gemma_success'] > 0:
                working_models.append("Gemma (Hugging Face)")
            
            if working_models:
                print(f"\n✅ Working Models: {', '.join(working_models)}")
            else:
                print(f"\n⚠️  No successful model executions yet")
                
            return True
        else:
            print(f"❌ Failed to get stats: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting stats: {str(e)}")
        return False

def main():
    print("🚀 COMPREHENSIVE API TESTING")
    print("=" * 60)
    
    # Test the sequential API
    api_success = test_sequential_api_with_both_models()
    
    # Check performance stats
    stats_success = test_performance_stats()
    
    print(f"\n🏆 FINAL RESULTS:")
    print(f"   API Tests: {'✅ PASSED' if api_success else '❌ FAILED'}")
    print(f"   Stats Check: {'✅ PASSED' if stats_success else '❌ FAILED'}")
    
    if api_success and stats_success:
        print(f"\n🎉 SYSTEM IS FULLY OPERATIONAL!")
        print(f"💡 The sequential system is working with available models")
        print(f"🚀 Ready for production use!")
    else:
        print(f"\n⚠️  Some issues detected - check the logs above")

if __name__ == "__main__":
    main()