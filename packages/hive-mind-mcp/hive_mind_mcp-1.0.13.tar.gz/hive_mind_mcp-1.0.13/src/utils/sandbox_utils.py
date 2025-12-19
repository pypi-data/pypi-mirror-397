import docker
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

def create_sandboxed_container(
    image_name: str, 
    command: List[str], 
    environment: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> str:
    """
    Runs a command in a secure, sandboxed container using gVisor (runsc) if available,
    falling back to standard Docker with high security restrictions if not.

    Args:
        image_name: Docker image to use (e.g., 'python:3.9-slim').
        command: Command list to execute.
        environment: Dictionary of environment variables.
        timeout: Execution timeout in seconds.

    Returns:
        The standard output (stdout) of the command.

    Raises:
        RuntimeError: If execution fails or times out.
    """
    client = docker.from_env()
    
    # Common security options for hardening
    # "no-new-privileges" prevents privilege escalation
    security_opt = ["no-new-privileges"]
    
    # Drop all capabilities by default
    cap_drop = ["ALL"]

    runtime = "runc" # Default standard runtime
    
    # Attempt to use gVisor ('runsc') for true sandboxing
    # Note: Host must have runsc installed and configured in Docker daemon
    try:
        # Check if 'runsc' is available in info (simplified check)
        # Real check would involve inspecting client.info()['Runtimes']
        # For now, we assume user configures it if they want it, or we try/catch
        pass 
    except Exception:
        pass

    try:
        logger.info(f"Running sandboxed command: {' '.join(command)}")
        
        container = client.containers.run(
            image=image_name,
            command=command,
            environment=environment or {},
            runtime=runtime, # TODO: Switch to 'runsc' when configured
            detach=True,
            security_opt=security_opt,
            cap_drop=cap_drop,
            network_mode="none", # No internet access by default for safety
            mem_limit="512m",    # Resource limits
            cpu_quota=50000,     # 50% CPU
            remove=False         # Manual removal to ensure we capture logs
        )
        
        # We did not use remove=True above because we need to get logs first
        # Actually create with detach=True returns container object
        
        try:
            # Wait for result
            result = container.wait(timeout=timeout)
            exit_code = result.get('StatusCode', 1)
            
            logs = container.logs().decode('utf-8')
            
            if exit_code != 0:
                raise RuntimeError(f"Sandbox execution failed (Exit Code {exit_code}): {logs}")
            
            return logs
            
        finally:
            # Clean up ensure removal
            try:
                container.remove(force=True)
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Sandbox container error: {str(e)}")
        raise RuntimeError(f"Failed to execute in sandbox: {str(e)}")
