import logging
import json
from typing import Optional
from src.providers.base import LLMProvider
from src.schemas import ExecutionPlan, IntentClassification
from src.planner.intent_classifier import IntentClassifier

logger = logging.getLogger(__name__)

class DynamicPlanner:
    """
    The 'Brain' of the system.
    1. Classifies User Intent (via IntentClassifier).
    2. Generates an ExecutionPlan (JSON) if needed.
    """
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.classifier = IntentClassifier(llm_provider)

    async def plan(self, user_input: str) -> ExecutionPlan:
        """
        Main entry point: Analyzes input and returns an executable plan.
        """
        # 1. Classify Intent
        classification = await self.classifier.classify(user_input)
        logger.info(f"Intent Classified: {classification.intent_type} (Score: {classification.confidence_score})")

        # 2. Generate Plan based on Intent
        plan = await self._generate_plan_for_intent(user_input, classification)
        return plan

    async def _generate_plan_for_intent(self, user_input: str, classification: IntentClassification) -> ExecutionPlan:
        """
        Asks the LLM to generate a structured step-by-step plan for the given intent.
        """
        prompt = f"""
        You are an Expert Planner. The user has a request with intent: '{classification.intent_type}'.
        Reasoning: {classification.reasoning}

        USER REQUEST: "{user_input}"

        Create a valid JSON ExecutionPlan to fulfill this request.
        The plan must result in a valid JSON object matching this schema:
        {{
            "intent": "{classification.intent_type}",
            "steps": [
                {{
                    "id": "step_1",
                    "description": "Description of step",
                    "tool_name": "optional_tool_name_or_null", 
                    "tool_args": ["arg1", "arg2"],
                    "dependencies": []
                }}
            ]
        }}
        
        Available Tools:
        - 'python_version': args=['--version']
        - 'ls': args=['directory'] (e.g. '.') - ONLY if absolutely needed.
        
        If the intent is 'chat' or 'debate', the plan might just have one step with no tool, just a description like "Reply to user".

        Respond ONLY with the valid JSON.
        """

        try:
            response_str = await self.llm_provider.generate_response(prompt)
            
            # Clean JSON
            clean_json = response_str.strip()
            if clean_json.startswith("```"):
                clean_json = clean_json.split("\n", 1)[1]
                clean_json = clean_json.rsplit("\n", 1)[0]
                clean_json = clean_json.replace("```", "")

            data = json.loads(clean_json)
            return ExecutionPlan(**data)

        except Exception as e:
            logger.error(f"Plan Generation Failed: {e}")
            raise ValueError(f"Could not generate plan: {e}")
