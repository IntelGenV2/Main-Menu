# Intel Byte 256 — desktop client

PySide6 UI, local profile and keys. Connects to your **Raspberry Pi / app.server** WebSocket URL.

## Default signaling URL (Pi)

Edit **one line** before you ship a build:

- **[`messenger_app/hosting.py`](messenger_app/hosting.py)** — set `DEFAULT_SIGNALING_URL` to your public URL, e.g. `ws://yourname.duckdns.org:8765`. Leave `""` to always ask on first run.

Override without rebuilding:

```text
set INTELBYTE256_SERVER_URL=ws://your-pi:8765
```

## Run

```bash
cd app.client   # this folder
pip install -r requirements.txt
py -3 -m messenger_app.main
```

Or double-click **`run_client.pyw`** (Windows) after dependencies are installed.

Profile and keys: **`.messenger/`** here when this directory is the working directory (`app.client/.messenger/`).

## First-time setup

1. Run **app.server** on your Pi (see `../app.server/README.md`).
2. Setup asks for the **Pi signaling URL** (DDNS or public IP, port 8765). Local dev on one PC only: `ws://127.0.0.1:8765`.
3. Pick display name and user ID.

## Friends and channels

- **Sidebar:** **Add friend**, **New room**, **Copy invite**, **Copy ID** (same invite block as Settings).
- **User settings** — full friends list, invites, Pi URL, activity logs.

## Build executable (Windows)

From repo root:

```powershell
.\build\windows\build.ps1
```

Output: **`app.client/dist/IntelByte256/`**

## Troubleshooting

- **Connect failed** — Pi is running app.server, port **8765** forwarded, firewall open, URL matches (no `0.0.0.0` in the client).
- **Send disabled** — Connect first, then select a channel or DM.
- **Server log pane empty** — Expected if the server runs only on the Pi; that pane tails a local `server.log` when present.
