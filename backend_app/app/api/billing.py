from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import time

from app.services.billing_service import process_text_to_bill

# Create router with Swagger tag
router = APIRouter(tags=["Billing"])

# Request model
class BillingRequest(BaseModel):
    text: str

# Response model: strongly typed with optional bonus 'success'
class BillingResponse(BaseModel):
    success: bool
    items: List[Dict[str, Any]]
    grand_total: int
    unknown_items: List[str]

# Health check endpoint
@router.get("/health")
def health_check():
    return {"status": "ok"}

# Create bill endpoint
@router.post("/voice-bill", response_model=BillingResponse)
def create_bill(request: BillingRequest):
    # Input validation
    input_text = request.text.strip() if request.text else ""
    
    if not input_text:
        raise HTTPException(status_code=400, detail="Text input is required and cannot be empty")

    try:
        # Logging
        print(f"Received request: {input_text}")
        
        start_time = time.time()

        # Core logic
        result = process_text_to_bill(input_text)
        
        if not result or not isinstance(result, dict):
            # Fallback to safe structure if service fails or returns invalid type
            result = {
                "items": [],
                "grand_total": 0,
                "unknown_items": []
            }
            
        end_time = time.time()
        print(f"Processing time: {end_time - start_time:.4f} seconds")
        
        # Add success indicator without mutating original dict
        final_result = {
            "success": True,
            **result
        }

        # Logging
        print(f"Parsed and billed result: {final_result}")

        return final_result

    except Exception as e:
        # Improve error handling
        print(f"Error processing bill request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Local testing
if __name__ == "__main__":
    import json
    
    sample_text = "5 kg rice and 2 unknownbrand"
    
    print("====== Local API Logic Test ======\n")
    print(f"Input:    \"{sample_text}\"")
    
    try:
        start_time = time.time()
        bill_result = process_text_to_bill(sample_text)
        
        if not bill_result or not isinstance(bill_result, dict):
            bill_result = {
                "items": [],
                "grand_total": 0,
                "unknown_items": []
            }
            
        end_time = time.time()
        print(f"Processing time: {end_time - start_time:.4f} seconds")
        
        final_result = {
            "success": True,
            **bill_result
        }
        
        print(f"Output:\n{json.dumps(final_result, indent=2)}")
    except Exception as e:
        print(f"Error executing local test: {e}")
