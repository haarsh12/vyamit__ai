"""
Simplified Vyamit AI Voice Service (hackathon).
Removed all LangChain and HuggingFace dependencies to fix environment conflicts.
Now it delegates entirely to Gemini via AIService.
"""

from typing import Any, Dict, List
from app.db.models import Item
from app.services.ai_service import AIService

class HybridVyamitVoiceService:
    """
    Simplified service that drops the multi-model pipeline.
    Maintains class name and interface for compatibility.
    Builds the prompt and directly returns the Gemini JSON.
    """

    def __init__(self) -> None:
        self._ai = AIService()

    def process_voice_command(
        self,
        user_text: str,
        inventory: List[Item],
        user_id: int,
        shop_category: str = "General",
    ) -> Dict[str, Any]:
        """
        Builds the prompt using AIService and runs Google Gemini.
        """
        print(f"\n🎙️ [Simplified Voice Service] Processing input for user_id: {user_id}")
        
        # 1) Build prompt using existing logic
        prompt = self._ai._build_vyamit_prompt(
            user_text, inventory, shop_category=shop_category
        )
        
        # 2) Run Gemini
        print("▶ Routing to Gemini (AIService)")
        result = self._ai.run_gemini_only(prompt)
        
        # 3) Return output directly
        if not result or not isinstance(result, dict) or "type" not in result:
            print("⚠️ Failed to parse valid JSON from Gemini output.")
            return {
                "type": "ERROR",
                "items": [],
                "msg": "सिस्टम त्रुटि: कृपया बाद में पुनः प्रयास करें।",
                "should_stop": False,
            }
            
        print("✅ Successfully processed voice command via Gemini.")
        return result
