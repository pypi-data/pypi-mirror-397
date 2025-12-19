import os
import json
import glob
from typing import List, Dict, Any

def load_usage() -> Dict[str, Any]:
    """
    Loads usage data from ~/.mcp_orchestrator/usage.json.
    Returns empty dict if file missing or invalid.
    """
    path = os.path.expanduser("~/.mcp_orchestrator/usage.json")
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except: 
            return {}
    return {}

def load_sessions(artifacts_dir: str = ".hive_mind") -> List[Dict[str, Any]]:
    """
    Scans the artifacts directory for session metadata.
    Structure: artifacts_dir/TYPE/SESSION_TIMESTAMP_SLUG/metadata.json
    """
    if not os.path.exists(artifacts_dir):
        return []
    
    sessions = []
    # Sort type directories to ensure stability
    for type_dir in sorted(glob.glob(os.path.join(artifacts_dir, "*"))):
        if os.path.isdir(type_dir):
            session_type = os.path.basename(type_dir)
            # Sort session directories
            for session_path in sorted(glob.glob(os.path.join(type_dir, "*")), reverse=True):
                if os.path.isdir(session_path):
                    meta_path = os.path.join(session_path, "metadata.json")
                    # Parse full timestamp from directory name (YYYY-MM-DD_HH-MM-SS)
                    parts = os.path.basename(session_path).split("_")
                    date_str = parts[0]
                    # Handle case where split might not produce enough parts if folder naming changed
                    time_str = parts[1].replace("-", ":") if len(parts) > 1 else ""
                    display_time = f"{date_str} {time_str}".strip()

                    meta = {}
                    if os.path.exists(meta_path):
                        try:
                            with open(meta_path, "r") as f: meta = json.load(f)
                        except: pass
                    
                    sessions.append({
                        "Type": session_type,
                        "Topic": meta.get("topic") or meta.get("prompt") or f"{session_type.replace('_', ' ').title()} ({meta.get('content_length', '?')} chars)",
                        "Time": meta.get("start_time") or display_time,
                        "Path": session_path,
                        "Files": len(glob.glob(os.path.join(session_path, "*"))),
                        "Cost": meta.get("cost", 0.0) 
                    })
    return sessions
