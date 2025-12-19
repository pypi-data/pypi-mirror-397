import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class TaskStore:
    def __init__(self, db_path: str = "var/tasks.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    category TEXT,
                    description TEXT,
                    priority INTEGER,
                    status TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    metadata TEXT
                )
            """)
            conn.commit()

    def add_task(self, task_id: str, category: str, description: str, priority: int = 3, status: str = "PENDING", metadata: Dict[str, Any] = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks (id, category, description, priority, status, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id, 
                category, 
                description, 
                priority, 
                status, 
                datetime.utcnow().isoformat(), 
                datetime.utcnow().isoformat(),
                str(metadata) if metadata else "{}"
            ))
            conn.commit()

    def get_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM tasks"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def update_status(self, task_id: str, status: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?
            """, (status, datetime.utcnow().isoformat(), task_id))
            conn.commit()
