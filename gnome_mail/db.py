"""All SQLite operations for Gnome Mail. No Pygame dependencies."""

import os
import sqlite3
from datetime import datetime, timezone

from gnome_mail.constants import DB_DIR, DB_NAME

_DB_PATH = None


def _get_db_path():
    global _DB_PATH
    if _DB_PATH is None:
        base = os.path.join(os.path.expanduser("~"), ".local", "share", DB_DIR)
        os.makedirs(base, exist_ok=True)
        _DB_PATH = os.path.join(base, DB_NAME)
    return _DB_PATH


def _connect():
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            model TEXT NOT NULL,
            subject TEXT NOT NULL,
            user_message TEXT NOT NULL,
            assistant_response TEXT,
            status TEXT DEFAULT 'pending',
            error_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gnome_names (
            model TEXT PRIMARY KEY,
            gnome_name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_conversation(id, model, subject, user_message):
    conn = _connect()
    conn.execute(
        "INSERT INTO conversations (id, model, subject, user_message, status) VALUES (?, ?, ?, ?, 'pending')",
        (id, model, subject, user_message),
    )
    conn.commit()
    conn.close()


def update_response(id, response_text):
    conn = _connect()
    conn.execute(
        "UPDATE conversations SET assistant_response = ?, status = 'complete', completed_at = ? WHERE id = ?",
        (response_text, datetime.now(timezone.utc).isoformat(), id),
    )
    conn.commit()
    conn.close()


def update_error(id, error_text):
    conn = _connect()
    conn.execute(
        "UPDATE conversations SET status = 'error', error_text = ? WHERE id = ?",
        (error_text, id),
    )
    conn.commit()
    conn.close()


def get_conversations(offset=0, limit=20):
    conn = _connect()
    rows = conn.execute(
        "SELECT id, model, subject, status, created_at FROM conversations ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_conversation(id):
    conn = _connect()
    row = conn.execute("SELECT * FROM conversations WHERE id = ?", (id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_total_count():
    conn = _connect()
    count = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
    conn.close()
    return count


def delete_conversation(id):
    conn = _connect()
    conn.execute("DELETE FROM conversations WHERE id = ?", (id,))
    conn.commit()
    conn.close()


def reset_to_pending(id):
    """Reset a failed/error conversation back to pending for resend."""
    conn = _connect()
    conn.execute(
        "UPDATE conversations SET status = 'pending', error_text = NULL WHERE id = ?",
        (id,),
    )
    conn.commit()
    conn.close()


def get_all_gnome_names():
    """Return dict of {model: gnome_name} from the gnome_names table."""
    conn = _connect()
    rows = conn.execute("SELECT model, gnome_name FROM gnome_names").fetchall()
    conn.close()
    return {r["model"]: r["gnome_name"] for r in rows}


def set_gnome_name(model, gnome_name):
    """Set or update a custom gnome name for a model."""
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO gnome_names (model, gnome_name) VALUES (?, ?)",
        (model, gnome_name),
    )
    conn.commit()
    conn.close()
