import os
import google.generativeai as genai
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import LLMProvider
from ..config import settings

class GeminiProvider(LLMProvider):
    PROVIDER_NAME = "gemini"
    
    def __init__(self, timeout: Optional[float] = None):
        self.api_key = os.getenv("GEMINI_API_KEY") # Or GOOGLE_API_KEY
        if not self.api_key:
            # Fallback
            self.api_key = os.getenv("GOOGLE_API_KEY")
            
        if not self.api_key:
             # Just warn, don't crash yet
             from src.logger import get_logger
             get_logger("gemini_provider").warning("gemini_key_missing")
        else:
            genai.configure(api_key=self.api_key)
            
        self.timeout = timeout or settings.default_timeout

    def _convert_messages(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None):
        """
        Convert standard messages to Gemini history.
        Gemini uses 'user'/'model' roles. 'system' is separate or handled via config.
        """
        gemini_history = []
        
        # If system prompt is present, Gemini 1.5 allows it in generation_config or as first part.
        # But simpler SDK usage often puts system prompt in Model construction.
        # Here we only instantiate model per request, so we can pass system_instruction there.
        
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [m["content"]]})
            
        return gemini_history

    @retry(
        stop=stop_after_attempt(3), # Less aggressive retry for non-standard providers initially
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_response(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set")

        # Helper validation: Gemini requires 'models/' or 'tunedModels/' usually, or just the name. 
        # But if we force override here, we break 'models/...' inputs.
        # Only override if completely empty or invalid looking?
        # Actually, let's trust the user input, or just ensure default if None.
        if not model:
            model = "models/gemini-1.5-flash" 
            
        # If user passed 'gemini-1.5-flash' (without prefix), the SDK might want 'models/' prefix?
        # The genai library is inconsistent. Let's try to be smart.
        if not model.startswith("models/") and not model.startswith("gemini"):
             # If it looks like a simple ID e.g. "gemini-pro"
             pass

        # Instantiate model with system instruction
        gen_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt
        )
        
        gemini_messages = self._convert_messages(messages)
        
        # Gemini expects the chat to start. 
        # If we have a history, we use it.
        # However, generate_content is stateless if we pass contents list?
        # Note: genai.GenerativeModel.generate_content (async?)
        # The library supports async.
        
        # We need a proper async call.
        response = await gen_model.generate_content_async(
            contents=gemini_messages
        )
        
        return response.text

    def list_models(self) -> List[str]:
        if not self.api_key:
            return []
        
        try:
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Strip 'models/' prefix for cleaner UI, or keep it depending on what generate_content expects
                    # The generate_content method usually handles 'models/' prefix gracefully, or even requires it.
                    # Let's return the name as is, usually 'models/gemini-pro'
                    models.append(m.name)
            return models
        except Exception as e:
            from src.logger import get_logger
            get_logger("gemini_provider").error("list_models_failed", error=str(e))
            return ["gemini-1.5-flash", "gemini-1.5-pro"] # Fallback
