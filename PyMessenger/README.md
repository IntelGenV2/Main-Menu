# Intel Byte 256

Intel Byte 256 is a desktop chat app with a PySide6 GUI, a lightweight signaling server, and encrypted direct messaging with TOFU key trust.

## How server and clients work

- **Server** (`signaling_service/server.py`): message router. It helps clients find each other and pass packets. It does not manage accounts.
- **Client** (`messenger_app/`): chat UI + your local profile/keys.
- **Identity**: each user sets a `User ID` in setup. Friends exchange this ID.
- **Encryption**: direct messages are encrypted end-to-end after key exchange. First key is trusted (TOFU); changed keys are flagged.

## First-time setup

1. Open `Intel Byte 256` (project folder currently named `PyMessenger`).
2. Run `python -m pip install -r requirements.txt` once.
3. Start server (for local test):
   - `py -3 signaling_service/server.py`
4. Start client:
   - `py -3 -m messenger_app.main`
5. Setup dialog appears:
   - Enter display name
   - Enter user ID (example: `lawbo`)
   - Enter server URL (example local: `ws://127.0.0.1:8765`)
6. Click `Connect`.

Profile is saved in `.messenger/profile.json`, so next launch does not need terminal arguments.

## One-click launchers

- `run_client.pyw`: launches GUI client without terminal.
- `run_server.pyw`: launches server without terminal.

Double-clicking these files works after Python and dependencies are installed.

## Add a friend and start messaging

1. Share your ID shown as `My ID` in the right panel.
2. Ask your friend for their ID.
3. In `Start Direct Chat`, enter your friend's ID and click `Add Direct`.
4. The app auto-sends a key exchange to that friend.
5. Your friend does the same for your ID.
6. Start sending direct messages.

If trust shows `key_changed`, use `Trust Key Change` only if you verified with your friend out of band.

## How to know it is working

- **Server running:** `run_server.pyw` opens a small window showing `Server state: running` and writes logs to `.messenger/server.log`.
- **Server memory:** known user IDs/display names are saved in `.messenger/server_users.json` on the server host and reloaded next launch.
- **Room memory:** server room list is saved in `.messenger/server_rooms.json` and restored on next server launch.
- **Client memory:** your friend list and room list are saved in `.messenger/profile.json`.
- **Client connected:** the status badge in the right panel turns `Connected`, timeline shows `[connect] Connected to signaling server.`
- **Room joined:** timeline shows `[room] Joined room: <room-id>`.
- **Friend added:** timeline shows `[friend] Added direct chat target: <friend-id>`.
- **Key exchange status:** direct chat row gets a state badge like `added`, `key_sent`, `key_received`, `trusted`, or `key_changed`.
- **Ready to message:** once key exchange is trusted, direct messages stop showing key errors and send normally.

## Local and remote testing

### Local (same PC or same network)

- Use server URL like `ws://127.0.0.1:8765` (same PC) or `ws://<LAN-IP>:8765` (same LAN).

### Remote (different locations)

- Run one signaling server on an internet-reachable host.
- Recommended: small VPS/VM with public IP/domain.
- Both clients set server URL to that host, e.g. `ws://your-domain-or-ip:8765`.

## Build executable (Windows)

- Run: `PyMessenger/build/windows/build.ps1`
- Output: `dist/IntelByte256/`

## Troubleshooting

- **Buttons seem to do nothing**
  - Check server state badge first.
  - If `Disconnected` or `Error`, click `Connect` and read timeline errors.
  - Some actions are disabled until connected.
- **`run_server.pyw` opens then closes**
  - Install dependencies first: `py -3 -m pip install -r requirements.txt`
  - Check `.messenger/server.log` for startup errors.
- **Cannot message friend**
  - Both clients must use the same server URL.
  - Both sides must add each other by User ID and exchange keys.
  - If state is `key_changed`, verify identity then click `Trust Key Change`.
- **Still getting protocol field errors**
  - Stop all old server/client instances.
  - Relaunch using updated code so all server `ack/error/presence` messages include full envelope fields.
- **Auto-start local server**
  - If server URL is local (`ws://127.0.0.1:8765`/`localhost`) and connect fails, client attempts to launch `run_server.pyw` then retries.
