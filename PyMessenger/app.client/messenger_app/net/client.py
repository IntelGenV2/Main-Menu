"""Async websocket chat client with TOFU trust and encrypted direct chat."""

from __future__ import annotations

import asyncio
import base64
from pathlib import Path
from typing import Awaitable, Callable, Optional

from websockets.asyncio.client import ClientConnection, connect

from messenger_app.net.protocol import Envelope, make_envelope
from messenger_app.security.crypto import decrypt_direct_payload, encrypt_direct_payload
from messenger_app.security.identity import load_or_create_identity
from messenger_app.storage.history import HistoryStore
from messenger_app.storage.trust_store import TrustState, TrustStore

MessageCallback = Callable[[Envelope], Awaitable[None]]
StatusCallback = Callable[[str], Awaitable[None]]


class MessengerClient:
    def __init__(
        self,
        server_url: str,
        user_id: str,
        display_name: str,
        history_path: Path,
        history_secret: str,
    ) -> None:
        self.server_url = server_url
        self.user_id = user_id
        self.display_name = display_name
        self.history = HistoryStore(history_path, history_secret)
        self.identity = load_or_create_identity(user_id)
        self.trust_store = TrustStore(user_id)
        self.peer_keys: dict[str, str] = {}
        self.peer_trust: dict[str, TrustState] = {}
        self.pending_peer_keys: dict[str, str] = {}
        self.ws: Optional[ClientConnection] = None
        self.on_message: Optional[MessageCallback] = None
        self.on_status: Optional[StatusCallback] = None
        self._listen_task: Optional[asyncio.Task] = None
        self._incoming_files: dict[str, list[bytes]] = {}
        self._incoming_meta: dict[str, dict] = {}
        self.download_dir = Path(".messenger/downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.last_error: str = ""
        self.known_users: dict[str, str] = {}

    async def _emit_status(self, text: str) -> None:
        if self.on_status:
            await self.on_status(text)

    async def connect(self) -> None:
        """Open exactly one WebSocket to `server_url` (ws:// or wss:// only — no HTTP or other transports)."""
        url = (self.server_url or "").strip()
        if not url.startswith("ws://") and not url.startswith("wss://"):
            raise ValueError(
                "Server address must be a WebSocket URL starting with ws:// or wss:// (not http:// or a bare host)."
            )
        self.server_url = url
        self.last_error = ""
        self.ws = await connect(url)
        auth = make_envelope(
            "auth",
            self.user_id,
            {
                "device": "desktop",
                "public_key_b64": self.identity["public_key_b64"],
                "display_name": self.display_name,
            },
        )
        await self.ws.send(auth.to_json())
        await self._emit_status("Connected")
        self._listen_task = asyncio.create_task(self._listen_loop())

    async def close(self) -> None:
        if self._listen_task:
            self._listen_task.cancel()
        if self.ws:
            await self.ws.close()
        await self._emit_status("Disconnected")

    async def _listen_loop(self) -> None:
        assert self.ws is not None
        try:
            async for raw in self.ws:
                try:
                    env = Envelope.from_json(raw)
                except Exception as exc:
                    self.last_error = str(exc)
                    await self._emit_status(f"Protocol parse warning: {exc}")
                    continue
                await self._handle_incoming(env)
        except asyncio.CancelledError:
            return
        except Exception as exc:
            self.last_error = str(exc)
            await self._emit_status(f"Connection error: {exc}")

    async def _handle_incoming(self, env: Envelope) -> None:
        if env.type == "chat":
            key = env.room_id or env.sender_id
            self.history.save_message(key, env.sender_id, env.payload.get("text", ""), env.timestamp)
            # Automatically acknowledge delivered chat messages.
            await self.send_read_receipt(env.sender_id, env.message_id)
        elif env.type == "encrypted_chat":
            peer_key = self.peer_keys.get(env.sender_id)
            if peer_key:
                decrypted = decrypt_direct_payload(
                    self.identity["private_key_b64"],
                    peer_key,
                    env.payload,
                )
                env = Envelope(
                    type="chat",
                    sender_id=env.sender_id,
                    message_id=env.message_id,
                    timestamp=env.timestamp,
                    recipient_id=env.recipient_id,
                    room_id=env.room_id,
                    payload={"text": decrypted.get("text", "")},
                )
                self.history.save_message(env.sender_id, env.sender_id, env.payload.get("text", ""), env.timestamp)
                await self.send_read_receipt(env.sender_id, env.message_id)
        elif env.type == "key_exchange":
            peer_id = env.sender_id
            peer_public = env.payload.get("public_key_b64")
            if peer_public:
                state = self.trust_store.observe_peer_key(peer_id, peer_public)
                self.peer_trust[peer_id] = state
                if state in ("new", "trusted"):
                    self.peer_keys[peer_id] = peer_public
                else:
                    self.pending_peer_keys[peer_id] = peer_public
                await self._emit_status(f"Trust[{peer_id}]={state}")
        elif env.type == "ack":
            known_users = env.payload.get("known_users")
            if isinstance(known_users, dict):
                for user_id, display_name in known_users.items():
                    self.known_users[str(user_id)] = str(display_name)
        elif env.type == "file_offer":
            transfer_id = env.payload.get("transfer_id")
            if transfer_id:
                self._incoming_meta[transfer_id] = env.payload
                self._incoming_files[transfer_id] = []
        elif env.type == "file_chunk":
            transfer_id = env.payload.get("transfer_id")
            chunk_b64 = env.payload.get("chunk_b64", "")
            if transfer_id and transfer_id in self._incoming_files:
                self._incoming_files[transfer_id].append(base64.b64decode(chunk_b64.encode("ascii")))
        elif env.type == "file_done":
            transfer_id = env.payload.get("transfer_id")
            if transfer_id and transfer_id in self._incoming_files:
                meta = self._incoming_meta.get(transfer_id, {})
                name = meta.get("name", f"{transfer_id}.bin")
                out_path = self.download_dir / name
                with out_path.open("wb") as fh:
                    for chunk in self._incoming_files[transfer_id]:
                        fh.write(chunk)
                self._incoming_files.pop(transfer_id, None)
                self._incoming_meta.pop(transfer_id, None)
        if self.on_message:
            await self.on_message(env)

    async def join_room(self, room_id: str) -> None:
        await self._send(make_envelope("room_join", self.user_id, {}, room_id=room_id))

    async def send_presence(self, online: bool) -> None:
        await self._send(make_envelope("presence", self.user_id, {"online": online}))

    async def send_typing(self, target: str, is_room: bool, typing: bool = True) -> None:
        kwargs = {"room_id": target} if is_room else {"recipient_id": target}
        await self._send(make_envelope("typing", self.user_id, {"typing": typing}, **kwargs))

    async def send_chat(self, target: str, text: str, is_room: bool) -> str:
        kwargs = {"room_id": target} if is_room else {"recipient_id": target}
        if is_room:
            env = make_envelope("chat", self.user_id, {"text": text}, **kwargs)
        else:
            peer_key = self.peer_keys.get(target)
            if not peer_key:
                await self.send_key_exchange(target)
                raise RuntimeError(f"No trusted key for {target} yet. Ask them to connect once first.")
            encrypted = encrypt_direct_payload(self.identity["private_key_b64"], peer_key, {"text": text})
            env = make_envelope("encrypted_chat", self.user_id, encrypted, **kwargs)
        await self._send(env)
        key = target
        self.history.save_message(key, self.user_id, text, env.timestamp)
        return env.message_id

    async def send_key_exchange(self, recipient_id: str) -> None:
        await self._send(
            make_envelope(
                "key_exchange",
                self.user_id,
                {"public_key_b64": self.identity["public_key_b64"]},
                recipient_id=recipient_id,
            )
        )

    async def trust_peer_new_key(self, peer_id: str) -> None:
        pending = self.pending_peer_keys.get(peer_id)
        if pending:
            self.trust_store.accept_new_key(peer_id, pending)
            self.peer_keys[peer_id] = pending
            self.peer_trust[peer_id] = "trusted"
            self.pending_peer_keys.pop(peer_id, None)
            await self._emit_status(f"Trusted updated key for {peer_id}")
            return
        cached = self.trust_store.get_peer_key(peer_id)
        if cached:
            self.peer_keys[peer_id] = cached
            self.peer_trust[peer_id] = "trusted"
            await self._emit_status(f"Trusted existing key for {peer_id}")
            return
        await self._emit_status(f"No key available to trust for {peer_id}")

    async def send_file_offer(self, target: str, transfer_id: str, name: str, size: int, is_room: bool) -> None:
        kwargs = {"room_id": target} if is_room else {"recipient_id": target}
        await self._send(
            make_envelope("file_offer", self.user_id, {"transfer_id": transfer_id, "name": name, "size": size}, **kwargs)
        )

    async def send_file_chunk(self, target: str, transfer_id: str, chunk_b64: str, is_room: bool) -> None:
        kwargs = {"room_id": target} if is_room else {"recipient_id": target}
        await self._send(
            make_envelope("file_chunk", self.user_id, {"transfer_id": transfer_id, "chunk_b64": chunk_b64}, **kwargs)
        )

    async def send_file_done(self, target: str, transfer_id: str, is_room: bool) -> None:
        kwargs = {"room_id": target} if is_room else {"recipient_id": target}
        await self._send(make_envelope("file_done", self.user_id, {"transfer_id": transfer_id}, **kwargs))

    async def send_read_receipt(self, recipient_id: str, message_id: str) -> None:
        await self._send(
            make_envelope(
                "read_receipt",
                self.user_id,
                {"message_id": message_id},
                recipient_id=recipient_id,
            )
        )

    async def _send(self, env: Envelope) -> None:
        if not self.ws:
            raise RuntimeError("Not connected")
        await self.ws.send(env.to_json())

    def is_connected(self) -> bool:
        return self.ws is not None

