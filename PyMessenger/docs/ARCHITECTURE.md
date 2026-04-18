# Intel Byte 256 — architecture and hosting idea

This document is the **mental model** for how the project is laid out and how you (and friends) use it **without paying for a cloud “chat server” product**. You still need **one machine on the internet** that everyone can reach (for example a **Raspberry Pi 5** at home with port forwarding, or a free-tier VPS). That is “your server,” not a subscription to Discord.

## Two programs, two folders

| Piece | Folder | Role |
|--------|--------|------|
| **Signaling server** | `app.server/` | Runs on a **single** always-on machine (Pi, PC, VPS). Routes messages, rooms, presence. **No** PySide6 GUI in the server process itself. |
| **Desktop client** | `app.client/` | What you and friends install. PySide6 UI, keys, history. Connects **only** to a WebSocket URL you configure. |

### Default Pi URL (ship builds without editing scattered strings)

- **[`app.client/messenger_app/hosting.py`](../app.client/messenger_app/hosting.py)** — set `DEFAULT_SIGNALING_URL` to your DDNS/public `ws://` URL before distributing, **or** leave empty so first-run setup asks.
- Environment **`INTELBYTE256_SERVER_URL`** overrides the default without rebuilding.

They are **separate Python trees** on purpose:

- The client **does not** start the signaling server.
- Server state files live under **`app.server/.messenger/`** when the server’s working directory is `app.server/`.
- Client profile and keys live under **`app.client/.messenger/`** when the client runs from `app.client/`.

## How chatting works (simple)

1. You run **one** signaling server process somewhere reachable from the internet.
2. Every client uses the **same** `ws://` or `wss://` URL pointing at that host.
3. The server does **not** decrypt DMs; it forwards envelopes. Trust and E2E behavior live in the client.

So: **“Same app, different networks”** works when **everyone’s app points at the same server URL** and that URL is **actually reachable** (port forward, firewall, correct public IP or DDNS).

## Raspberry Pi 5

1. Put the `app.server/` tree on the Pi.
2. `pip install -r requirements.txt`
3. Run `python3 -m signaling_service` from `app.server/` (or systemd).
4. Router: **TCP 8765** → Pi.
5. Clients use `hosting.py` / setup / Settings with `ws://YOUR_PUBLIC_IP_OR_DDNS:8765`.

If your ISP uses **CGNAT**, use a tunnel (Tailscale, Cloudflare Tunnel, etc.).

## What is not in scope (yet)

- **Video / voice** needs WebRTC (and often TURN).
- **Global discovery** without a shared URL is not provided; you share **server URL + user ID** (invite).

## Where to read next

- **[../README.md](../README.md)** — repo map and quick links.
- **[../app.server/README.md](../app.server/README.md)** — run the signaling server (including Pi notes).
- **[../app.client/README.md](../app.client/README.md)** — run and build the desktop client, including **`hosting.py`**.

Keep this file when you forget **why** the repo is split: **one server many clients**, Pi-friendly.
