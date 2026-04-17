"""Encrypted local chat history backed by sqlite."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
from typing import List

from messenger_app.security.crypto import CryptoBox


@dataclass
class StoredMessage:
    room_or_peer: str
    sender_id: str
    body: str
    created_at: str


class HistoryStore:
    def __init__(self, db_path: Path, secret: str) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.crypto = CryptoBox(secret)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_or_peer TEXT NOT NULL,
                    sender_id TEXT NOT NULL,
                    body_cipher TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_message(self, room_or_peer: str, sender_id: str, body: str, created_at: str) -> None:
        cipher = self.crypto.encrypt_text(body)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO messages(room_or_peer, sender_id, body_cipher, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (room_or_peer, sender_id, cipher, created_at),
            )
            conn.commit()

    def list_messages(self, room_or_peer: str, limit: int = 200) -> List[StoredMessage]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT room_or_peer, sender_id, body_cipher, created_at
                FROM messages
                WHERE room_or_peer = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (room_or_peer, limit),
            ).fetchall()
        rows.reverse()
        return [
            StoredMessage(
                room_or_peer=row[0],
                sender_id=row[1],
                body=self.crypto.decrypt_text(row[2]),
                created_at=row[3],
            )
            for row in rows
        ]

