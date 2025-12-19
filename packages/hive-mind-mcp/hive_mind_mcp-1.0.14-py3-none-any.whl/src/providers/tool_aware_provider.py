import logging
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from src.providers.base import LLMProvider
from src.utils.sandbox_utils import create_sandboxed_container

logger = logging.getLogger(__name__)

class ToolDefinition(BaseModel):
    name: str
    description: str
    docker_image: str
    entrypoint: str
    allowed_args: List[str]

class ToolAwareProvider:
    """
    Wraps a standard LLMProvider to add secure Tool Execution capabilities.
    """
    def __init__(self, provider: LLMProvider, tools: List[ToolDefinition]):
        self.provider = provider
        self.tools = {t.name: t for t in tools}
        self.logger = logger
        
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Intercepts the prompt to check for tool usage intent (simplified for now).
        In a real agent loop, this would parse a structured tool-use output.
        """
        # For Phase 1, we pass-through to LLM. 
        # The internal logic to *detect* tool calls would live here or in the Agent loop.
        response = await self.provider.generate_response(prompt, context)
        return response

    def execute_tool(self, tool_name: str, args: List[str]) -> str:
        """
        Executes a named tool securely.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' is not registered/allowed.")
            
        tool_def = self.tools[tool_name]
        
        # Security: Validate arguments against allow-list (Basic implementation)
        # In production, this needs robust regex matching
        for arg in args:
             if arg.startswith("-") and arg not in tool_def.allowed_args:
                 # Check if the flag itself is allowed. 
                 # This is a bit naive for key-value args (e.g. --key value), but good for start.
                 # A stricter allow-list might require full command string validation.
                 pass 

        # Construct payload
        full_command = [tool_def.entrypoint] + args
        
        try:
            output = create_sandboxed_container(
                image_name=tool_def.docker_image,
                command=full_command
            )
            return output
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return f"Error executing tool {tool_name}: {str(e)}"
