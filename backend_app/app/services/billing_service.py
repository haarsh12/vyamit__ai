from typing import List, Dict, Any, Optional

# STEP 5: Optional integration
# Importing the smart parser we previously built
from app.services.inventory_ai_parser import smart_parse

# STEP 1: Create product database (RAG base)
PRODUCT_DB = [
    {"name": "noodles", "price": 14, "unit": "packet"},
    {"name": "chocolate", "price": 20, "unit": "piece"},
    {"name": "sugar", "price": 45, "unit": "kg"},
    {"name": "rice", "price": 60, "unit": "kg"},
    {"name": "biscuits", "price": 10, "unit": "packet"},
    {"name": "chips", "price": 20, "unit": "packet"}
]

# STEP 2: Retrieval function (RAG logic)
def get_product(item_name: str) -> Optional[Dict[str, Any]]:
    """
    Search PRODUCT_DB for a matching product.
    Uses simple matching (contains or equals).
    """
    if not item_name:
        return None
        
    item_name_lower = item_name.lower().strip()
    
    # Try exact match first
    for product in PRODUCT_DB:
        if product["name"] == item_name_lower:
            return product
            
    # Try contains match if exact fails
    for product in PRODUCT_DB:
        if product["name"] in item_name_lower or item_name_lower in product["name"]:
            return product
            
    return None

# STEP 3: Enrich items
def enrich_items(parsed_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich parsed items with pricing information from the product database.
    """
    enriched = []
    
    for item in parsed_items:
        # Clone item to avoid mutating original list
        enriched_item = dict(item)
        item_name = enriched_item.get("item", "")
        quantity = enriched_item.get("quantity", 0)
        
        product = get_product(item_name)
        
        if product:
            # Override unit from DB and add price/total
            enriched_item["unit"] = product["unit"]
            enriched_item["price"] = product["price"]
            enriched_item["total"] = quantity * product["price"]
            enriched_item["found"] = True
        else:
            # If not found, keep item but set price and total to 0
            enriched_item["price"] = 0
            enriched_item["total"] = 0
            enriched_item["found"] = False
            
        enriched.append(enriched_item)
        
    return enriched

# STEP 4: Generate bill
def generate_bill(parsed_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate the final bill given the parsed items.
    """
    enriched_items = enrich_items(parsed_items)
    
    # Sum all totals -> grand_total
    total_sum = sum(item.get("total", 0) for item in enriched_items)
    
    # List all item names that were not found in the product DB
    unknown_items = [item.get("item", "") for item in enriched_items if not item.get("found", True)]
    
    return {
        "items": enriched_items,
        "grand_total": total_sum,
        "unknown_items": unknown_items
    }

# Helper wrapper
def process_text_to_bill(text: str) -> Dict[str, Any]:
    """
    Processes raw text, parses it, and computes the final bill.
    """
    parsed_items = smart_parse(text)
    return generate_bill(parsed_items)

# STEP 7: Testing
if __name__ == "__main__":
    import json
    
    test_inputs = [
        "2 maggi and 1 dairy milk",
        "3 biscuit and 2 chips",
        "5 kg rice and 1 chocolate",
        "2 unknownitem and 1 maggi"
    ]
    
    print("====== Kirana Billing System Tests ======\n")
    for text in test_inputs:
        print(f"Input:    \"{text}\"")
        bill = process_text_to_bill(text)
        print(f"Output:   {json.dumps(bill, indent=2)}\n")
        print("-" * 50)
