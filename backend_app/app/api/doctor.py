import os
import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai

router = APIRouter()

# Setup Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key, transport="rest")

class VoicePrescriptionRequest(BaseModel):
    text: str

class PrescriptionLine(BaseModel):
    medicine_name: str
    dosage_frequency_timing: str
    days: str

class SavePrescriptionRequest(BaseModel):
    items: List[PrescriptionLine]
    notes: Optional[str] = None

@router.post("/prescriptions/parse-voice")
def parse_voice(request: VoicePrescriptionRequest):
    if not api_key:
        # Fallback if no API key
        return {"items": []}
    
    prompt = f"""You are a medical AI assistant parsing a doctor's dictated prescription.
Extract the medicines and instructions into a JSON array of objects.
Each object must have:
- medicine_name (string)
- dosage_frequency_timing (string, e.g., '2 times daily after food' or '500 mg twice daily')
- days (string number, e.g., '5')

If no dosage or days are provided, use '—' and '1' respectively.

Doctor's text: "{request.text}"

Output strictly JSON with the format:
{{
  "items": [
    {{"medicine_name": "...", "dosage_frequency_timing": "...", "days": "..."}}
  ]
}}
"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash") # Use 1.5-flash as 2.5-flash might not be configured everywhere
        try:
             model = genai.GenerativeModel("gemini-2.5-flash") # Try 2.5 flash first
             response = model.generate_content(prompt)
        except Exception:
             model = genai.GenerativeModel("gemini-1.5-flash")
             response = model.generate_content(prompt)
             
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        return {"items": data.get("items", [])}
    except Exception as e:
        print(f"Error parsing prescription: {e}")
        return {"items": []}

@router.post("/prescriptions")
def save_prescription(request: SavePrescriptionRequest):
    # Mock saving prescription to Database
    print(f"Saved {len(request.items)} prescription lines. Notes: {request.notes}")
    return {"status": "success", "message": "Prescription saved successfully"}
