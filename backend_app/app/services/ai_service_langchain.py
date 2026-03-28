import os
import json
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from app.db.models import Item

class LangChainAIService:
    def __init__(self):
        # Get Hugging Face API token
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            raise ValueError("❌ ERROR: HUGGINGFACE_API_TOKEN is missing!")
        
        # Set environment variable for LangChain
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = self.api_token
        
        # Initialize the model - Using Google Gemma 3 27B IT as requested
        self.llm = HuggingFaceEndpoint(
            repo_id="google/gemma-2-27b-it",
            task="text-generation",
            max_new_tokens=1024,
            temperature=0.3,
            repetition_penalty=1.1,
            return_full_text=False,
            huggingfacehub_api_token=self.api_token
        )
        
        # Wrap with ChatHuggingFace for better conversation handling
        self.chat_model = ChatHuggingFace(llm=self.llm)
        
        # Initialize embeddings for future RAG capabilities
        self.embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=self.api_token,
            model_name="BAAI/bge-base-en-v1.5"
        )
        
        # Initialize conversation memory for chat history
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True,
            memory_key="chat_history"
        )
        
        print("✅ LangChain AI Service initialized with Gemma-2-27B-IT")

    def get_master_prompt(self, user_text: str, inventory_json: str) -> str:
        """Master prompt for Vyamit AI - optimized for Hugging Face models"""
        return f"""You are Vyamit AI, a female voice assistant for "Vyamit AI App". Detect the language user is speaking and answer ONLY in that language but use Latin Script (Hinglish/Roman script) for billing items. Use Devanagari script only for response questions.

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

    def process_voice_command(self, user_text: str, inventory: List[Item], user_id: str = "default") -> Dict[str, Any]:
        """Process voice command using LangChain + Hugging Face"""
        print(f"\n🎤 Processing Voice with LangChain: {user_text}")
        
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
        
        # Get the master prompt
        prompt = self.get_master_prompt(user_text, inventory_json)
        
        try:
            # Add user message to memory
            self.memory.chat_memory.add_user_message(user_text)
            
            # Get response from the model
            print("🔄 Calling Hugging Face API...")
            response = self.chat_model.invoke([HumanMessage(content=prompt)])
            
            # Extract response content
            response_text = response.content if hasattr(response, 'content') else str(response)
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
            self.memory.chat_memory.add_ai_message(result.get("msg", ""))
            
            print("✅ SUCCESS! LangChain processing completed.")
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
            print(f"❌ LangChain Error: {e}")
            return {
                "type": "ERROR",
                "customer_name": "Walk-in", 
                "items": [],
                "msg": "System error, kripaya baad mein try kariye",
                "should_stop": False
            }

    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get formatted chat history"""
        messages = self.memory.chat_memory.messages
        history = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        
        return history

    def clear_chat_history(self):
        """Clear conversation memory"""
        self.memory.clear()
        print("🧹 Chat history cleared")

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts (for future RAG features)"""
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            print(f"❌ Embedding Error: {e}")
            return []

    def search_similar_items(self, query: str, inventory: List[Item], top_k: int = 5) -> List[Item]:
        """Search similar items using embeddings (future feature)"""
        try:
            # Get query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # This is a placeholder for future RAG implementation
            # You would store item embeddings in a vector database
            # and perform similarity search
            
            return inventory[:top_k]  # For now, return first k items
            
        except Exception as e:
            print(f"❌ Search Error: {e}")
            return inventory[:top_k]