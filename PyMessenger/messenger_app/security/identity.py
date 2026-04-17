"""Identity keypair persistence for TOFU key exchange."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from messenger_app.security.crypto import generate_identity_keypair


def load_or_create_identity(user_id: str) -> Dict[str, str]:
    base_dir = Path(".messenger")
    base_dir.mkdir(parents=True, exist_ok=True)
    path = base_dir / f"identity_{user_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    private_key_b64, public_key_b64 = generate_identity_keypair()
    identity = {
        "user_id": user_id,
        "private_key_b64": private_key_b64,
        "public_key_b64": public_key_b64,
    }
    path.write_text(json.dumps(identity, indent=2), encoding="utf-8")
    return identity
