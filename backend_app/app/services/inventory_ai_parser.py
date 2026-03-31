import json
import re
from transformers import pipeline
from typing import List, Dict, Any

# Import the robust rule-based fallback we previously created
from app.services.inventory_parser import parse_inventory

# STEP 1: Initialize the pipeline globally so it stays in memory (FastAPI ready)
# Using the lightweight model requested for max speed
ai_parser = pipeline("text2text-generation", model="google/flan-t5-small")

UNIT_MAP = {
    "kilo": "kg",
    "kg": "kg",
    "gram": "g",
    "gm": "g",
    "packets": "packet",
    "packet": "packet",
    "pcs": "piece",
    "piece": "piece"
}

ITEM_ALIASES = {
    "maggi": "noodles",
    "biscuit": "biscuits",
    "dairy milk": "chocolate"
}

def clean_json_output(text: str) -> str:
    """Cleans up common JSON formatting issues from LLM output."""
    # Fix single quotes -> double quotes
    text = text.replace("'", '"')
    # Remove trailing commas before closing brackets/braces
    text = re.sub(r",\s*([\]}])", r"\1", text)
    return text

def normalize_unit(unit: str) -> str:
    """Normalizes various unit strings into standard forms."""
    if not unit:
        return ""
    unit_lower = unit.lower().strip()
    return UNIT_MAP.get(unit_lower, unit_lower)

def normalize_item(name: str) -> str:
    """Normalizes item names into standard taxonomy items."""
    if not name:
        return ""
    name_lower = name.lower().strip()
    return ITEM_ALIASES.get(name_lower, name_lower)

def post_process(items: list) -> list:
    """Post-processes parsed JSON list of items."""
    processed = []
    
    if not isinstance(items, list):
        return processed
        
    for item in items:
        # Validate each item type
        if not isinstance(item, dict):
            continue
            
        name = item.get("item", "")
        qty = item.get("quantity", 0)
        unit = item.get("unit", "")
        
        # Convert quantity to int safely
        try:
            qty = int(float(qty))
        except (ValueError, TypeError):
            continue
            
        # Normalize unit and item
        norm_name = normalize_item(name)
        norm_unit = normalize_unit(unit)
        
        # Remove invalid entries
        if not norm_name or qty <= 0:
            continue
            
        processed.append({
            "item": norm_name,
            "quantity": qty,
            "unit": norm_unit
        })
        
    return processed

def parse_inventory_ai(text: str) -> List[Dict[str, Any]]:
    """Generates structured inventory items using a lightweight LLM."""
    prompt = (
        "Convert this kirana shop sentence into a JSON list of items. Format exactly like the examples.\n"
        "Input: '2 kg sugar 3 maggi'\n"
        "Output: [{\"item\":\"sugar\",\"quantity\":2,\"unit\":\"kg\"},{\"item\":\"maggi\",\"quantity\":3,\"unit\":\"packet\"}]\n"
        "Input: 'bhaiya ek dairy milk aur 2 biscuit'\n"
        "Output: [{\"item\":\"dairy milk\",\"quantity\":1,\"unit\":\"piece\"},{\"item\":\"biscuit\",\"quantity\":2,\"unit\":\"packet\"}]\n"
        f"Input: '{text}'\n"
        "Output:"
    )
    
    try:
        # Optimization: limit max_new_tokens, do_sample=False
        result = ai_parser(prompt, max_new_tokens=100, do_sample=False)
        output_text = result[0]['generated_text'].strip()
        
        cleaned_text = clean_json_output(output_text)
        parsed_items = json.loads(cleaned_text)
        
        return post_process(parsed_items)
        
    except json.JSONDecodeError:
        # T5-small often hallucinates slightly broken JSON; catch it efficiently
        return []
    except Exception as e:
        print(f"AI Parse Error: {e}")
        return []

def is_low_confidence(items: List[Dict[str, Any]]) -> bool:
    """
    Confidence Check
    Return True if the items list is empty, broken, or missing essential keys.
    """
    # Empty list check
    if not items or len(items) == 0:
        return True
        
    for item in items:
        # Invalid types check
        if not isinstance(item, dict):
            return True
            
        name = item.get("item")
        qty = item.get("quantity")
        unit = item.get("unit")
        
        # Missing keys or invalid name length
        if not name or not isinstance(name, str) or len(name) < 2:
            return True
            
        # Quantity <= 0 or invalid type check
        if qty is None or not isinstance(qty, int) or qty <= 0:
            return True
            
        # Unit missing or invalid
        if not unit or not isinstance(unit, str):
            return True
            
    # All confidence checks passed!
    return False

def smart_parse(text: str) -> List[Dict[str, Any]]:
    """
    Primary logic prioritizing AI, cascading to Rule-based on failure.
    """
    print("Using AI parser")
    ai_result = parse_inventory_ai(text)
    
    if is_low_confidence(ai_result):
        print("AI output invalid -> fallback triggered")
        print("Using rule-based parser")
        return parse_inventory(text)
    
    return ai_result

if __name__ == "__main__":
    test_inputs = [
        "give 1 dairy milk and 2 biscuits",  # Clean input
        "bhaiya 2 kg sugar aur 3 maggi dena",  # Messy Hinglish input
        "kuch bhi mat dena",  # Edge case: no valid items
        "thoda sa 5 kilo chawal aur 2 packet chips",  # Normal input
        "100",  # Edge case: garbage input
        "[{'item': 'broken json', }]",  # Edge case: problematic chars handled by cleaning
    ]
    
    print("====== AI-First Smart Parser Tests ======\n")
    for text in test_inputs:
        print(f"Input:    \"{text}\"")
        result = smart_parse(text)
        print(f"Output:   {json.dumps(result, indent=2)}")
        print("-" * 50)
