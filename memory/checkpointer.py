"""
LangGraph SQLite Checkpointer for persistent Short-Term Memory.
Persists conversation state across page reloads and server restarts.
"""
import os
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

DB_PATH = os.path.join(os.path.dirname(__file__), "checkpoints.db")
_checkpointer_instance = None
_sqlite_conn = None


def get_checkpointer() -> SqliteSaver:
    """Returns singleton instance of the persistent SQLite checkpointer."""
    global _checkpointer_instance, _sqlite_conn
    if _checkpointer_instance is None:
        _sqlite_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _checkpointer_instance = SqliteSaver(_sqlite_conn)
        _checkpointer_instance.setup()
    return _checkpointer_instance


def reset_checkpointer():
    """Resets the checkpointer instance for testing."""
    global _checkpointer_instance, _sqlite_conn
    if _sqlite_conn:
        try:
            _sqlite_conn.close()
        except Exception:
            pass
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass
    _sqlite_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    _checkpointer_instance = SqliteSaver(_sqlite_conn)
    _checkpointer_instance.setup()
    return _checkpointer_instance
