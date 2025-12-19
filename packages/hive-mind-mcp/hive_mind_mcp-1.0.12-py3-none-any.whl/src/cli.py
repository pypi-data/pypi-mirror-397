import argparse
import asyncio
import os
import sys
import fnmatch
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Ensure src can be imported if running from root
sys.path.append(os.getcwd())

from src.tools import LLMManager
from src.logger import configure_logger, get_logger
from src.ui.presentation import ArtifactPresenter
from src.watchdog.ingest import fetch_openrouter_models
from src.watchdog.ingest import fetch_openrouter_models
from src.watchdog.engine import check_for_upgrades
import shutil
import json


# Initialize logger
configure_logger()
logger = get_logger("cli")

def parse_kv(items: Optional[List[str]]) -> Optional[List[Dict[str, str]]]:
    """Parse list of 'provider:model' strings into dicts."""
    if not items:
        return None
    result = []
    for item in items:
        try:
            provider, model = item.split(":", 1)
            result.append({"provider": provider, "model": model})
        except ValueError:
            logger.warning("invalid_reviewer_format", item=item, expected="provider:model")
    return result

def resolve_paths(paths: List[str]) -> List[str]:
    """Resolve directories to a list of file paths."""
    resolved = []
    for path in paths:
        if os.path.isfile(path):
            resolved.append(path)
        elif os.path.isdir(path):
             for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(('.py', '.md', '.txt', '.json', '.yaml', '.yml', '.js', '.ts', '.html', '.css', '.env', '.sh', '.sql')):
                         resolved.append(os.path.join(root, file))
    return resolved

def collect_context_content(paths: List[str]) -> str:
    """Read files or directories (recursively) and return collected context."""
    context_content = ""
    # Use the shared resolver
    files_to_read = resolve_paths(paths)
    logger.info("loading_context", count=len(files_to_read))

    for file_path in files_to_read:
        try:
            with open(file_path, 'r', errors='ignore') as f:
                 context_content += f"\n--- Context from {file_path} ---\n{f.read()}\n"
        except Exception as e:
             logger.warning("context_read_error", file=file_path, error=str(e))
             
    return context_content

async def run_debate(args):
    manager = LLMManager()
    reviewers = parse_kv(args.reviewers)
    
    logger.info("starting_debate", topic=args.prompt)
    
    
    context_content = ""
    if args.context:
         if args.map_reduce:
             # Use the new Universal Map-Reduce
             files = resolve_paths(args.context)
             context_content = await manager.map_reduce_context(files)
         else:
             context_content = collect_context_content(args.context)


    result = await manager.collaborative_refine(
        prompt=args.prompt,
        drafter_model=args.drafter_model,
        drafter_provider=args.drafter_provider,
        reviewers=reviewers,
        max_turns=args.max_turns,
        context=context_content if context_content else None
    )
    
    if isinstance(result, dict) and "content" in result:
        print(result["content"])
        if result.get("session_dir"):
            ArtifactPresenter.present_artifact(result["session_dir"], "Debate Session Artifacts")
    else:
        print(result)

async def run_review(args):
    manager = LLMManager()
    reviewers = parse_kv(args.reviewers)
    
    # If content is a file path, read it
    
    # If content is a file path or directory, read it using our context collector
    content = args.content
    if os.path.exists(content):
        if args.map_reduce:
             files = resolve_paths([content])
             content = await manager.map_reduce_context(files)
        else:
             content = collect_context_content([content])
            
    logger.info("starting_peer_review")
    result = await manager.evaluate_content(
        content=content,
        reviewers=reviewers
    )
    
    if isinstance(result, dict) and "content" in result:
        print(result["content"])
        if result.get("session_dir"):
             ArtifactPresenter.present_artifact(result["session_dir"], "Review Session Artifacts")
    else:
        print(result)

async def run_round_table(args):
    manager = LLMManager()
    panelists = parse_kv(args.panelists)
    
    # Default panel if none provided (logic usually in tool.py, but explicit here for CLI help)
    if not panelists:
        # We rely on tool.py defaults, or user passed flags
        pass 
        
    logger.info("starting_round_table", topic=args.prompt)
    
    
    context_content = ""
    if args.context:
        if args.map_reduce:
             files = resolve_paths(args.context)
             context_content = await manager.map_reduce_context(files)
        else:
             context_content = collect_context_content(args.context)


    result = await manager.round_table_debate(
        prompt=args.prompt,
        panelists=panelists,
        moderator_provider=args.moderator,
        context=context_content if context_content else None
    )
    
    if isinstance(result, dict) and "content" in result:
        print(result["content"])
        if result.get("session_dir"):
             ArtifactPresenter.present_artifact(result["session_dir"], "Round Table Artifacts")
    else:
        print(result)

async def run_analyze(args):
    manager = LLMManager()
    panelists = parse_kv(args.panelists)
    
    # Collect all file paths
    collected_files = []
    for p in args.paths:
        if os.path.isfile(p):
            collected_files.append(p)
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for file in files:
                    full_path = os.path.join(root, file)
                    # Check exclusions
                    if args.exclude:
                        should_exclude = False
                        for pattern in args.exclude:
                             if fnmatch.fnmatch(file, pattern) or fnmatch.fnmatch(full_path, pattern):
                                 should_exclude = True
                                 break
                        if should_exclude:
                            continue
                            
                    if file.endswith(('.py', '.md', '.txt')): # Basic filter
                         collected_files.append(full_path)
    
    logger.info("starting_analysis", file_count=len(collected_files), topic=args.prompt)
    run_result = await manager.analyze_project(
        file_paths=collected_files,
        prompt=args.prompt,
        panelists=panelists
    )
    
    if isinstance(run_result, dict) and "content" in run_result:
        print(run_result["content"])
        if run_result.get("session_dir"):
             ArtifactPresenter.present_artifact(run_result["session_dir"], "Map-Reduce Analysis Artifacts")
    else:
        print(run_result)

async def run_init(args):
    """Scaffold a new MCP Orchestrator project in the current directory."""
    print(f"🚀 Initializing MCP Orchestrator in {os.getcwd()}...")
    
    # 1. Artifact Visibility Preference
    print("📋 Configuration: Artifact Visibility")
    hide_artifacts = input("🙈 Should Hive Mind logs (.hive_mind/) be hidden from Git? (Recommended: Yes) [Y/n] ").lower() != 'n'
    
    gitignore_path = ".gitignore"
    base_ignore = "\n# Env\n.env\n"
    artifact_ignore = "\n# Orchestrator Artifacts\n.hive_mind/\noutputs/\n"
    
    final_ignore_content = base_ignore
    if hide_artifacts:
        final_ignore_content = artifact_ignore + base_ignore
        print("   -> Artifacts will be HIDDEN (.gitignore).")
    else:
        print("   -> Artifacts will be VISIBLE in project tree.")

    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write(final_ignore_content)
        print("✅ Created .gitignore")
    else:
        # Smart Update: Check if we need to append rules based on preference
        with open(gitignore_path, "r") as f:
            current_content = f.read()
            
        updates_made = False
        with open(gitignore_path, "a") as f:
            if hide_artifacts and ".hive_mind" not in current_content:
                f.write(artifact_ignore)
                print("   -> ➕ Appended .hive_mind to .gitignore")
                updates_made = True
            
            if ".env" not in current_content:
                 f.write(base_ignore)
                 print("   -> ➕ Appended .env to .gitignore")
                 updates_made = True
                 
        if updates_made:
            print("✅ Updated .gitignore")
        else:
            print("ℹ️  .gitignore already valid (skipped)")

    # 1.5 Global Configuration (Transparent Setup)
    home_dir = os.path.expanduser("~")
    global_config_dir = os.path.join(home_dir, ".hive_mind")
    global_env_path = os.path.join(global_config_dir, ".env")
    
    if not os.path.exists(global_env_path):
        print("\n🌍 Global Configuration (Shared across all projects)")
        setup_global = input("   Do you want to configure global API keys now? [y/N] ").lower() == 'y'
        
        if setup_global:
            if not os.path.exists(global_config_dir):
                os.makedirs(global_config_dir)
            
            with open(global_env_path, "w") as f:
                f.write(f"# Hive Mind Global Configuration\n# These keys will be used if not found in project .env\n\nOPENAI_API_KEY=\nANTHROPIC_API_KEY=\nDEEPSEEK_API_KEY=\nGROQ_API_KEY=\n")
            print(f"✅ Created global config at {global_env_path}")
            print(f"👉 Please edit this file to add your keys: 'nano {global_env_path}'")
            print("   (Skipping local .env creation since you chose global config)")
            return # Exit early if global setup is chosen to avoid confusion
            
    # 2. Create local .env scaffold (only if global wasn't just set up)
    env_path = ".env"
    if not os.path.exists(env_path):
        retention = input("🗑️  Enable automated cleanup of old sessions? (Default: 30 days) [Y/n] ")
        retention_days = "30"
        if retention.lower() == 'n':
            retention_days = "0"
            print("   -> Cleanup disabled.")
        else:
            print("   -> Retention set to 30 days.")

        with open(env_path, "w") as f:
            f.write(f"# API Keys\nOPENAI_API_KEY=\nANTHROPIC_API_KEY=\nDEEPSEEK_API_KEY=\n\n# Security\nDAILY_BUDGET_USD=2.00\n\n# Maintenance\nARTIFACT_RETENTION_DAYS={retention_days}\n")
        print("✅ Created .env (Please fill in your keys!)")
    else:
        print("ℹ️  .env already exists (skipped)")

    # 3. Create .mcp/ directory
    mcp_dir = ".mcp"
    project_name = os.path.basename(os.getcwd()) # Auto-detect project name
    
    if not os.path.exists(mcp_dir):
        os.makedirs(mcp_dir)
        with open(os.path.join(mcp_dir, "config.toml"), "w") as f:
            f.write(f"# Project Configuration\n[orchestrator]\nproject_name = '{project_name}'\n")
        print("✅ Created .mcp/config.toml")
    else:
        print("ℹ️  .mcp/ directory already exists (skipped)")

    # 4. Scaffold Agentic Workflows (Slash Commands support)
    workflows_dir = os.path.join(".agent", "workflows")
    if not os.path.exists(workflows_dir):
        os.makedirs(workflows_dir)
        
        # Define default workflows
        workflows = {
            "round_table.md": """---
description: Run a full Round Table debate (Independent Gen -> Cross Critique -> Synthesis).
---

# Chat Usage (/round_table)

**Syntax:**
`/round_table "<topic>" [--panelists ...]`

**Auto-Execution:**
// turbo
hive-mind round_table "$1" --context .
""",
            "debate.md": """---
description: Run an iterative collaborative debate loop.
---

# Chat Usage (/debate)

**Syntax:**
`/debate "<topic>" --max-turns 5`

**Auto-Execution:**
// turbo
hive-mind debate "$1"
""",
            "review.md": """---
description: Submit content for a Safety & Logic Check by the Council.
---

# Chat Usage (/review)

**Syntax:**
`/review "file/path"`

**Auto-Execution:**
// turbo
hive-mind review "$1"
"""
        }
        
        for name, content in workflows.items():
            path = os.path.join(workflows_dir, name)
            with open(path, "w") as f:
                f.write(content)
        print("✅ Created .agent/workflows/ (Slash Commands Enabled!)")
    else:
        print("ℹ️  .agent/workflows directory already exists (skipped)")
        
    print(f"\n🎉 Done! Hive Mind initialized for '{project_name}'.")
    print("👉 Try typing '/round_table' in your IDE chat!")

def find_free_port(start_port: int, max_retries: int = 10) -> int:
    """Find a free port starting from start_port."""
    import socket
    for port in range(start_port, start_port + max_retries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) != 0:
                return port
    raise RuntimeError(f"Could not find a free port between {start_port} and {start_port + max_retries}")

async def run_watchdog(args):
    """Execution for the Meta-Agent Watchdog: Syncs Intelligence Data from Scientist Service."""
    from src.config import settings
    import httpx
    import json
    
    print("🐕🤖 Watchdog: Syncing Dynamic Intelligence Data...")
    
    # 1. Connect to Scientist Service
    print(f"   -> Connecting to Scientist Service at {settings.scientist_api_url}...")
    
    intelligence_data = None
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.scientist_api_url}/v1/rankings")
            resp.raise_for_status()
            intelligence_data = resp.json()
            print("   -> ✅ Successfully connected to Scientist Service.")
    except Exception as e:
        print(f"   -> ⚠️  Could not reach Scientist Service ({str(e)})")
        print("   -> 🧪 Using Mock Intelligence (Simulation Mode) for demonstration.")
        
        # MOCK DATA (Simulates what the Scientist would return)
        intelligence_data = {
            "last_updated": "2025-12-17T12:00:00Z",
            "models": [
                {"id": "anthropic/claude-3-5-sonnet-20241022", "score": 98.5, "tags": ["coding", "sota"], "reason": "Best in BigCodeBench Hard"},
                {"id": "openai/gpt-4o", "score": 97.2, "tags": ["logic", "general"], "reason": "High reasoning capability"},
                {"id": "deepseek/deepseek-coder", "score": 92.0, "tags": ["coding", "fast"], "reason": "Best value for money"}
            ]
        }

    # 2. Save to Local Cache
    cache_dir = os.path.expanduser("~/.hive_mind")
    cache_path = os.path.join(cache_dir, "intelligence_cache.json")
    
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        
    with open(cache_path, "w") as f:
        json.dump(intelligence_data, f, indent=2)
        
    print(f"   -> 💾 Saved intelligence cache to {cache_path}")
    
    # 3. Report
    print("\n📊 Updated Model Rankings:")
    for model in intelligence_data["models"]:
        print(f"   🌟 [{model['score']}] {model['id']} ({', '.join(model['tags'])})")
        print(f"      Use Case: {model.get('reason', 'N/A')}")
        
    print("\n✅ Hive Mind is now synced with the Scientist.")

async def run_dashboard(args):
    """Launch the Streamlit dashboard."""
    import subprocess
    import sys
    
    # 1. Ensure artifacts dir exists
    if not os.path.exists(".hive_mind"):
        print("Warning: '.hive_mind' directory not found. Dashboard main be empty.")

    # 2. Path to dashboard script
    script_path = os.path.join(os.path.dirname(__file__), "dashboard.py")
    
    # 3. Launch Streamlit
    try:
        port = find_free_port(8503, max_retries=10)
        print(f"📊 Launching Dashboard on port {port}...")
        cmd = [sys.executable, "-m", "streamlit", "run", script_path, "--server.port", str(port)]
        
        # Run and wait
        process = subprocess.Popen(cmd)
        await asyncio.to_thread(process.wait)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
        process.terminate()

async def run_config(args):
    """Open the global configuration file in default editor."""
    import shutil
    
    config_dir = os.path.expanduser("~/.mcp_orchestrator")
    config_path = os.path.join(config_dir, ".env")
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"Created config directory: {config_dir}")
        
    if not os.path.exists(config_path):
        # Copy template if exists or create empty
        base_env = ".env.example"
        if os.path.exists(base_env):
            shutil.copy(base_env, config_path)
            print("Initialized config from .env.example")
        else:
            with open(config_path, "w") as f:
                f.write("# MCP Orchestrator Configuration\n")
            print("Created empty config file.")
    
    print(f"Opening config file: {config_path}")
    
    # Try opening in editor
    editor = os.getenv("EDITOR", "nano")
    if shutil.which("code"):
        editor = "code"
    elif shutil.which("vim"):
        editor = "vim"
        
    import subprocess
    subprocess.call([editor, config_path])

async def run_server(args):
    """Run the MCP server directly."""
    from src.server import mcp
    print("🚀 Starting Hive Mind MCP Server...", file=sys.stderr)
    # This runs the FastMCP server which blocks
    mcp.run()

async def run_install(args):
    """Auto-configure MCP clients."""
    print("\n🛠️  Hive Mind MCP Installer")
    print("===========================")
    
    # 1. Detect binary path
    binary_path = shutil.which("hive-mind")
    if not binary_path:
        binary_path = sys.executable
        # Attempt to reconstruct 'hive-mind' call if running from python
        if "python" in binary_path:
            # Fallback to module execution if binary not found
            pass 
            
    print(f"📍 Detected Installation: {binary_path}")
    
    print("\nSelect your client:")
    print("1. Google Antigravity (Help)")
    print("2. Claude Desktop")
    print("3. VS Code (MCP Servers extension)")
    print("4. Manual Configuration")
    
    choice = input("\n> ")
    
    if choice == "1":
        print("\n🔵 Google Antigravity")
        print("---------------------")
        print("Antigravity usually detects tools in the environment.")
        print("Verify your installation by running:")
        print(f"  {binary_path} --version")
        print("\nIf you need to register it manually in a workflow:")
        print("  command: hive-mind")
        print("  args: ['run']")
        
    elif choice == "2":
        config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
        if sys.platform != "darwin":
             # Win/Linux paths could be added here
             print("⚠️  Auto-config only supported on macOS for now.")
             return

        print(f"\n📂 Checking: {config_path}")
        
        current_config = {"mcpServers": {}}
        if os.path.exists(config_path):
             try:
                 with open(config_path, "r") as f:
                     current_config = json.load(f)
             except json.JSONDecodeError:
                 print("⚠️  Existing config is invalid JSON. Backing up...")
                 shutil.copy(config_path, config_path + ".bak")

        # Load Global Keys to inject if needed
        home_dir = os.path.expanduser("~")
        global_env_path = os.path.join(home_dir, ".hive_mind", ".env")
        env_vars = {}
        
        if os.path.exists(global_env_path):
            with open(global_env_path, "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        if v: env_vars[k] = v
        
        # Add Hive Mind
        current_config.setdefault("mcpServers", {})["hive-mind"] = {
            "command": binary_path,
            "args": ["run"],
            "env": env_vars
        }
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(current_config, f, indent=2)
            
        print("✅ Configured 'hive-mind' in Claude Desktop!")
        print("👉 Restart Claude Desktop to use it.")

    elif choice == "3":
        print("\n🆚 VS Code configuration")
        print("------------------------")
        print("Add this to your MCP Servers extension config:")
        
        config = {
            "mcpServers": {
                "hive-mind": {
                    "command": binary_path,
                    "args": ["run"],
                    "env": {"OPENAI_API_KEY": "..."}
                }
            }
        }
        print(json.dumps(config, indent=2))
        
    else:
        print("\n📝 Manual Configuration Details")
        print(f"Command: {binary_path}")
        print("Arguments: ['run']")


async def run_models(args):
    """List available models, optionally filtered by search term or provider."""
    manager = LLMManager()
    print("🔍 Discovering models... (this may take a moment)")
    
    # This triggers dynamic discovery
    models_data = manager.list_models()
    
    print(f"\n--- Available Models ---")
    total_matches = 0
    
    for provider, models in sorted(models_data.items()):
        # Filter by provider if specified
        if args.provider and args.provider.lower() != provider.lower():
            continue
            
        # Filter models by search term
        filtered_models = []
        for m in models:
            full_id = f"{provider}:{m}"
            if not args.search or (args.search.lower() in full_id.lower()):
                filtered_models.append(m)
        
        if filtered_models:
            print(f"\n📦 {provider.upper()} ({len(filtered_models)})")
            for m in filtered_models:
                print(f"  • {provider}:{m}")
            total_matches += len(filtered_models)
            
    if total_matches == 0:
        print("\n❌ No models found matching your criteria.")
    else:
        print(f"\nTotal: {total_matches} models found.")

def main():
    load_dotenv()
    
def get_version():
    try:
        from importlib.metadata import version
        return version("hive-mind-mcp")
    except ImportError:
        return "unknown"

def get_parser(parser_cls=argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = parser_cls(
        description="MCP LLM Orchestrator CLI"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {get_version()}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Config Command
    config_parser = subparsers.add_parser("config", help="Edit global configuration")
    config_parser.set_defaults(func=run_config)
    
    # Debate Command
    debate_parser = subparsers.add_parser("debate", help="Run a collaborative refinement debate")
    debate_parser.add_argument("prompt", help="The initial prompt or task")
    debate_parser.add_argument("--drafter-provider", default="openai", help="Provider for the drafter")
    debate_parser.add_argument("--drafter-model", default="gpt-4o", help="Model for the drafter")

    debate_parser.add_argument("--reviewers", nargs="+", help="List of reviewers in 'provider:model' format", default=[])
    debate_parser.add_argument("--max-turns", type=int, default=3, help="Maximum refinement loops")
    debate_parser.add_argument("--context", nargs="+", help="List of files to provide as context", default=[])
    debate_parser.add_argument("--map-reduce", action="store_true", help="Summarize context using Map-Reduce before debating")
    debate_parser.set_defaults(func=run_debate)
    
    # Review Command
    review_parser = subparsers.add_parser("review", help="Peer review existing content")
    review_parser.add_argument("content", help="Content string or path to file")
    review_parser.add_argument("--reviewers", nargs="+", help="List of reviewers in 'provider:model' format", default=[])
    review_parser.add_argument("--map-reduce", action="store_true", help="Summarize content using Map-Reduce before reviewing")
    review_parser.set_defaults(func=run_review)
    
    # Round Table Command
    rt_parser = subparsers.add_parser("round_table", help="Run a multi-model round table consensus")
    rt_parser.add_argument("prompt", help="The topic or question")
    rt_parser.add_argument("--panelists", nargs="+", help="Panelists in 'provider:model' format", default=[])
    rt_parser.add_argument("--moderator", default="openai", help="Moderator provider")
    rt_parser.add_argument("--context", nargs="+", help="List of files to provide as context", default=[])
    rt_parser.add_argument("--map-reduce", action="store_true", help="Summarize context using Map-Reduce before debating")
    rt_parser.set_defaults(func=run_round_table)

    # Analyze Command (Map-Reduce)
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a project or files using Map-Reduce")
    analyze_parser.add_argument("paths", nargs="+", help="Files or directories to analyze")
    analyze_parser.add_argument("prompt", help="The question or task")
    analyze_parser.add_argument("--panelists", nargs="+", help="Panelists for Reduce phase", default=[])
    analyze_parser.add_argument("--exclude", nargs="+", help="Glob patterns to exclude from analysis", default=[])
    analyze_parser.set_defaults(func=run_analyze)

    # Init Command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.set_defaults(func=run_init)

    # Dashboard Command
    dash_parser = subparsers.add_parser("dashboard", help="Launch the Observability Dashboard")
    dash_parser.set_defaults(func=run_dashboard)

    # Watchdog Command
    watchdog_parser = subparsers.add_parser("watchdog", help="Run the Meta-Agent Watchdog to check for model updates")
    watchdog_parser.set_defaults(func=run_watchdog)
    
    # Models Command
    models_parser = subparsers.add_parser("models", help="List and search available models")
    models_parser.add_argument("--search", help="Filter by name (e.g. 'claude')")
    models_parser.add_argument("--provider", help="Filter by provider (e.g. 'openai')")
    models_parser.set_defaults(func=run_models)
    
    # Server Command
    server_parser = subparsers.add_parser("run", help="Run the MCP Server")
    server_parser.set_defaults(func=run_server)

    # Install Command
    install_parser = subparsers.add_parser("install", help="Auto-configure MCP clients")
    install_parser.set_defaults(func=run_install)

    
    return parser

def parse_args(args=None):
    """Parse command line arguments."""
    parser = get_parser()
    return parser.parse_args(args)

def main():
    # Load Global Env first (Fallback)
    home_dir = os.path.expanduser("~")
    global_env = os.path.join(home_dir, ".hive_mind", ".env")
    if os.path.exists(global_env):
        load_dotenv(global_env)
        
    # Load Local Env (Override)
    load_dotenv(override=True)
    
    args = parse_args()
    
    try:
        asyncio.run(args.func(args))
    except KeyboardInterrupt:
        logger.warning("operation_cancelled")
    except Exception as e:
        logger.error("cli_error", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
