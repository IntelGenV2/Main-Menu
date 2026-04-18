"""Lightweight signaling/bootstrap server for peer discovery and room fanout."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, Set
import uuid

from websockets.asyncio.server import ServerConnection, serve


CLIENTS: Dict[str, ServerConnection] = {}
KNOWN_USERS_PATH = Path(".messenger/server_users.json")
ROOMS_PATH = Path(".messenger/server_rooms.json")


def load_known_users() -> Dict[str, str]:
    KNOWN_USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if KNOWN_USERS_PATH.exists():
        try:
            data = json.loads(KNOWN_USERS_PATH.read_text(encoding="utf-8"))
            return {str(k): str(v) for k, v in data.items()}
        except Exception:
            return {}
    return {}


def save_known_users(data: Dict[str, str]) -> None:
    KNOWN_USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    KNOWN_USERS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_rooms() -> Dict[str, Set[str]]:
    ROOMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if ROOMS_PATH.exists():
        try:
            data = json.loads(ROOMS_PATH.read_text(encoding="utf-8"))
            return {str(room_id): set(str(x) for x in members) for room_id, members in data.items()}
        except Exception:
            return {}
    return {}


def save_rooms() -> None:
    ROOMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    serializable = {room_id: sorted(list(members)) for room_id, members in ROOMS.items()}
    ROOMS_PATH.write_text(json.dumps(serializable, indent=2), encoding="utf-8")


ROOMS: Dict[str, Set[str]] = load_rooms()


def server_message(message_type: str, sender_id: str, payload: dict) -> dict:
    return {
        "type": message_type,
        "sender_id": sender_id,
        "message_id": f"srv-{uuid.uuid4()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }


async def broadcast_presence(user_id: str, online: bool) -> None:
    payload = json.dumps(server_message("presence", user_id, {"online": online}))
    stale: Set[str] = set()
    for peer_id, ws in CLIENTS.items():
        try:
            await ws.send(payload)
        except Exception:
            stale.add(peer_id)
    for peer_id in stale:
        CLIENTS.pop(peer_id, None)


async def route_message(sender_id: str, body: dict) -> None:
    recipient_id = body.get("recipient_id")
    room_id = body.get("room_id")
    if recipient_id:
        ws = CLIENTS.get(recipient_id)
        if ws:
            await ws.send(json.dumps(body))
        return
    if room_id:
        members = ROOMS.get(room_id, set())
        for member in members:
            if member == sender_id:
                continue
            ws = CLIENTS.get(member)
            if ws:
                await ws.send(json.dumps(body))
        return

    # Fallback: broadcast unknown-target message to all peers except sender.
    for peer_id, ws in CLIENTS.items():
        if peer_id != sender_id:
            await ws.send(json.dumps(body))


async def handler(websocket: ServerConnection) -> None:
    known_users = load_known_users()
    user_id: str | None = None
    try:
        async for raw in websocket:
            body = json.loads(raw)
            msg_type = body.get("type")
            if msg_type == "auth":
                user_id = body.get("sender_id")
                if not user_id:
                    await websocket.send(json.dumps(server_message("error", "server", {"reason": "missing sender_id"})))
                    continue
                CLIENTS[user_id] = websocket
                display_name = body.get("payload", {}).get("display_name") or user_id
                known_users[user_id] = str(display_name)
                save_known_users(known_users)
                await websocket.send(
                    json.dumps(
                        server_message(
                            "ack",
                            "server",
                            {
                                "ok": True,
                                "user_id": user_id,
                                "known_users": known_users,
                                "rooms": sorted(list(ROOMS.keys())),
                            },
                        )
                    )
                )
                await broadcast_presence(user_id, True)
                continue
            if not user_id:
                await websocket.send(json.dumps(server_message("error", "server", {"reason": "auth required"})))
                continue
            if msg_type == "room_join":
                room_id = body.get("room_id")
                if room_id:
                    ROOMS.setdefault(room_id, set()).add(user_id)
                    save_rooms()
                    await websocket.send(
                        json.dumps(server_message("ack", "server", {"joined_room": room_id}))
                    )
                continue
            await route_message(user_id, body)
    finally:
        if user_id:
            CLIENTS.pop(user_id, None)
            for members in ROOMS.values():
                members.discard(user_id)
            save_rooms()
            await broadcast_presence(user_id, False)


async def run_server(host: str = "0.0.0.0", port: int = 8765) -> None:
    async with serve(handler, host, port):
        print(f"signaling server running on ws://{host}:{port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(run_server())

