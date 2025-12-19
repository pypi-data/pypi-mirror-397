import httpx
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/models"

async def fetch_openrouter_models() -> List[Dict[str, Any]]:
    """
    Fetches the list of available models from OpenRouter.
    Returns a list of model objects (dict).
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OPENROUTER_URL, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # OpenRouter returns {"data": [...]}
            models = data.get("data", [])
            logger.info(f"Watchdog: Fetched {len(models)} models from OpenRouter.")
            return models
            
    except httpx.HTTPError as e:
        logger.error(f"Watchdog Ingest Error: Failed to fetch models from {OPENROUTER_URL}. Error: {e}")
        return []
    except Exception as e:
        logger.exception(f"Watchdog Ingest Unexpected Error: {e}")
        return []
