"""Lightweight signaling/bootstrap server for peer discovery and room fanout."""

from __future__ import annotations

import asyncio
import json
from typing import Dict, Set

from websockets.asyncio.server import ServerConnection, serve


CLIENTS: Dict[str, ServerConnection] = {}
ROOMS: Dict[str, Set[str]] = {}


async def broadcast_presence(user_id: str, online: bool) -> None:
    payload = json.dumps(
        {
            "type": "presence",
            "sender_id": user_id,
            "message_id": f"presence-{user_id}-{int(asyncio.get_running_loop().time())}",
            "timestamp": "",
            "payload": {"online": online},
        }
    )
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
    user_id: str | None = None
    try:
        async for raw in websocket:
            body = json.loads(raw)
            msg_type = body.get("type")
            if msg_type == "auth":
                user_id = body.get("sender_id")
                if not user_id:
                    await websocket.send(json.dumps({"type": "error", "payload": {"reason": "missing sender_id"}}))
                    continue
                CLIENTS[user_id] = websocket
                await websocket.send(json.dumps({"type": "ack", "payload": {"ok": True, "user_id": user_id}}))
                await broadcast_presence(user_id, True)
                continue
            if not user_id:
                await websocket.send(json.dumps({"type": "error", "payload": {"reason": "auth required"}}))
                continue
            if msg_type == "room_join":
                room_id = body.get("room_id")
                if room_id:
                    ROOMS.setdefault(room_id, set()).add(user_id)
                    await websocket.send(
                        json.dumps({"type": "ack", "payload": {"joined_room": room_id}})
                    )
                continue
            await route_message(user_id, body)
    finally:
        if user_id:
            CLIENTS.pop(user_id, None)
            for members in ROOMS.values():
                members.discard(user_id)
            await broadcast_presence(user_id, False)


async def run_server(host: str = "0.0.0.0", port: int = 8765) -> None:
    async with serve(handler, host, port):
        print(f"signaling server running on ws://{host}:{port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(run_server())

