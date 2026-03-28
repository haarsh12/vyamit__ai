from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from app.db.database import get_session
from app.db.models import Item
from app.services.ai_service import AIService
from app.api.items import get_current_user # Re-use the login logic

router = APIRouter()
ai_service = AIService()

class VoiceRequest(BaseModel):
    text: str

class PremiumVoiceRequest(BaseModel):
    transcript: str
    user_id: int
    inventory: List[Dict[str, Any]]

@router.post("/process")
def process_voice(
    request: VoiceRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(get_current_user)
):
    """
    Legacy endpoint - Receives text from the App -> Fetches Inventory -> Calls AI -> Returns Bill JSON
    """
    # 1. Get THIS user's inventory
    statement = select(Item).where(Item.owner_id == user_id)
    inventory = session.exec(statement).all()
    
    # 2. Call the AI Service
    ai_response = ai_service.process_voice_command(request.text, inventory)
    
    return ai_response

@router.post("/process-query")
def process_query(request: PremiumVoiceRequest):
    """
    Process a query (question) from the user
    Returns answer and whether to continue listening
    """
    try:
        # Detect query type
        transcript_lower = request.transcript.lower()
        
        # Check if it's a price query
        if any(word in transcript_lower for word in ['kitna', 'price', 'rate', 'cost', 'kya hai']):
            # Extract item name from query
            item_name = _extract_item_from_query(transcript_lower)
            
            if item_name:
                # Find item in inventory
                matching_item = None
                for item in request.inventory:
                    if any(item_name in name.lower() for name in item.get('names', [])):
                        matching_item = item
                        break
                
                if matching_item:
                    answer = f"{matching_item['names'][0]} ka price hai {matching_item['price']} rupaye per {matching_item['unit']}"
                    
                    # Check if query includes billing intent
                    if any(word in transcript_lower for word in ['de do', 'dena', 'chahiye', 'add']):
                        # Continue listening for billing
                        return {
                            "success": True,
                            "answer": answer,
                            "continue_listening": True,
                            "mode": "billing"
                        }
                    else:
                        # Just answer, stop listening
                        return {
                            "success": True,
                            "answer": answer,
                            "continue_listening": False,
                            "mode": "query"
                        }
                else:
                    answer = f"{item_name} inventory mein nahi hai"
                    return {
                        "success": True,
                        "answer": answer,
                        "continue_listening": False,
                        "mode": "query"
                    }
        
        # Generic query - use AI
        answer = "Kripya apna sawal dobara puchiye"
        return {
            "success": True,
            "answer": answer,
            "continue_listening": False,
            "mode": "query"
        }
        
    except Exception as e:
        print(f"Query processing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "continue_listening": False
        }

@router.post("/process-billing")
def process_billing(request: PremiumVoiceRequest):
    """
    Process billing transcript
    Returns bill updates
    """
    try:
        # Use AI service to parse billing items
        inventory_items = []
        for item_data in request.inventory:
            # Create mock Item objects for AI service
            item = type('Item', (), {
                'id': item_data.get('id'),
                'names': item_data.get('names', []),
                'price': item_data.get('price'),
                'unit': item_data.get('unit'),
                'category': item_data.get('category', '')
            })()
            inventory_items.append(item)
        
        # Process with AI
        ai_response = ai_service.process_voice_command(request.transcript, inventory_items)
        
        # Extract bill items
        bill_updates = []
        if ai_response.get('success') and 'bill' in ai_response:
            for item in ai_response['bill']:
                bill_updates.append({
                    'name': item.get('item_name'),
                    'quantity': item.get('quantity', 1.0),
                    'unit': item.get('unit', ''),
                    'price': item.get('price_per_unit', 0.0),
                    'total': item.get('total_price', 0.0)
                })
        
        return {
            "success": True,
            "bill_updates": bill_updates,
            "total_items": len(bill_updates)
        }
        
    except Exception as e:
        print(f"Billing processing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "bill_updates": []
        }

def _extract_item_from_query(query: str) -> Optional[str]:
    """Extract item name from query"""
    # Remove common query words
    remove_words = ['kitna', 'kya', 'hai', 'ka', 'ki', 'ke', 'price', 'rate', 'cost', 'batao', 'bata', 'do']
    
    words = query.split()
    item_words = [w for w in words if w not in remove_words and len(w) > 1]
    
    if item_words:
        return ' '.join(item_words)
    
    return None