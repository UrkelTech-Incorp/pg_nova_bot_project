"""SQLite persistence for chats the bot has been added to."""
import logging
import sqlite3
import time
from typing import List, NamedTuple, Optional

from config import DATABASE_NAME

logger = logging.getLogger(__name__)


class Chat(NamedTuple):
    chat_id: int
    title: str
    chat_type: str
    username: Optional[str]
    updated_at: int


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the chats table if it does not exist."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id   INTEGER PRIMARY KEY,
                title     TEXT,
                chat_type TEXT,
                username  TEXT,
                updated_at INTEGER
            )
            """
        )
        conn.commit()


def upsert_chat(
    chat_id: int, title: str, chat_type: str, username: Optional[str]
) -> None:
    """Insert or update a detected chat."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO chats (chat_id, title, chat_type, username, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                title=excluded.title,
                chat_type=excluded.chat_type,
                username=excluded.username,
                updated_at=excluded.updated_at
            """,
            (chat_id, title, chat_type, username, int(time.time())),
        )
        conn.commit()


def remove_chat(chat_id: int) -> None:
    """Forget a chat (e.g. when the bot is removed from it)."""
    with _connect() as conn:
        conn.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        conn.commit()


def list_chats() -> List[Chat]:
    """Return all known chats, most recently seen first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT chat_id, title, chat_type, username, updated_at "
            "FROM chats ORDER BY updated_at DESC"
        ).fetchall()
    return [
        Chat(r["chat_id"], r["title"], r["chat_type"], r["username"], r["updated_at"])
        for r in rows
    ]


def get_chat(chat_id: int) -> Optional[Chat]:
    with _connect() as conn:
        r = conn.execute(
            "SELECT chat_id, title, chat_type, username, updated_at "
            "FROM chats WHERE chat_id = ?",
            (chat_id,),
        ).fetchone()
    if r is None:
        return None
    return Chat(r["chat_id"], r["title"], r["chat_type"], r["username"], r["updated_at"])
