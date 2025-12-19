import logging
import json
from typing import Dict, Any, Optional
from src.providers.base import LLMProvider
from src.schemas import IntentClassification
from src.planner.complexity_analyzer import ComplexityAnalyzer

logger = logging.getLogger(__name__)

class IntentClassifier:
    """
    Classifies user intent using an LLM and analyzes complexity for tier/model selection.
    """
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.complexity_analyzer = ComplexityAnalyzer()

    async def classify(self, user_input: str) -> IntentClassification:
        """
        Determines the intent of the user input.
        """
        prompt = f"""
        You are the 'Brain' of an advanced AI Agent System.
        Your job is to CLASSIFY the user's request into one of the following categories:
        
        1. 'tool_use': The user wants to perform a specific action, run a command, specific file manipulation, or look up information. 
           (Examples: "List files in src", "Run the tests", "Check python version", "Read file X")
        
        2. 'debate': The user wants to discuss a complex topic, get a second opinion, or refine an idea through multiple perspectives. 
           (Examples: "Debate the pros/cons of Rust vs Go", "Critique this design", "Brainstorm features")
        
        3. 'review': The user wants a peer review of a specific artifact or code.
           (Examples: "Review this PR", "Check this code for bugs", "Evaluate this plan")
        
        4. 'chat': General conversation, greeting, or simple questions that don't fit above.
           (Examples: "Hi", "Who are you?", "Tell me a joke")

        USER REQUEST: "{user_input}"

        Respond ONLY with a valid JSON object matching this schema:
        {{
            "intent_type": "tool_use" | "debate" | "review" | "chat",
            "confidence_score": float (0.0 to 1.0),
            "reasoning": "string explanation"
        }}
        """
        
        try:
            response_str = await self.llm_provider.generate_response(prompt)
            clean_json = self._clean_json(response_str)
            logger.info(f"LLM Response: {clean_json}")
            
            data = json.loads(clean_json)
            
            # Run Complexity Analysis
            suggested_tier = self.complexity_analyzer.analyze(user_input)
            data["suggested_tier"] = suggested_tier
            
            return IntentClassification(**data)
            
        except Exception as e:
            logger.error(f"Intent Classification Failed: {e}")
            # Fallback
            return IntentClassification(
                intent_type="chat", 
                confidence_score=0.0, 
                reasoning="Fallback due to error",
                suggested_tier=None
            )

    def _clean_json(self, raw_text: str) -> str:
        text = raw_text.strip()
        if text.startswith("```"):
            # Remove first line (```json) using split
            text = text.split("\n", 1)[1]
            # Remove last line (```)
            text = text.rsplit("\n", 1)[0]
            text = text.replace("```", "")
        return text
