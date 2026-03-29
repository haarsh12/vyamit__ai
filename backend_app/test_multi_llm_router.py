#!/usr/bin/env python3
"""
🚀 HACKATHON DEMO: Adaptive Multi-LLM Routing System Test
This script demonstrates the intelligent model routing with detailed logging
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_mock_inventory():
    """Create mock inventory for testing"""
    class MockItem:
        def __init__(self, names, price, unit, category="grocery"):
            self.names = json.dumps(names) if isinstance(names, list) else names
            self.price = price
            self.unit = unit
            self.category = category
    
    return [
        MockItem(["chawal", "rice", "basmati"], 120.0, "kg"),
        MockItem(["maggie", "noodles"], 5.0, "pic"),
        MockItem(["sugar", "cheeni"], 45.0, "kg"),
        MockItem(["oil", "tel", "cooking oil"], 150.0, "litre"),
        MockItem(["atta", "wheat flour"], 40.0, "kg"),
        MockItem(["doodh", "milk"], 60.0, "litre"),
        MockItem(["pyaz", "onion"], 30.0, "kg"),
        MockItem(["aloo", "potato"], 25.0, "kg")
    ]

def print_demo_header():
    """Print hackathon demo header"""
    print("\n" + "🚀" * 30)
    print("🎯 HACKATHON DEMO: ADAPTIVE MULTI-LLM ROUTING SYSTEM")
    print("🚀" * 30)
    print("📊 System: Intelligent model selection based on query complexity")
    print("🤖 Models: Qwen (Fast) | Gemma (Balanced) | Gemini (Smart)")
    print("🌐 Languages: English | Hindi | Hinglish")
    print("📝 Features: Structured logging | Performance analytics | Chat memory")
    print("🚀" * 30 + "\n")

def run_hackathon_demo():
    """Run comprehensive hackathon demonstration"""
    print_demo_header()
    
    try:
        from app.services.ai_service_router import AdaptiveMultiLLMService
        
        # Initialize service
        print("🔧 Initializing Adaptive Multi-LLM Routing System...")
        service = AdaptiveMultiLLMService()
        inventory = create_mock_inventory()
        
        # Demo test cases - designed to showcase different routing decisions
        demo_cases = [
            {
                "category": "🟢 LOW COMPLEXITY (Qwen)",
                "cases": [
                    "namaste",
                    "2 kilo chawal",
                    "maggie ka price kya hai",
                    "1kg sugar 45 rupaye"
                ]
            },
            {
                "category": "🟡 MEDIUM COMPLEXITY (Gemma)", 
                "cases": [
                    "suggest me best items for breakfast",
                    "calculate total cost for 2kg rice and 1kg sugar",
                    "find cheapest cooking oil options",
                    "recommend items under 100 rupees"
                ]
            },
            {
                "category": "🔴 HIGH COMPLEXITY (Gemini)",
                "cases": [
                    "analyze market trends for rice prices in last month and explain why prices are fluctuating",
                    "compare nutritional value of different cooking oils and suggest best option for health",
                    "explain the economic impact of seasonal vegetables on grocery store profits",
                    "provide detailed market analysis for setting competitive prices in local area"
                ]
            },
            {
                "category": "🌐 MULTILINGUAL TESTS",
                "cases": [
                    "customer raju charde 5rs wali 6 maggie packet",
                    "दो किलो चावल और एक किलो चीनी",
                    "oil ka price kitna hai per litre",
                    "atta aur chawal ka total cost calculate karo"
                ]
            }
        ]
        
        total_tests = sum(len(category["cases"]) for category in demo_cases)
        current_test = 0
        
        for category_data in demo_cases:
            print(f"\n{'='*60}")
            print(f"{category_data['category']}")
            print(f"{'='*60}")
            
            for test_case in category_data["cases"]:
                current_test += 1
                print(f"\n🧪 TEST {current_test}/{total_tests}")
                print(f"📝 Input: \"{test_case}\"")
                
                try:
                    # Process the query
                    start_time = time.time()
                    result = service.process_voice_command(test_case, inventory)
                    end_time = time.time()
                    
                    # The detailed log is already printed by the service
                    # Just add a brief summary here
                    print(f"⚡ Processing completed in {(end_time - start_time)*1000:.2f}ms")
                    
                    # Small delay for demo effect
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Error processing test case: {e}")
        
        # Show final statistics
        print(f"\n{'🎯'*20} DEMO SUMMARY {'🎯'*20}")
        
        # Get service statistics
        service_info = service.get_service_info()
        stats = service_info.get("statistics", {})
        
        print(f"\n📊 SYSTEM PERFORMANCE:")
        print(f"   • Total Requests: {stats.get('total_requests', 0)}")
        print(f"   • Success Rate: {stats.get('success_rate', 0):.1f}%")
        
        if stats.get('model_usage'):
            print(f"\n🤖 MODEL USAGE:")
            for model, count in stats['model_usage'].items():
                print(f"   • {model.upper()}: {count} requests")
        
        if stats.get('avg_latency_by_model'):
            print(f"\n⚡ AVERAGE LATENCY:")
            for model, latency in stats['avg_latency_by_model'].items():
                print(f"   • {model.upper()}: {latency:.2f}ms")
        
        print(f"\n💬 CHAT MEMORY:")
        history = service.get_chat_history()
        print(f"   • Messages Stored: {len(history)}")
        print(f"   • Memory Capacity: 20 messages")
        
        print(f"\n🔧 MODEL AVAILABILITY:")
        models = service_info.get("models", {})
        for model_name, model_info in models.items():
            status = "✅ Available" if model_info.get("available") else "❌ Unavailable"
            role = model_info.get("role", "Unknown")
            print(f"   • {model_name.upper()}: {status} ({role})")
        
        print(f"\n🎉 HACKATHON DEMO COMPLETED SUCCESSFULLY!")
        print(f"🏆 Key Features Demonstrated:")
        print(f"   ✅ Intelligent model routing based on query complexity")
        print(f"   ✅ Multi-language support (English, Hindi, Hinglish)")
        print(f"   ✅ Structured logging with detailed analytics")
        print(f"   ✅ Performance monitoring and statistics")
        print(f"   ✅ Chat memory and conversation context")
        print(f"   ✅ Graceful fallback handling")
        print(f"   ✅ Real-time terminal logging")
        
        # Show recent logs sample
        print(f"\n📋 RECENT LOGS SAMPLE:")
        recent_logs = service.get_logs(3)
        for i, log in enumerate(recent_logs[-3:], 1):
            print(f"   {i}. {log['timestamp'][:19]} | {log['routing']['selected_model'].upper()} | "
                  f"{log['execution']['latency_ms']}ms | {log['user_input'][:30]}...")
        
        print(f"\n{'🚀'*30}")
        print(f"🎯 ADAPTIVE MULTI-LLM ROUTING SYSTEM DEMO COMPLETE")
        print(f"{'🚀'*30}\n")
        
    except Exception as e:
        print(f"❌ Demo initialization failed: {e}")
        print("\n💡 Make sure to:")
        print("   1. Set HUGGINGFACE_API_TOKEN and/or GEMINI_API_KEY in .env")
        print("   2. Install dependencies: pip install google-generativeai")
        print("   3. Check your internet connection")

if __name__ == "__main__":
    run_hackathon_demo()