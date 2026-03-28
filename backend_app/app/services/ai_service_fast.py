import google.generativeai as genai
import os
import json
from app.db.models import Item
from typing import List, Dict, Any, Optional

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("\n❌ ERROR: GEMINI_API_KEY is missing!\n")
else:
    genai.configure(api_key=api_key, transport="rest")

class AIServiceFast:
    def __init__(self):
        # FAST models prioritized
        self.candidate_models = [
            "gemini-2.0-flash-exp",      # Fastest experimental
            "gemini-flash-2.0",          # Fast stable
            "gemini-2.0-flash-001"       # Alternative fast
        ]

    def process_voice_command(
        self, 
        user_text: str, 
        inventory: List[Item],
        dashboard_data: Optional[Dict[str, Any]] = None,
        recent_bills: Optional[List[Dict[str, Any]]] = None
    ):
        print(f"\n🎤 Processing Voice: {user_text}")
        
        # Filter inventory
        filtered_inventory = [item for item in inventory if item.price > 0]
        print(f"📦 Items: {len(filtered_inventory)}")
        
        # MINIMAL Inventory
        inventory_list = []
        for item in filtered_inventory:
            names_array = json.loads(item.names) if isinstance(item.names, str) else item.names
            inventory_list.append({
                "names": names_array,
                "price": item.price,
                "unit": item.unit
            })
        
        inventory_json = json.dumps(inventory_list, ensure_ascii=False)
        
        # MINIMAL analytics
        analytics_context = ""
        if dashboard_data and recent_bills:
            top_items_str = ', '.join([item['name'] for item in dashboard_data.get('top_selling_items', [])])
            last_bill_amt = recent_bills[0]['total_amount'] if recent_bills else 0
            last_bill_cust = recent_bills[0]['customer_name'] if recent_bills else 'N/A'
            
            analytics_context = f"""
DATA: Revenue ₹{dashboard_data.get('summary', {}).get('total_revenue', 0)}, Bills {dashboard_data.get('summary', {}).get('total_bills', 0)}, Top: {top_items_str}, Last: ₹{last_bill_amt} ({last_bill_cust})
"""
        
        # ULTRA-COMPACT PROMPT
        prompt = f"""Vyamit AI voice assistant. Hinglish (Latin script).

CUSTOMER: Extract from "customer [name]" or "naam [name]". Default: "Walk-in"

INVENTORY: {inventory_json}
{analytics_context}
USER: "{user_text}"

RULES:
1. Price mentioned → Extract, calculate, add to bill
2. Item in inventory → Use inventory price
3. Multiple items, one missing → Add known to "items", ask in "msg", type: "BILL"
4. One item, not in inventory, no price → Ask price, type: "ERROR"
5. Greeting → type: "GREETING"
6. Business query → Use data, type: "QUERY"

JSON OUTPUT:
{{"type": "BILL/ERROR/GREETING/QUERY", "customer_name": "Name", "items": [{{"name": "Item", "qty_display": "1kg", "rate": 50.0, "total": 50.0, "unit": "kg"}}], "msg": "Short Hinglish"}}

If OK: msg "Saaman Bill mein jod diya gaya hai"

EXAMPLES:
- "customer raju 5rs wali 6 maggie" → {{"type": "BILL", "customer_name": "Raju", "items": [{{"name": "Maggie", "qty_display": "6pic", "rate": 5.0, "total": 30.0, "unit": "pic"}}], "msg": "Raju ke liye 6 Maggie add"}}
- "1kg chawal aur aam" → {{"type": "BILL", "items": [{{"name": "Chawal", ...}}], "msg": "Chawal add. Aam ki keemat?"}}
- "hello" → {{"type": "GREETING", "items": [], "msg": "Namaste! Main Vyamit AI"}}"""

        # Try fast models
        for model_name in self.candidate_models:
            try:
                print(f"🔄 {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                print(f"✅ {model_name} worked")
                
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_text)
                
            except Exception as e:
                print(f"⚠️ {model_name} failed: {e}")
                continue
        
        print(f"\n❌ ALL MODELS FAILED\n")
        return {
            "type": "ERROR",
            "items": [],
            "msg": "System error", 
            "should_stop": False
        }
