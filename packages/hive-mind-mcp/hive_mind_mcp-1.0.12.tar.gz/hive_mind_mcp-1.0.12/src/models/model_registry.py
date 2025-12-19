import yaml
import logging
import json
import os
from typing import Dict, List, Optional
from pydantic import BaseModel
from src.schemas import IntelligenceTier

logger = logging.getLogger(__name__)

class ModelConfig(BaseModel):
    provider: str
    model: str
    priority: int = 1

class TierConfig(BaseModel):
    models: List[ModelConfig]
    fallback_strategy: str = "next_priority"

class ResolverConfig(BaseModel):
    tiers: Dict[str, TierConfig]
    default_tier: str = "Advanced"

class ModelRegistry:
    """
    Manages model configuration and resolves Intelligence Tiers to specific models.
    """
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config: Optional[ResolverConfig] = None
        self._load_config()

    def _load_config(self):
        """Loads config from yaml or cached intelligence."""
        import os
        import json
        
        # 1. Try Loading Cached Intelligence (Highest Priority for Dynamic Models)
        cache_path = os.path.expanduser("~/.hive_mind/intelligence_cache.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    cached_data = json.load(f)
                    if "models" in cached_data:
                        logger.info("🧠 Loaded Dynamic Intelligence Cache.")
                        self._build_config_from_cache(cached_data["models"])
                        return
            except Exception as e:
                logger.warning(f"Failed to load intelligence cache: {e}")

        # 2. Try Config File (User Override)
        try:
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f)
                if data and "model_resolver" in data:
                    self.config = ResolverConfig(**data["model_resolver"])
                    logger.info("ModelRegistry loaded from config.yaml.")
                else:
                    logger.warning("Invalid config structure. Utilizing defaults.")
                    self._use_defaults()
        except FileNotFoundError:
            # Only warn if cache also failed
            logger.info(f"Config file {self.config_path} not found. Using defaults.")
            self._use_defaults()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._use_defaults()

    def _build_config_from_cache(self, models_list: List[Dict]):
        """Converts Scientist Ranking into ResolverConfig."""
        # Map known tags to Tiers
        sota_models = []
        advanced_models = []
        basic_models = []
        
        for m in models_list:
            if "/" not in m["id"]: continue
            provider, model_name = m["id"].split("/", 1)
            mc = ModelConfig(provider=provider, model=model_name, priority=1) # Score logic could go here
            
            tags = [t.lower() for t in m.get("tags", [])]
            if "sota" in tags or m.get("score", 0) > 95:
                sota_models.append(mc)
            elif "fast" in tags or m.get("score", 0) < 90:
                basic_models.append(mc)
            else:
                advanced_models.append(mc)
                
        self.config = ResolverConfig(
            tiers={
                "SOTA": TierConfig(models=sota_models or [ModelConfig(provider="openai", model="gpt-4o")]),
                "Advanced": TierConfig(models=advanced_models or [ModelConfig(provider="openai", model="gpt-4o")]),
                "Basic": TierConfig(models=basic_models or [ModelConfig(provider="groq", model="llama-3.1-8b-instant")])
            },
            default_tier="SOTA" # Promote intelligence
        )

    def _use_defaults(self):
        # Fallback defaults if config is missing
        logger.info("Initializing ModelRegistry with default hardcoded tiers.")
        self.config = ResolverConfig(
            tiers={
                "SOTA": TierConfig(models=[ModelConfig(provider="openai", model="gpt-4o")]),
                "Advanced": TierConfig(models=[ModelConfig(provider="openai", model="gpt-4o-mini")]),
                "Basic": TierConfig(models=[ModelConfig(provider="groq", model="llama-3.1-8b-instant")])
            },
            default_tier="Advanced"
        )

    def resolve_tier(self, tier: Optional[IntelligenceTier] = None) -> ModelConfig:
        """
        Resolves a Tier to the best available ModelConfig.
        """
        if not self.config:
            self._use_defaults()

        # Handle None -> Default
        target_tier_name = tier.value if tier else self.config.default_tier
        
        # Case insensitive lookup
        tier_config = None
        for key, conf in self.config.tiers.items():
            if key.lower() == target_tier_name.lower():
                tier_config = conf
                break
        
        if not tier_config:
            logger.warning(f"Tier '{target_tier_name}' not found. Falling back to default '{self.config.default_tier}'.")
            # Try default again
            target_tier_name = self.config.default_tier
            for key, conf in self.config.tiers.items():
                if key.lower() == target_tier_name.lower():
                    tier_config = conf
                    break
        
        if not tier_config or not tier_config.models:
            raise ValueError(f"Could not resolve tier '{target_tier_name}' to any model.")

        # Sort by priority (lower is better, assuming conventional 1=Highest)
        # But implementation plan implicitly suggested list order. 
        # Let's sort just in case priority is used widely.
        sorted_models = sorted(tier_config.models, key=lambda m: m.priority)
        
        # Return the first one (Health checks would filter this list in future)
        return sorted_models[0]

    def resolve_tier_models(self, tier: Optional[IntelligenceTier] = None) -> List[Dict[str, str]]:
        """
        Resolves a Tier to ALL available models in that tier.
        Returns a list of dicts: [{'provider': 'p', 'model': 'm'}, ...]
        """
        if not self.config:
            self._use_defaults()

        target_tier_name = tier.value if tier else self.config.default_tier
        
        tier_config = None
        for key, conf in self.config.tiers.items():
            if key.lower() == target_tier_name.lower():
                tier_config = conf
                break
        
        if not tier_config:
            # Fallback to default tier
            logger.warning(f"Tier '{target_tier_name}' not found. Falling back to default '{self.config.default_tier}'.")
            target_tier_name = self.config.default_tier
            for key, conf in self.config.tiers.items():
               if key.lower() == target_tier_name.lower():
                   tier_config = conf
                   break

        if not tier_config or not tier_config.models:
             # Critical fallback to avoid empty list
             logger.error(f"Could not resolve ANY models for tier '{target_tier_name}'. Returning hardcoded fallback.")
             return [{"provider": "openai", "model": "gpt-4o"}]

        # Sort by priority
        sorted_models = sorted(tier_config.models, key=lambda m: m.priority)
        
        # Convert to simple dict format expected by tools
        return [{"provider": m.provider, "model": m.model} for m in sorted_models]
