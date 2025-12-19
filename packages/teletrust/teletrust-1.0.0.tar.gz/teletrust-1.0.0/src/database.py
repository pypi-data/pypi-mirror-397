
import sqlite3
import logging
from typing import Any, List, Optional, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "teletrust.db"

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    Enables foreign keys and row factory.
    """
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise

def init_db():
    """
    Initializes the database schema if it doesn't exist.
    """
    schema = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stripe_customer_id TEXT UNIQUE NOT NULL,
        subscription_tier TEXT DEFAULT 'free',
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS billing_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stripe_customer_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        payload TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    conn = get_db_connection()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()

# Auto-initialize on import (Module-level singleton pattern for MVP)
init_db()

class SessionLocal:
    """
    Database session context manager for safe transaction handling.
    Replaces the previous mock class.
    """
    def __init__(self):
        self.conn = get_db_connection()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
        finally:
            self.conn.close()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        return self.conn.execute(query, params)

    def query_user(self, stripe_customer_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.execute("SELECT * FROM users WHERE stripe_customer_id = ?", (stripe_customer_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

class User:
    """
    ORM-lite wrapper for User operations.
    """
    def __init__(self, stripe_customer_id: str, id: int = None, subscription_tier: str = 'free'):
        self.stripe_customer_id = stripe_customer_id
        self.id = id
        self.subscription_tier = subscription_tier

def update_subscription(stripe_customer_id: str, new_tier: str) -> bool:
    """
    Updates a user's subscription tier.
    Replaces the empty 'pass' stub.
    """
    logger.info(f"Updating subscription for {stripe_customer_id} to {new_tier}")
    try:
        with SessionLocal() as db:
            # Upsert user logic
            cursor = db.execute(
                "SELECT id FROM users WHERE stripe_customer_id = ?",
                (stripe_customer_id,)
            )
            if cursor.fetchone():
                db.execute(
                    "UPDATE users SET subscription_tier = ? WHERE stripe_customer_id = ?",
                    (new_tier, stripe_customer_id)
                )
            else:
                db.execute(
                    "INSERT INTO users (stripe_customer_id, subscription_tier) VALUES (?, ?)",
                    (stripe_customer_id, new_tier)
                )
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to update subscription: {e}")
        return False

def log_stripe_event(stripe_customer_id: str, event_type: str, payload: str = "") -> bool:
    """
    Logs a raw stripe event to the audit table.
    """
    try:
        with SessionLocal() as db:
            db.execute(
                "INSERT INTO billing_events (stripe_customer_id, event_type, payload) VALUES (?, ?, ?)",
                (stripe_customer_id, event_type, payload)
            )
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to log event: {e}")
        return False
