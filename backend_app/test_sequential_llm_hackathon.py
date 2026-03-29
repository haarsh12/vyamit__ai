"""
Hackathon Demo Test Script
Sequential Multi-LLM Orchestration System with Memory & Logging

This script demonstrates the complete system functionality:
1. Sequential model execution (Qwen → Gemini → Gemma)
2. Memory-enabled conversations
3. Detailed structured logging
4. Performance tracking
"""

import asyncio
import json
import time
from datetime import datetime
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.sequential_multi_llm_service import SequentialMultiLLMService

class HackathonDemo:
    """Complete hackathon demonstration"""
    
    def __init__(self):
        print("🚀 HACKATHON DEMO INITIALIZING...")
        print("=" * 80)
        self.service = SequentialMultiLLMService()
        
    async def run_demo(self):
        """Run complete hackathon demonstration"""
        
        print("\n🎯 HACKATHON DEMO: Sequential Multi-LLM Orchestration System")
        print("=" * 80)
        print("📋 SYSTEM: Sequential Multi-LLM Orchestration System with Memory & Logging")
        print("🔄 MODELS: Qwen → Gemini → Gemma")
        print("🧠 MEMORY: Conversation Buffer Enabled")
        print("📊 LOGGING: Structured Terminal Output")
        print("=" * 80)
        
        # Test scenarios for hackathon
        test_scenarios = [
            {
                "name": "Billing Task (Hindi/English Mix)",
                "query": "2 kilo chawal 50 rupaye kilo aur 1 liter doodh 60 rupaye",
                "expected": "JSON billing response"
            },
            {
                "name": "Price Query (English)",
                "query": "What is the current price of tomatoes per kg?",
                "expected": "Structured price information"
            },
            {
                "name": "General Query (Hinglish)",
                "query": "Kya aap mujhe vegetables ki list de sakte hain?",
                "expected": "Helpful response in context"
            },
            {
                "name": "Follow-up Conversation",
                "query": "Add 3 kg onions at 40 rupees per kg to my previous bill",
                "expected": "Context-aware billing update"
            },
            {
                "name": "Complex Billing (Multiple Items)",
                "query": "I need 2 kg rice, 1 liter oil, 500g sugar, and 1 kg dal. Rice is 60/kg, oil 120/liter, sugar 45/kg, dal 80/kg",
                "expected": "Complete JSON billing structure"
            }
        ]
        
        print(f"\n🧪 RUNNING {len(test_scenarios)} TEST SCENARIOS")
        print("=" * 80)
        
        demo_results = []
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🔍 SCENARIO {i}: {scenario['name']}")
            print(f"📝 Query: '{scenario['query']}'")
            print(f"🎯 Expected: {scenario['expected']}")
            print("-" * 60)
            
            # Process query
            start_time = time.time()
            result = await self.service.process_query(scenario['query'])
            scenario_time = time.time() - start_time
            
            # Store results
            demo_results.append({
                "scenario": scenario['name'],
                "query": scenario['query'],
                "result": result,
                "scenario_time": scenario_time
            })
            
            print(f"\n✅ SCENARIO {i} COMPLETED in {scenario_time:.3f}s")
            print("=" * 60)
            
            # Small delay between scenarios for readability
            await asyncio.sleep(1)
        
        # Final demo summary
        await self.print_demo_summary(demo_results)
        
        return demo_results
    
    async def print_demo_summary(self, results):
        """Print comprehensive demo summary"""
        
        print("\n" + "=" * 80)
        print("🏆 HACKATHON DEMO SUMMARY")
        print("=" * 80)
        
        # Performance stats
        stats = self.service.get_performance_stats()
        
        print(f"📊 SYSTEM PERFORMANCE:")
        print(f"   Total Requests: {stats['total_requests']}")
        print(f"   Qwen Success: {stats['qwen_success']}")
        print(f"   Gemini Success: {stats['gemini_success']}")
        print(f"   Gemma Success: {stats['gemma_success']}")
        print(f"   Total Failures: {stats['total_failures']}")
        print(f"   Average Response Time: {stats['avg_response_time']:.3f}s")
        print(f"   Memory Conversations: {stats['memory_conversations']}")
        
        # Model distribution
        total_success = stats['qwen_success'] + stats['gemini_success'] + stats['gemma_success']
        if total_success > 0:
            print(f"\n🎯 MODEL USAGE DISTRIBUTION:")
            print(f"   Qwen: {(stats['qwen_success']/total_success)*100:.1f}%")
            print(f"   Gemini: {(stats['gemini_success']/total_success)*100:.1f}%")
            print(f"   Gemma: {(stats['gemma_success']/total_success)*100:.1f}%")
        
        # Conversation history
        history = self.service.get_conversation_history()
        print(f"\n🧠 CONVERSATION MEMORY:")
        print(f"   Total Conversations: {len(history)}")
        
        if history:
            print(f"   Recent Conversations:")
            for i, conv in enumerate(history[-3:], 1):  # Show last 3
                print(f"     {i}. User: {conv['user'][:50]}...")
                print(f"        AI: {conv['assistant'][:50]}...")
        
        # Scenario results summary
        print(f"\n📋 SCENARIO RESULTS:")
        for i, result in enumerate(results, 1):
            success_icon = "✅" if result['result']['success'] else "❌"
            print(f"   {success_icon} Scenario {i}: {result['result']['model_used']} ({result['scenario_time']:.3f}s)")
        
        print("\n🎉 HACKATHON DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
    
    async def interactive_demo(self):
        """Interactive demo for live presentation"""
        
        print("\n🎤 INTERACTIVE HACKATHON DEMO")
        print("=" * 50)
        print("Type your queries to test the system live!")
        print("Commands: 'quit' to exit, 'stats' for performance, 'history' for conversation")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n👤 Your Query: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 Demo ended!")
                    break
                elif user_input.lower() == 'stats':
                    stats = self.service.get_performance_stats()
                    print(f"\n📊 Current Stats: {json.dumps(stats, indent=2)}")
                    continue
                elif user_input.lower() == 'history':
                    history = self.service.get_conversation_history()
                    print(f"\n🧠 Conversation History ({len(history)} conversations):")
                    for i, conv in enumerate(history[-3:], 1):
                        print(f"   {i}. User: {conv['user']}")
                        print(f"      AI: {conv['assistant']}")
                    continue
                elif not user_input:
                    continue
                
                # Process the query
                print(f"\n🔄 Processing: '{user_input}'")
                result = await self.service.process_query(user_input)
                
                print(f"\n🤖 Response: {result['response']}")
                print(f"📊 Model Used: {result['model_used']} ({result['execution_time']:.3f}s)")
                
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

async def main():
    """Main demo execution"""
    
    print("🚀 HACKATHON DEMO STARTING...")
    
    try:
        demo = HackathonDemo()
        
        # Run automated demo
        print("\n1️⃣ RUNNING AUTOMATED DEMO SCENARIOS...")
        await demo.run_demo()
        
        # Ask for interactive demo
        print("\n" + "=" * 50)
        interactive = input("🎤 Run interactive demo? (y/n): ").strip().lower()
        
        if interactive == 'y':
            await demo.interactive_demo()
        
        print("\n🎉 HACKATHON DEMO COMPLETED!")
        
    except Exception as e:
        print(f"\n💥 Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())