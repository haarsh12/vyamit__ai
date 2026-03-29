"""
API Test Script for Sequential Multi-LLM System
Tests all endpoints for hackathon demo
"""

import requests
import json
import time
from datetime import datetime

class SequentialAPITester:
    """Test the Sequential Multi-LLM API endpoints"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.sequential_url = f"{base_url}/sequential-llm"
        
    def test_system_info(self):
        """Test system info endpoint"""
        print("\n🔍 Testing System Info...")
        
        try:
            response = requests.get(f"{self.sequential_url}/system-info")
            if response.status_code == 200:
                data = response.json()
                print("✅ System Info Retrieved:")
                print(f"   System: {data['system_name']}")
                print(f"   Models: {', '.join(data['models'])}")
                print(f"   Status: {data['status']}")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_query_processing(self):
        """Test query processing endpoint"""
        print("\n🔍 Testing Query Processing...")
        
        test_queries = [
            "2 kilo chawal 50 rupaye kilo",
            "What is the price of tomatoes?",
            "Hello, how are you?"
        ]
        
        results = []
        
        for query in test_queries:
            print(f"\n   Testing: '{query}'")
            
            try:
                payload = {
                    "text": query,
                    "include_history": True
                }
                
                response = requests.post(
                    f"{self.sequential_url}/query",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Success: {data['model_used']} ({data['execution_time']:.3f}s)")
                    print(f"   📤 Response: {data['response'][:100]}...")
                    results.append(True)
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    results.append(False)
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                results.append(False)
            
            time.sleep(1)  # Small delay between requests
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 Query Processing Success Rate: {success_rate:.1f}%")
        return success_rate > 80
    
    def test_conversation_history(self):
        """Test conversation history endpoint"""
        print("\n🔍 Testing Conversation History...")
        
        try:
            response = requests.get(f"{self.sequential_url}/conversation-history")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ History Retrieved: {data['total_count']} conversations")
                if data['conversations']:
                    print("   Recent conversations:")
                    for i, conv in enumerate(data['conversations'][-2:], 1):
                        print(f"     {i}. User: {conv['user'][:50]}...")
                        print(f"        AI: {conv['assistant'][:50]}...")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_performance_stats(self):
        """Test performance stats endpoint"""
        print("\n🔍 Testing Performance Stats...")
        
        try:
            response = requests.get(f"{self.sequential_url}/performance-stats")
            if response.status_code == 200:
                data = response.json()
                print("✅ Performance Stats Retrieved:")
                print(f"   Total Requests: {data['total_requests']}")
                print(f"   Qwen Success: {data['qwen_success']}")
                print(f"   Gemini Success: {data['gemini_success']}")
                print(f"   Gemma Success: {data['gemma_success']}")
                print(f"   Avg Response Time: {data['avg_response_time']:.3f}s")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_demo_endpoint(self):
        """Test the demo endpoint"""
        print("\n🔍 Testing Demo Endpoint...")
        
        try:
            response = requests.post(f"{self.sequential_url}/demo-test")
            if response.status_code == 200:
                data = response.json()
                print("✅ Demo Test Completed:")
                print(f"   Test Queries: {data['test_queries']}")
                print(f"   Results: {len(data['results'])} processed")
                
                # Show results summary
                for i, result in enumerate(data['results'], 1):
                    query_result = result['result']
                    success_icon = "✅" if query_result['success'] else "❌"
                    print(f"     {success_icon} Query {i}: {query_result['model_used']}")
                
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def run_complete_test(self):
        """Run all tests"""
        print("🚀 SEQUENTIAL MULTI-LLM API TESTING")
        print("=" * 60)
        print(f"🌐 Base URL: {self.base_url}")
        print(f"🔗 Sequential LLM URL: {self.sequential_url}")
        print("=" * 60)
        
        tests = [
            ("System Info", self.test_system_info),
            ("Query Processing", self.test_query_processing),
            ("Conversation History", self.test_conversation_history),
            ("Performance Stats", self.test_performance_stats),
            ("Demo Endpoint", self.test_demo_endpoint)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 40)
            
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        success_rate = (passed / total) * 100
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed}/{total})")
        
        if success_rate >= 80:
            print("🎉 API TESTING SUCCESSFUL - Ready for Hackathon!")
        else:
            print("⚠️  Some tests failed - Check server and configuration")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    
    print("🧪 SEQUENTIAL MULTI-LLM API TESTER")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️  Server responded with non-200 status")
    except:
        print("❌ Server is not running!")
        print("💡 Start the server with: python start_server.py")
        return
    
    # Run tests
    tester = SequentialAPITester()
    success = tester.run_complete_test()
    
    if success:
        print("\n🚀 Ready for hackathon presentation!")
    else:
        print("\n🔧 Fix issues before demo")

if __name__ == "__main__":
    main()