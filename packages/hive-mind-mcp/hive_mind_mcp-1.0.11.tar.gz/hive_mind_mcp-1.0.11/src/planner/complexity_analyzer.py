import logging
from typing import Dict, Any, Optional
from src.schemas import IntelligenceTier

logger = logging.getLogger(__name__)

class ComplexityAnalyzer:
    """
    Analyzes user prompts to determine the appropriate Intelligence Tier.
    Uses a hybrid approach: Heuristics -> (Future) Router LLM.
    """
    
    # Heuristic Keywords
    HIGH_COMPLEXITY_KEYWORDS = {
        "architect", "design", "refactor", "strategy", "roadmap", "analyze", 
        "debate", "critique", "plan", "complex", "security", "vulnerability"
    }
    
    MEDIUM_COMPLEXITY_KEYWORDS = {
        "example", "explain", "generate", "write", "create", "list", "how to"
    }

    def analyze(self, prompt: str) -> IntelligenceTier:
        """
        Analyzes the prompt and returns the suggested Intelligence Tier.
        """
        prompt_lower = prompt.lower()
        word_count = len(prompt.split())
        
        # 1. Length Heuristic
        # Very long prompts usually imply context-heavy tasks -> SOTA
        if word_count > 500:
            logger.info(f"Complexity Analysis: HIGH (Length: {word_count} words)")
            return IntelligenceTier.SOTA
            
        # 2. Keyword Heuristic
        if any(kw in prompt_lower for kw in self.HIGH_COMPLEXITY_KEYWORDS):
            logger.info("Complexity Analysis: HIGH (Keywords detected)")
            return IntelligenceTier.SOTA
            
        if any(kw in prompt_lower for kw in self.MEDIUM_COMPLEXITY_KEYWORDS):
            logger.info("Complexity Analysis: ADVANCED (Keywords detected)")
            return IntelligenceTier.ADVANCED
            
        # 3. Default (Basic)
        # Short, simple queries -> Basic
        logger.info("Complexity Analysis: BASIC (Default)")
        return IntelligenceTier.BASIC
