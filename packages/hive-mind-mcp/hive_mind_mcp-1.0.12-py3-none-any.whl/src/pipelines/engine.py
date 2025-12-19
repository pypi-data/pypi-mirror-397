import yaml
import logging
from typing import Dict, Any, List
from pathlib import Path
from src.schemas import WorkflowDefinition, WorkflowStep
from src.providers.tool_aware_provider import ToolAwareProvider

logger = logging.getLogger(__name__)

class PipelineEngine:
    """
    Engine for executing YAML-defined Workflows.
    """
    def __init__(self, tool_provider: ToolAwareProvider):
        self.tool_provider = tool_provider
        self.workflows: Dict[str, WorkflowDefinition] = {}

    def load_workflow(self, yaml_path: str) -> str:
        """
        Loads and validates a workflow from a YAML file.
        Returns the workflow name.
        """
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            
            workflow = WorkflowDefinition(**data)
            self.workflows[workflow.name] = workflow
            logger.info(f"Loaded workflow: {workflow.name} (v{workflow.version})")
            return workflow.name
        except Exception as e:
            logger.error(f"Failed to load workflow {yaml_path}: {e}")
            raise ValueError(f"Invalid workflow file: {e}")

    async def run_workflow(self, workflow_name: str, initial_context: Dict[str, Any] = None):
        """
        Executes a loaded workflow.
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found.")
        
        workflow = self.workflows[workflow_name]
        logger.info(f"Starting workflow: {workflow.name}")
        
        context = initial_context or {}
        
        # Simple linear execution for Phase 3 MVP (ignoring dependencies for now)
        # TODO: Implement full dependency graph resolution
        for step in workflow.steps:
            await self._execute_step(step, context)
            
        logger.info(f"Workflow {workflow.name} completed.")
        return context

    async def _execute_step(self, step: WorkflowStep, context: Dict[str, Any]):
        """
        Executes a single step.
        """
        logger.info(f"Executing step: {step.name} (Action: {step.action})")
        
        retries = 0
        while True:
            try:
                if step.action == "run_tool":
                    tool_name = step.args.get("tool_name")
                    tool_args = step.args.get("tool_args", [])
                    
                    # Resolve args
                    resolved_args = []
                    for arg in tool_args:
                        if isinstance(arg, str) and arg.startswith("$") and arg[1:] in context:
                            resolved_args.append(context[arg[1:]])
                        else:
                            resolved_args.append(arg)

                    output = self.tool_provider.execute_tool(tool_name, resolved_args)
                    context[f"{step.name}.output"] = output.strip()
                    logger.info(f"Step {step.name} output: {output.strip()}")

                elif step.action == "log":
                    message = step.args.get("message", "")
                    print(f"[Workflow Log] {message}")
                
                else:
                    logger.warning(f"Unknown action: {step.action}")
                
                # Success - break loop
                break

            except Exception as e:
                retries += 1
                logger.error(f"Step {step.name} failed (Attempt {retries}/{step.max_retries + 1}): {e}")
                
                if not step.retry_on_failure or retries > step.max_retries:
                    raise RuntimeError(f"Workflow failed at step {step.name} after {retries} retries: {e}")
                
                # Optional: Add sleep here if needed
                import asyncio
                await asyncio.sleep(0.1) # Brief pause before retry
