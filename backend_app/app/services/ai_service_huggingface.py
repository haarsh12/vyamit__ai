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

class HuggingFaceAIService:
    def __init__(self):
        # Get Hugging Face API token
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            raise ValueError("❌ ERROR: HUGGINGFACE_API_TOKEN is missing!")
        
        # Multiple model options (using new router endpoint)
        self.model_options = [
            {
                "name": "microsoft/DialoGPT-medium",
                "url": "https://router.huggingface.co/models/microsoft/DialoGPT-medium",
                "type": "conversational"
            },
            {
                "name": "google/flan-t5-base", 
                "url": "https://router.huggingface.co/models/google/flan-t5-base",
                "type": "text2text"
            },
            {
                "name": "microsoft/DialoGPT-small",
                "url": "https://router.huggingface.co/models/microsoft/DialoGPT-small", 
                "type": "conversational"
            }
        ]
        
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        self.current_model = None
        
        # Initialize chat memory
        self.memory = ChatMemory(max_messages=20)
        
        # Test and select working model
        self._select_working_model()
        
        print(f"✅ Hugging Face AI Service initialized with {self.current_model['name']}")

    def _select_working_model(self):
        """Test models and select the first working one"""
        for model in self.model_options:
            try:
                print(f"🔄 Testing model: {model['name']}...")
                
                # Simple test query
                test_payload = {
                    "inputs": "Hello",
                    "parameters": {"max_new_tokens": 10}
                }
                
                response = requests.post(
                    model["url"], 
                    headers=self.headers, 
                    json=test_payload, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.current_model = model
                    print(f"✅ Selected working model: {model['name']}")
                    return
                else:
                    print(f"⚠️ Model {model['name']} not available: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️ Model {model['name']} test failed: {e}")
                continue
        
        # If no model works, use the first one anyway
        self.current_model = self.model_options[0]
        print(f"⚠️ No models responded, using fallback: {self.current_model['name']}")

    def get_master_prompt(self, user_text: str, inventory_json: str, context: str = "") -> str:
        """Master prompt for Vyamit AI - simplified for better model compatibility"""
        return f"""You are Vyamit AI, a helpful assistant for a grocery store billing system.

Context: {context}

Available inventory: {inventory_json}

User said: "{user_text}"

Rules:
1. For greetings (hello, hi, namaste): Respond warmly and return type "GREETING"
2. For billing items: Extract item name, quantity, and calculate total
3. If item not in inventory: Ask for price
4. Always respond in JSON format

Required JSON format:
{{
  "type": "BILL" or "ERROR" or "GREETING",
  "customer_name": "Walk-in",
  "items": [],
  "msg": "Your response message",
  "should_stop": false
}}

Examples:
- "hello" → {{"type": "GREETING", "customer_name": "Walk-in", "items": [], "msg": "Namaste! Main Vyamit AI hoon. Kaise madad kar sakti hoon?"}}
- "2kg rice" → {{"type": "BILL", "customer_name": "Walk-in", "items": [{{"name": "rice", "qty_display": "2kg", "rate": 120.0, "total": 240.0, "unit": "kg"}}], "msg": "Bill mein add kar diya"}}

Respond with only JSON:"""

    def get_master_prompt(self, user_text: str, inventory_json: str, context: str = "") -> str:
        """Master prompt for Vyamit AI - optimized for Hugging Face models"""
        return f"""{context}You are Vyamit AI, a female voice assistant for "Vyamit AI App". Detect the language user is speaking and answer ONLY in that language but use Latin Script (Hinglish/Roman script) for billing items. Use Devanagari script only for response questions.

PERSONALITY:
- You are a helpful female AI assistant named Vyamit AI
- Respond to greetings warmly: "Namaste! Main Vyamit AI hoon, aapki sahayak."
- If asked who you are: "Main Vyamit AI hoon, aapki voice assistant."
- Be friendly and conversational in Hinglish (Latin script only)
- Always give response in short sentences

CUSTOMER NAME EXTRACTION:
- If user says "customer [name]" or "naam [name]" or mentions a person's name, extract it
- Examples: "customer raju charde", "naam mohan hai", "ramesh ke liye"
- If NO customer name mentioned, use "Walk-in" as default
- Customer name should be in the "customer_name" field

INVENTORY (Only items with configured prices): {inventory_json}
USER SAID: "{user_text}"

CRITICAL RULES FOR PRICE HANDLING:
1. If user mentions price with item (e.g., "1kg chawal 120 rs kilo" or "5rs wali 6 maggie packet"):
   - EXTRACT the price from user's speech
   - CALCULATE total: quantity × price
   - ADD to bill immediately with that price

2. If item is in inventory (check all name variations):
   - Use inventory price
   - Calculate total correctly

3. If item NOT in inventory AND user did NOT mention price:
   - Ask: "[Item name] ki keemat kya hai?"
   - Return type: "ERROR" with this message

4. Match quantities correctly (1 kg, 2 litre, 5 pieces, etc.)

5. For greetings (hi, hello, namaste):
   - Respond warmly in Hinglish
   - Return type: "GREETING"

OUTPUT JSON FORMAT (STRICT):
{{
  "type": "BILL" or "ERROR" or "GREETING",
  "customer_name": "Customer Name or Walk-in",
  "items": [ {{"name": "ItemName", "qty_display": "1kg", "rate": 50.0, "total": 50.0, "unit": "kg"}} ],
  "msg": "Response in Hinglish (Latin script only, NO Devanagari, answer in short)",
  "should_stop": false
}}

If everything is fine with quantity, price and item and you have no questions then give response msg as "Saaman Bill mein jod diya gaya hai"

EXAMPLES:
- User: "customer raju charde 5rs wali 6 maggie packet" → {{"type": "BILL", "customer_name": "Raju Charde", "items": [{{"name": "Maggie", "qty_display": "6pic", "rate": 5.0, "total": 30.0, "unit": "pic"}}], "msg": "Raju Charde ke liye 6 Maggie packet bill mein add kar diya"}}
- User: "hello" → {{"type": "GREETING", "customer_name": "Walk-in", "items": [], "msg": "Namaste! Main Vyamit AI hoon. Kaise madad kar sakti hoon?"}}

Respond with ONLY the JSON format. No additional text."""

    def query_huggingface_api(self, prompt: str, max_retries: int = 2) -> str:
        """Query Hugging Face Inference API with retries"""
        if not self.current_model:
            raise Exception("No working model available")
            
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Calling {self.current_model['name']} (attempt {attempt + 1})...")
                response = requests.post(
                    self.current_model["url"], 
                    headers=self.headers, 
                    json=payload, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "")
                    elif isinstance(result, dict):
                        return result.get("generated_text", "")
                    else:
                        print(f"⚠️ Unexpected response format: {result}")
                        
                elif response.status_code == 503:
                    print(f"⚠️ Model loading (attempt {attempt + 1}), waiting...")
                    import time
                    time.sleep(5)  # Wait for model to load
                    continue
                    
                else:
                    print(f"❌ API Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                print(f"⚠️ Request timeout (attempt {attempt + 1})")
            except Exception as e:
                print(f"❌ Request error (attempt {attempt + 1}): {e}")
        
        # If API fails, return a simple fallback response
        print("⚠️ API failed, using fallback response")
        return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Generate a simple fallback response when API fails"""
        user_input = prompt.split('User said: "')[-1].split('"')[0].lower()
        
        if any(greeting in user_input for greeting in ['hello', 'hi', 'namaste']):
            return '{"type": "GREETING", "customer_name": "Walk-in", "items": [], "msg": "Namaste! Main Vyamit AI hoon. Kaise madad kar sakti hoon?", "should_stop": false}'
        else:
            return '{"type": "ERROR", "customer_name": "Walk-in", "items": [], "msg": "Samajh nahi aaya, phir se boliye", "should_stop": false}'

    def process_voice_command(self, user_text: str, inventory: List[Item], user_id: str = "default") -> Dict[str, Any]:
        """Process voice command using Hugging Face API"""
        print(f"\n🎤 Processing Voice with Hugging Face: {user_text}")
        
        # Filter inventory to only include items with price > 0
        filtered_inventory = [item for item in inventory if item.price > 0]
        print(f"📦 Total Inventory Items: {len(inventory)}")
        print(f"✅ Items with Price > 0: {len(filtered_inventory)}")
        
        # Prepare Inventory with names array support
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
        
        # Get conversation context
        context = self.memory.get_context_string()
        
        # Get the master prompt
        prompt = self.get_master_prompt(user_text, inventory_json, context)
        
        try:
            # Add user message to memory
            self.memory.add_user_message(user_text)
            
            # Get response from Hugging Face API
            response_text = self.query_huggingface_api(prompt)
            print(f"🤖 Raw Response: {response_text}")
            
            # Clean and parse JSON response
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # Find JSON in response (sometimes models add extra text)
            json_start = clean_text.find('{')
            json_end = clean_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                clean_text = clean_text[json_start:json_end]
            
            result = json.loads(clean_text)
            
            # Add AI response to memory
            self.memory.add_assistant_message(result.get("msg", ""))
            
            print("✅ SUCCESS! Hugging Face processing completed.")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Raw response: {response_text}")
            return {
                "type": "ERROR",
                "customer_name": "Walk-in",
                "items": [],
                "msg": "Samajh nahi aaya, phir se boliye",
                "should_stop": False
            }
            
        except Exception as e:
            print(f"❌ Hugging Face Error: {e}")
            return {
                "type": "ERROR",
                "customer_name": "Walk-in", 
                "items": [],
                "msg": "System error, kripaya baad mein try kariye",
                "should_stop": False
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
            "service": "Hugging Face Direct API",
            "model": self.current_model["name"] if self.current_model else "None",
            "memory_enabled": True,
            "chat_history_available": True,
            "max_messages": self.memory.max_messages,
            "current_messages": len(self.memory.messages),
            "available_models": [m["name"] for m in self.model_options]
        }