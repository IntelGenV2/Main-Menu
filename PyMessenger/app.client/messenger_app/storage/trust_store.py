"""TOFU trust store for peer public keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from messenger_app.security.crypto import fingerprint_public_key

TrustState = Literal["new", "trusted", "key_changed"]


class TrustStore:
    def __init__(self, user_id: str) -> None:
        self.path = Path(".messenger") / f"trust_{user_id}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {}

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def observe_peer_key(self, peer_id: str, peer_public_key_b64: str) -> TrustState:
        new_fp = fingerprint_public_key(peer_public_key_b64)
        record = self.data.get(peer_id)
        if record is None:
            self.data[peer_id] = {"public_key_b64": peer_public_key_b64, "fingerprint": new_fp}
            self._save()
            return "new"
        if record.get("fingerprint") != new_fp:
            return "key_changed"
        return "trusted"

    def accept_new_key(self, peer_id: str, peer_public_key_b64: str) -> None:
        self.data[peer_id] = {
            "public_key_b64": peer_public_key_b64,
            "fingerprint": fingerprint_public_key(peer_public_key_b64),
        }
        self._save()

    def get_peer_key(self, peer_id: str) -> str | None:
        rec = self.data.get(peer_id)
        if rec:
            return rec.get("public_key_b64")
        return None
