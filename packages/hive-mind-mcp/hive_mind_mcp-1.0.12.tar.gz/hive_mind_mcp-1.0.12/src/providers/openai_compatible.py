import os
import logging
from typing import Optional
from .base import LLMProvider
from .openai import OpenAIProvider

class OpenAICompatibleProvider(OpenAIProvider):
    """
    Generic provider for any OpenAI-compatible API (Ollama, Groq, Azure, vLLM, DeepInfra).
    Reuses the OpenAIProvider logic but overrides the client initialization.
    """
    PROVIDER_NAME = "generic"

    def __init__(self,
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 timeout: Optional[float] = None):
        # We don't call super().__init__ directly because it might force standard OPENAI_ API keys.
        # Instead, we set up what we need manually or call it carefully.
        # Looking at openai.py, __init__ sets self.client using env vars.
        
        # We will override the client creation logic.
        from openai import AsyncOpenAI
        
        # 1. Determine Config
        # Priority: Constructor Args -> Env Vars specific to Generic -> Fallback
        self.base_url = base_url or os.getenv("GENERIC_BASE_URL")
        self.api_key = api_key or os.getenv("GENERIC_API_KEY", "dummy-key-for-local")
        
        if not self.base_url:
            # Maybe the user didn't config, but we can't crash blindly.
            # But for a proactive provider, we should warn.
            logging.getLogger("llm_manager").warning(
                "generic_provider_config_missing: GENERIC_BASE_URL not set. Defaulting to localhost:11434/v1 (Ollama)."
            )
            self.base_url = "http://localhost:11434/v1"

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout,
            max_retries=2
        )

    def list_models(self):
        # Allow dynamic discovery if the endpoint supports it (like Ollama /v1/models)
        # We need to run the async client call in a sync wrapper or return a static list if failing.
        # But this method is likely called synchronously by the manager?
        # The manager calls `provider.list_models()`. If we need async, we might be blocked.
        # However, checking openai.py, list_models is synchronous? 
        # Wait, openai.py uses `client = AsyncOpenAI`. 
        # If we need to list models synchronously, we might need a separate Sync client or raw request.
        
        # Let's try to use requests for simplicity in this discovery phase, or rely on a hardcoded list if complex.
        # Better: use httpx since we have it.
        import httpx
        try:
            # Assuming standard OpenAI format /v1/models
            url = f"{self.base_url.rstrip('/')}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            # fast timeout
            resp = httpx.get(url, headers=headers, timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                # OpenAI format: {'data': [{'id': 'foo', ...}]}
                if 'data' in data:
                    return [m['id'] for m in data['data']]
            return ["generic-model (configured in env)"]
        except Exception:
             return ["generic-model (configured in env)"]
