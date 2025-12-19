"""
ESM Baseline Store - SQLite + Hash-Chain
=========================================
Stores ESM spectral fingerprints with tamper-evident hash chaining.
"""

import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class ESMBaselineStore:
    """
    SQLite-backed store for ESM fingerprints with hash-chain integrity.
    
    Each record includes:
    - session_id: Unique session identifier
    - fingerprint: 192-dimension spectral vector (JSON)
    - prev_hash: Hash of the previous record (chain link)
    - curr_hash: SHA-256 of (prev_hash + fingerprint)
    """
    
    def __init__(self, db_path: str = "data/esm_baseline.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS esm_baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    curr_hash TEXT NOT NULL UNIQUE,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session ON esm_baselines(session_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON esm_baselines(timestamp)
            """)
            conn.commit()
    
    def _compute_hash(self, prev_hash: str, fingerprint: str) -> str:
        """Compute SHA-256 hash for chain integrity."""
        content = f"{prev_hash}:{fingerprint}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_latest_hash(self) -> str:
        """Get the hash of the most recent record (chain tip)."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT curr_hash FROM esm_baselines ORDER BY id DESC LIMIT 1"
            ).fetchone()
            return row[0] if row else "GENESIS"
    
    def store(
        self,
        session_id: str,
        fingerprint: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a new ESM fingerprint with hash-chain linking.
        
        Args:
            session_id: Session identifier
            fingerprint: 192-dimension spectral vector
            metadata: Optional metadata dict
        
        Returns:
            Record with id, timestamp, and hash
        """
        timestamp = datetime.utcnow().isoformat()
        fp_json = json.dumps(fingerprint)
        prev_hash = self._get_latest_hash()
        curr_hash = self._compute_hash(prev_hash, fp_json)
        meta_json = json.dumps(metadata) if metadata else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO esm_baselines 
                (session_id, timestamp, fingerprint, prev_hash, curr_hash, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, timestamp, fp_json, prev_hash, curr_hash, meta_json)
            )
            conn.commit()
            record_id = cursor.lastrowid
        
        return {
            "id": record_id,
            "session_id": session_id,
            "timestamp": timestamp,
            "curr_hash": curr_hash,
            "prev_hash": prev_hash,
        }
    
    def verify_chain(self) -> Dict[str, Any]:
        """
        Verify the integrity of the entire hash chain.
        
        Returns:
            {"valid": bool, "records": int, "broken_at": Optional[int]}
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, fingerprint, prev_hash, curr_hash FROM esm_baselines ORDER BY id"
            ).fetchall()
        
        if not rows:
            return {"valid": True, "records": 0, "broken_at": None}
        
        expected_prev = "GENESIS"
        for row in rows:
            record_id, fp_json, prev_hash, curr_hash = row
            
            # Check chain link
            if prev_hash != expected_prev:
                return {"valid": False, "records": len(rows), "broken_at": record_id}
            
            # Verify hash
            computed = self._compute_hash(prev_hash, fp_json)
            if computed != curr_hash:
                return {"valid": False, "records": len(rows), "broken_at": record_id}
            
            expected_prev = curr_hash
        
        return {"valid": True, "records": len(rows), "broken_at": None}
    
    def get_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve all fingerprints for a session."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT id, timestamp, fingerprint, curr_hash 
                FROM esm_baselines 
                WHERE session_id = ? 
                ORDER BY id
                """,
                (session_id,)
            ).fetchall()
        
        return [
            {
                "id": r[0],
                "timestamp": r[1],
                "fingerprint": json.loads(r[2]),
                "curr_hash": r[3],
            }
            for r in rows
        ]
