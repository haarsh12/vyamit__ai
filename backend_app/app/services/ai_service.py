"""
Vyamit AI Service - Hybrid Implementation
Uses Hugging Face + Gemini fallback + Rule-based fallback for maximum reliability
"""

from .ai_service_hybrid import HybridAIService

# Create a singleton instance
_ai_service_instance = None

def get_ai_service():
    """Get or create AI service instance"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = HybridAIService()
    return _ai_service_instance

# For backward compatibility, create AIService class that wraps HybridAIService
class AIService:
    def __init__(self):
        self._service = get_ai_service()
    
    def process_voice_command(self, user_text: str, inventory, user_id: str = "default"):
        """Process voice command - compatible with existing API"""
        return self._service.process_voice_command(user_text, inventory, user_id)
    
    def get_chat_history(self):
        """Get chat history"""
        return self._service.get_chat_history()
    
    def clear_chat_history(self):
        """Clear chat history"""
        return self._service.clear_chat_history()
    
    def get_service_info(self):
        """Get service information"""
        return self._service.get_service_info()

# Export for direct usage
__all__ = ['AIService', 'HybridAIService', 'get_ai_service']