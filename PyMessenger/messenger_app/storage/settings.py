"""Persistent app settings for profile and server configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

DEFAULT_SETTINGS: Dict[str, str] = {
    "display_name": "",
    "user_id": "",
    "server_url": "ws://127.0.0.1:8765",
}


def settings_path() -> Path:
    base = Path(".messenger")
    base.mkdir(parents=True, exist_ok=True)
    return base / "profile.json"


def load_settings() -> Dict[str, str]:
    path = settings_path()
    if not path.exists():
        return DEFAULT_SETTINGS.copy()
    data = json.loads(path.read_text(encoding="utf-8"))
    merged = DEFAULT_SETTINGS.copy()
    merged.update({k: str(v) for k, v in data.items()})
    return merged


def save_settings(settings: Dict[str, str]) -> None:
    path = settings_path()
    merged = DEFAULT_SETTINGS.copy()
    merged.update(settings)
    path.write_text(json.dumps(merged, indent=2), encoding="utf-8")

