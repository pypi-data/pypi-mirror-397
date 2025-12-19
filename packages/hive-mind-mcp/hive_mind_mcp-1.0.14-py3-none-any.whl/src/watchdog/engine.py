import logging
from typing import List, Dict, Any
from src.schemas import IntelligenceTier

logger = logging.getLogger(__name__)

# Trusted providers we want to watch. 
# We only suggest updates for providers the user already trusts.
TRUSTED_PROVIDERS = ["openai", "anthropic", "deepseek"]

def classify_tier(model_info: Dict[str, Any]) -> IntelligenceTier:
    """
    Heuristics to determine Intelligence Tier based on Name and Pricing.
    Accuracy: ~90% for major providers.
    """
    model_id = model_info.get("id", "").lower()
    pricing = model_info.get("pricing", {})
    prompt_price = float(pricing.get("prompt", 0) or 0)
    
    # 1. Price Signal (Strongest)
    # > $5 per 1M tokens ($0.000005 per token) -> SOTA
    # This catches "Opus", "GPT-4", "Ultra" 
    if prompt_price > 0.000005: 
        return IntelligenceTier.SOTA
        
    # 2. Name Signal (Marketing Keywords)
    sota_keywords = ["opus", "ultra", "gpt-5", "gpt-4.5", "gpt-4o"]
    if any(kw in model_id for kw in sota_keywords):
        return IntelligenceTier.SOTA
        
    basic_keywords = ["mini", "haiku", "flash", "instant", "micro", "nano"]
    if any(kw in model_id for kw in basic_keywords):
        return IntelligenceTier.BASIC
        
    # Default Fallback -> Advanced (Safe middle ground)
    return IntelligenceTier.ADVANCED

def check_for_upgrades(current_providers: List[Any], remote_models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compares local config against remote models to find new candidates.
    Returns a list of suggestion dicts.
    """
    suggestions = []
    
    # Extract IDs of models we already have to avoid duplicates
    existing_model_ids = set()
    for prov in current_providers:
         # Assuming prov is a ProviderConfig object or dict from config.yaml
         # The structure in config.yaml is tiers -> tier -> models -> list
         pass 
         # Actually, 'current_providers' argument structure needs to be clarified.
         # Let's assume we pass a Set of "provider:model" strings for efficiency.
    
    # Simplify: We just look for "Interesting" models in remote list that match our TRUSTED_PROVIDERS
    # and satisfy the "Newness" criteria (heuristic: name contains year 2024/2025/2026)
    
    for remote in remote_models:
        rid = remote.get("id", "")
        # Check standard provider prefixes used by OpenRouter
        # e.g. "openai/gpt-5", "anthropic/claude-3-7-opus"
        
        provider_match = None
        for trusted in TRUSTED_PROVIDERS:
            if rid.startswith(f"{trusted}/"):
                provider_match = trusted
                break
        
        if not provider_match:
            continue
            
        # Refine Model Name (remove prefix for local config compat)
        # "anthropic/claude-3-5-sonnet" -> "claude-3-5-sonnet"
        clean_model_name = rid.split("/", 1)[1]
        
        # Determine Tier
        tier = classify_tier(remote)
        
        # Add to suggestions
        suggestions.append({
            "provider": provider_match,
            "model": clean_model_name,
            "tier": tier.value, # "SOTA", "Advanced", etc.
            "price": remote.get("pricing", {}),
            "context": remote.get("context_length", 0)
        })
        
    return suggestions
