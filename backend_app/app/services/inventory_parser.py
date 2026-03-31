import re
import string
from typing import List, Dict, Any, Optional

NOISE_WORDS = {
    "give", "me", "please", "bhai", "bhaiya", "dena", 
    "aur", "and", "to"
}

NUMBER_MAP = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, 
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "ek": 1, "do": 2, "teen": 3, "chaar": 4, "paanch": 5
}

UNIT_MAP = {
    "kg": "kg", "kilo": "kg", "kilogram": "kg", "kgs": "kg", "kilos": "kg",
    "gm": "g", "gram": "g", "grams": "g", "gms": "g",
    "packet": "packet", "packets": "packet", "pkt": "packet",
    "piece": "piece", "pieces": "piece", "pcs": "piece", "pc": "piece"
}

def normalize_text(text: str) -> List[str]:
    """
    Convert text to lowercase, apply digit separation,
    strip out punctuation, and cleanly remove generic filler words.
    """
    text = text.lower()
    
    # Add spaces around numbers so glued inputs like '2kg' safely split to '2' and 'kg'
    text = re.sub(r'(\d+)', r' \1 ', text)
    
    # Strip punctuation by replacing with space
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    
    tokens = text.split()
    
    # Keep non-noise words
    return [t for t in tokens if t not in NOISE_WORDS]

def normalize_numbers(token: str) -> Optional[int]:
    """Return integer if token resolves to a recognizable number."""
    if token.isdigit():
        return int(token)
    return NUMBER_MAP.get(token)

def normalize_units(token: str) -> Optional[str]:
    """Map localized abbreviations to pure base units, else return None."""
    return UNIT_MAP.get(token)

def parse_inventory(text: str) -> List[Dict[str, Any]]:
    """
    Core algorithm for rule-based, fully offline parsing.
    Identifies bounds of items efficiently based on changes in
    sequence continuity related to quantities and units.
    """
    tokens = normalize_text(text)
    
    items = []
    current_item = {"quantity": None, "unit": None, "words": []}
    
    # A crucial state tracking flag.
    # If we have absorbed words -> then found a quantity/unit -> and later see MORE words,
    # those new words denote a completely NEW item entry boundary.
    has_seen_number_or_unit_after_words = False
    
    def save_current_item():
        if not current_item["words"]:
            return  # Skip saving empty/invalid parsed sets
            
        qty = current_item["quantity"] if current_item["quantity"] is not None else 1
        unit = current_item["unit"] if current_item["unit"] is not None else "piece"
        item_name = " ".join(current_item["words"]).strip()
            
        items.append({
            "item": item_name,
            "quantity": qty,
            "unit": unit
        })
        
    for tok in tokens:
        num_val = normalize_numbers(tok)
        unit_val = normalize_units(tok)
        
        if num_val is not None:
            # Entering new number! If we already had a number stored, that triggers boundary.
            if current_item["quantity"] is not None:
                save_current_item()
                current_item = {"quantity": num_val, "unit": None, "words": []}
                has_seen_number_or_unit_after_words = False
            else:
                current_item["quantity"] = num_val
                if current_item["words"]:
                    has_seen_number_or_unit_after_words = True
                    
        elif unit_val is not None:
            # Entering new unit! If we already had a unit stored, triggers boundary.
            if current_item["unit"] is not None:
                save_current_item()
                current_item = {"quantity": None, "unit": unit_val, "words": []}
                has_seen_number_or_unit_after_words = False
            else:
                current_item["unit"] = unit_val
                if current_item["words"]:
                    has_seen_number_or_unit_after_words = True
                    
        else:
            # Entering standard text word!
            if has_seen_number_or_unit_after_words:
                # We saw Words -> Quantity/Unit -> Words. Triggers boundary.
                # Valid Kirana Example: "sugar 2 kg maggi" where "maggi" breaks it here.
                save_current_item()
                current_item = {"quantity": None, "unit": None, "words": [tok]}
                has_seen_number_or_unit_after_words = False
            else:
                # Standard appending logic for continuous nouns (e.g., 'dairy' + 'milk')
                current_item["words"].append(tok)
                
    # Close out and save final buffered object at line end
    save_current_item()
    
    return items

if __name__ == "__main__":
    import json
    
    test_cases = [
        "bhaiya 2 kg sugar 3 maggi aur ek dairy milk dena",
        "give 3 biscuit and 1 oil bottle",
        "sugar 2 kilo aur maggi 3 dena",
        "atta flour 5 kg",
        "10 packet chips aur 500 gm dal"
    ]
    
    print("====== Kirana Scanner NLP Core Test ======\n")
    for tc in test_cases:
        print(f"Input:    \"{tc}\"")
        result = parse_inventory(tc)
        print(f"Output:   {json.dumps(result, indent=2)}\n")
        print("-" * 50)
