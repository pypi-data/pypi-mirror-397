import sqlite3
import logging
from typing import Optional, Dict
import json

logger = logging.getLogger(__name__)

class StateManager:
    """
    Persists workflow execution state to SQLite to support recovery.
    """
    def __init__(self, db_path: str = "workflow_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_state (
                        run_id TEXT PRIMARY KEY,
                        workflow_name TEXT,
                        status TEXT,
                        last_step TEXT,
                        context_json TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        except Exception as e:
            logger.error(f"Failed to init DB: {e}")

    def save_state(self, run_id: str, workflow_name: str, status: str, last_step: str, context: Dict):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO workflow_state 
                    (run_id, workflow_name, status, last_step, context_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (run_id, workflow_name, status, last_step, json.dumps(context)))
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def load_state(self, run_id: str) -> Optional[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM workflow_state WHERE run_id = ?", (run_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        "run_id": row[0],
                        "workflow_name": row[1],
                        "status": row[2],
                        "last_step": row[3],
                        "context": json.loads(row[4])
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None
