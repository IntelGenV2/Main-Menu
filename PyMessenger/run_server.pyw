"""Double-click launcher for signaling server (no terminal window)."""

import asyncio

from signaling_service.server import run_server


if __name__ == "__main__":
    asyncio.run(run_server())

