"""File transfer helpers with chunking and simple validation."""

from __future__ import annotations

import base64
from pathlib import Path
import uuid
from typing import Generator, Tuple

CHUNK_SIZE = 64 * 1024
MAX_FILE_SIZE = 25 * 1024 * 1024


def validate_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise ValueError(f"File too large ({size} bytes). Max is {MAX_FILE_SIZE}.")


def build_transfer_id() -> str:
    return str(uuid.uuid4())


def iter_chunks_b64(path: Path) -> Generator[Tuple[int, str], None, None]:
    validate_file(path)
    index = 0
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(CHUNK_SIZE)
            if not chunk:
                break
            yield index, base64.b64encode(chunk).decode("ascii")
            index += 1

