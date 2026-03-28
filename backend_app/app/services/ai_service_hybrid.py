import os
import json
import requests
from typing import List, Dict, Any
from collections import deque
from app.db.models import Item

class ChatMemory:
    """Simple chat memory implementation"""
    def __init__(self, max_messages: int = 20):
        self.messages = deque(maxlen=max_messages)
        self.max_messages = max_messages
    
    def add_user_message(self, message: str):
        self.messages.append({"role": "user", "content": message})
    
    def add_assistant_message(self, message: str):
        self.messages.append({"role": "assistant", "content": message})
    
    def get_history(self) -> List[Dict[str, str]]:
        return list(self.messages)
    
    def clear(self):
        self.messages.clear()
    
    def get_context_string(self) -> str:
        """Get recent conversation context as string"""
        if not self.messages:
            return ""
        
        context = "Previous conversation:\n"
        for msg in list(self.messages)[-6:]:  # Last 6 messages for context
            context += f"{msg['role']}: {msg['content']}\n"
        return context + "\nCurrent request:\n"

class HybridAIService:
    def __init__(self):
        # Initialize chat memory
        self.memory = ChatMemory(max_messages=20)
        
        # Try to initialize Hugging Face
        self.hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        self.hf_available = bool(self.hf_token)
        
        # Try to initialize Gemini as fallback
        self.gemini_available = False
        try:
            import google.generativeai as genai
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                genai.configure(api_key=gemini_key, transport="rest")
                self.genai = genai
                self.gemini_available = True
                print("✅ Gemini fallback available")
        except ImportError:
            print("⚠️ Gemini not available (google-generativeai not installed)")
        except Exception as e:
            print(f"⚠️ Gemini initialization failed: {e}")
        
        # Determine primary service
        if self.hf_available:
            self.primary_service = "huggingface"
            print("✅ Hybrid AI Service initialized (Primary: Hugging Face)")
        elif self.gemini_available:
            self.primary_service = "gemini"
            print("✅ Hybrid AI Service initialized (Primary: Gemini)")
        else:
            self.primary_service = "fallback"
            print("⚠️ Hybrid AI Service initialized (Fallback mode only)")

    def get_master_prompt(self, user_text: str, inventory_json: str, context: str = "") -> str:
        """Master prompt for Vyamit AI"""
        return f"""{context}You are Vyamit AI, a female voice assistant for "Vyamit AI App". Detect the language user is speaking and answer ONLY in that language but use Latin Script (Hinglish/Roman script) for billing items.

PERSONALITY:
- You are a helpful female AI assistant named Vyamit AI
- Respond to greetings warmly: "Namaste! Main Vyamit AI hoon, aapki sahayak."
- Be friendly and conversational in Hinglish (Latin script only)
- Always give response in short sentences

CUSTOMER NAME EXTRACTION:
- If user says "customer [name]" or "naam [name]", extract it
- If NO customer name mentioned, use "Walk-in" as default

INVENTORY: {inventory_json}
USER SAID: "{user_text}"

RULES:
1. If user mentions price with item: Extract price, calculate total
2. If item is in inventory: Use inventory price
3. If item NOT in inventory AND no price mentioned: Ask for price
4. For greetings: Respond warmly, return type "GREETING"

OUTPUT JSON FORMAT:
{{
  "type": "BILL" or "ERROR" or "GREETING",
  "customer_name": "Customer Name or Walk-in",
  "items": [ {{"name": "ItemName", "qty_display": "1kg", "rate": 50.0, "total": 50.0, "unit": "kg"}} ],
  "msg": "Response in Hinglish (Latin script only)",
  "should_stop": false
}}

Examples:
- "hello" → {{"type": "GREETING", "customer_name": "Walk-in", "items": [], "msg": "Namaste! Main Vyamit AI hoon. Kaise madad kar sakti hoon?"}}
- "2kg chawal" → {{"type": "BILL", "customer_name": "Walk-in", "items": [{{"name": "chawal", "qty_display": "2kg", "rate": 120.0, "total": 240.0, "unit": "kg"}}], "msg": "Saaman Bill mein jod diya gaya hai"}}

Respond with ONLY the JSON format:"""

    def process_with_gemini(self, prompt: str) -> str:
        """Process using Gemini API"""
        try:
            # Use a stable Gemini model
            model = self.genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            raise

    def process_with_huggingface(self, prompt: str) -> str:
        """Process using Hugging Face API (placeholder - currently returns fallback)"""
        # Since HF API is having issues, return structured fallback
        user_input = prompt.split('USER SAID: "')[-1].split('"')[0].lower()
        
        if any(greeting in user_input for greeting in ['hello', 'hi', 'namaste']):
            return '{"type": "GREETING", "customer_name": "Walk-in", "items": [], "msg": "Namaste! Main Vyamit AI hoon. Kaise madad kar sakti hoon?", "should_stop": false}'
        else:
            return '{"type": "ERROR", "customer_name": "Walk-in", "items": [], "msg": "Samajh nahi aaya, phir se boliye", "should_stop": false}'

    def get_fallback_response(self, user_text: str) -> str:
        """Enhanced rule-based fallback with better item recognition"""
        user_lower = user_text.lower()
        
        # Extract customer name if present
        customer_name = "Walk-in"
        if "customer" in user_lower:
            parts = user_text.split()
            try:
                customer_idx = [p.lower() for p in parts].index("customer")
                if customer_idx + 1 < len(parts):
                    customer_name = " ".join(parts[customer_idx + 1:customer_idx + 3]).title()
            except:
                pass
        
        # Handle greetings
        if any(greeting in user_lower for greeting in ['hello', 'hi', 'namaste', 'helo']):
            return f'{{"type": "GREETING", "customer_name": "{customer_name}", "items": [], "msg": "Namaste! Main Vyamit AI hoon. Kaise madad kar sakti hoon?", "should_stop": false}}'
        
        # Handle common items with quantity extraction
        items_map = {
            'chawal': {'name': 'chawal', 'rate': 120.0, 'unit': 'kg'},
            'rice': {'name': 'chawal', 'rate': 120.0, 'unit': 'kg'},
            'maggie': {'name': 'maggie', 'rate': 5.0, 'unit': 'pic'},
            'noodles': {'name': 'maggie', 'rate': 5.0, 'unit': 'pic'},
            'sugar': {'name': 'sugar', 'rate': 45.0, 'unit': 'kg'},
            'cheeni': {'name': 'sugar', 'rate': 45.0, 'unit': 'kg'},
            'oil': {'name': 'oil', 'rate': 150.0, 'unit': 'litre'},
            'tel': {'name': 'oil', 'rate': 150.0, 'unit': 'litre'},
            'atta': {'name': 'atta', 'rate': 40.0, 'unit': 'kg'}
        }
        
        # Find matching item
        found_item = None
        for item_key, item_data in items_map.items():
            if item_key in user_lower:
                found_item = item_data
                break
        
        if found_item:
            # Extract quantity (simple regex-like approach)
            import re
            qty_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|pic|litre|liter)', user_lower)
            if qty_match:
                qty = float(qty_match.group(1))
                qty_display = qty_match.group(0)
            else:
                qty = 1.0
                qty_display = f"1{found_item['unit']}"
            
            # Check for custom price in user input
            price_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:rs|rupay|rupee)', user_lower)
            if price_match:
                rate = float(price_match.group(1))
            else:
                rate = found_item['rate']
            
            total = qty * rate
            
            return f'{{"type": "BILL", "customer_name": "{customer_name}", "items": [{{"name": "{found_item["name"]}", "qty_display": "{qty_display}", "rate": {rate}, "total": {total}, "unit": "{found_item["unit"]}"}}], "msg": "Saaman Bill mein jod diya gaya hai", "should_stop": false}}'
        
        # Item not found
        return f'{{"type": "ERROR", "customer_name": "{customer_name}", "items": [], "msg": "Samajh nahi aaya, phir se boliye", "should_stop": false}}'

    def process_voice_command(self, user_text: str, inventory: List[Item], user_id: str = "default") -> Dict[str, Any]:
        """Process voice command using hybrid approach"""
        print(f"\n🎤 Processing Voice with Hybrid Service: {user_text}")
        
        # Filter inventory
        filtered_inventory = [item for item in inventory if item.price > 0]
        print(f"📦 Total Inventory Items: {len(inventory)}")
        print(f"✅ Items with Price > 0: {len(filtered_inventory)}")
        
        # Prepare inventory JSON
        inventory_list = []
        for item in filtered_inventory:
            names_array = json.loads(item.names) if isinstance(item.names, str) else item.names
            inventory_list.append({
                "names": names_array,
                "price": item.price,
                "unit": item.unit,
                "category": item.category
            })
        
        inventory_json = json.dumps(inventory_list, ensure_ascii=False)
        context = self.memory.get_context_string()
        prompt = self.get_master_prompt(user_text, inventory_json, context)
        
        # Add user message to memory
        self.memory.add_user_message(user_text)
        
        # Try services in order of preference
        response_text = None
        service_used = "fallback"
        
        # Try Gemini first if available
        if self.gemini_available:
            try:
                print("🔄 Trying Gemini API...")
                response_text = self.process_with_gemini(prompt)
                service_used = "gemini"
                print("✅ Gemini API successful")
            except Exception as e:
                print(f"⚠️ Gemini failed: {e}")
        
        # Try Hugging Face if Gemini failed and HF is available
        if not response_text and self.hf_available:
            try:
                print("🔄 Trying Hugging Face API...")
                response_text = self.process_with_huggingface(prompt)
                service_used = "huggingface"
                print("✅ Hugging Face API successful")
            except Exception as e:
                print(f"⚠️ Hugging Face failed: {e}")
        
        # Use fallback if all else fails
        if not response_text:
            print("🔄 Using enhanced rule-based fallback...")
            response_text = self.get_fallback_response(user_text)
            service_used = "fallback"
            print("✅ Enhanced fallback response generated")
        
        try:
            # Clean and parse JSON response
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # Find JSON in response
            json_start = clean_text.find('{')
            json_end = clean_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                clean_text = clean_text[json_start:json_end]
            
            result = json.loads(clean_text)
            
            # Add service info to result
            result["_service_used"] = service_used
            
            # Add AI response to memory
            self.memory.add_assistant_message(result.get("msg", ""))
            
            print(f"✅ SUCCESS! Processed with {service_used}")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Raw response: {response_text}")
            return {
                "type": "ERROR",
                "customer_name": "Walk-in",
                "items": [],
                "msg": "Samajh nahi aaya, phir se boliye",
                "should_stop": False,
                "_service_used": service_used
            }
            
        except Exception as e:
            print(f"❌ Processing Error: {e}")
            return {
                "type": "ERROR",
                "customer_name": "Walk-in", 
                "items": [],
                "msg": "System error, kripaya baad mein try kariye",
                "should_stop": False,
                "_service_used": "error"
            }

    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get formatted chat history"""
        return self.memory.get_history()

    def clear_chat_history(self):
        """Clear conversation memory"""
        self.memory.clear()
        print("🧹 Chat history cleared")

    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            "service": "Hybrid AI Service",
            "primary_service": self.primary_service,
            "huggingface_available": self.hf_available,
            "gemini_available": self.gemini_available,
            "memory_enabled": True,
            "chat_history_available": True,
            "max_messages": self.memory.max_messages,
            "current_messages": len(self.memory.messages)
        }