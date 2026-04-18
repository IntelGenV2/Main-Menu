"""Allow: python3 -m signaling_service (from the app.server/ directory)."""

from __future__ import annotations

import argparse
import asyncio

from .server import run_server


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Intel Byte signaling server (WebSocket only). "
        "Binds to all interfaces by default so port-forwarded internet clients can connect."
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Listen address (default 0.0.0.0 = every interface; required for Pi + router port forward).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="TCP port (default 8765; forward this port from your router to the Pi).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(run_server(host=args.host, port=args.port))
