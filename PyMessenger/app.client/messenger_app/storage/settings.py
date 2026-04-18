"""Persistent app settings for profile and server configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_SETTINGS: Dict[str, Any] = {
    "display_name": "",
    "user_id": "",
    "server_url": "",
    "friends": [],
    "rooms": [],
}


def settings_path() -> Path:
    base = Path(".messenger")
    base.mkdir(parents=True, exist_ok=True)
    return base / "profile.json"


def load_settings() -> Dict[str, Any]:
    path = settings_path()
    if not path.exists():
        return DEFAULT_SETTINGS.copy()
    data = json.loads(path.read_text(encoding="utf-8"))
    merged = DEFAULT_SETTINGS.copy()
    for key, value in data.items():
        if key in ("friends", "rooms") and isinstance(value, list):
            merged[key] = [str(x) for x in value]
        else:
            merged[key] = str(value)
    return merged


def save_settings(settings: Dict[str, Any]) -> None:
    path = settings_path()
    merged = DEFAULT_SETTINGS.copy()
    merged.update(settings)
    path.write_text(json.dumps(merged, indent=2), encoding="utf-8")

