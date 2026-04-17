"""Message protocol models and helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from typing import Any, Dict, Literal, Optional
import uuid

MessageType = Literal[
    "auth",
    "presence",
    "typing",
    "chat",
    "file_offer",
    "file_chunk",
    "file_done",
    "room_join",
    "read_receipt",
    "key_exchange",
    "encrypted_chat",
    "ack",
    "error",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Envelope:
    """Wire envelope for every websocket payload."""

    type: MessageType
    sender_id: str
    message_id: str
    timestamp: str
    room_id: Optional[str] = None
    recipient_id: Optional[str] = None
    payload: Dict[str, Any] = None

    def to_json(self) -> str:
        body = asdict(self)
        body["payload"] = body.get("payload") or {}
        return json.dumps(body, ensure_ascii=True)

    @staticmethod
    def from_json(raw: str) -> "Envelope":
        body = json.loads(raw)
        required = {"type", "sender_id", "message_id", "timestamp"}
        missing = [k for k in required if k not in body]
        if missing:
            raise ValueError(f"Missing required protocol fields: {missing}")
        return Envelope(
            type=body["type"],
            sender_id=body["sender_id"],
            message_id=body["message_id"],
            timestamp=body["timestamp"],
            room_id=body.get("room_id"),
            recipient_id=body.get("recipient_id"),
            payload=body.get("payload") or {},
        )


def make_envelope(
    message_type: MessageType,
    sender_id: str,
    payload: Optional[Dict[str, Any]] = None,
    *,
    room_id: Optional[str] = None,
    recipient_id: Optional[str] = None,
) -> Envelope:
    return Envelope(
        type=message_type,
        sender_id=sender_id,
        message_id=str(uuid.uuid4()),
        timestamp=utc_now_iso(),
        room_id=room_id,
        recipient_id=recipient_id,
        payload=payload or {},
    )
