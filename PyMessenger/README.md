# PyMessenger

PyMessenger is a Python desktop messaging prototype with a PySide6 GUI, lightweight signaling, and TOFU-based key exchange for encrypted direct messages.

## Architecture

- Client app: `messenger_app/`
- Signaling service: `signaling_service/server.py`
- Build scripts: `build/windows/build.ps1`

The signaling service only routes messages and key-exchange payloads. Direct message content is encrypted end-to-end once peers exchange keys.

## Security model (TOFU)

- Each user gets a local X25519 identity keypair on first run.
- First-seen peer key is trusted automatically (TOFU).
- If a peer key changes later, trust state becomes `key_changed` and the UI warns you.
- You can explicitly trust a changed key using the `Trust Key Change` control in direct chat mode.

## Run from source

1. `cd PyMessenger`
2. `python -m pip install -r requirements.txt`
3. Start signaling service:
   - `python signaling_service/server.py`
4. Start one or more clients:
   - `python messenger_app/main.py --user user1 --server ws://127.0.0.1:8765`
   - `python messenger_app/main.py --user user2 --server ws://127.0.0.1:8765`

## Remote friends setup recommendation

For friends in different locations, run signaling on an internet-reachable machine:

- Best: small VPS/VM with public IP/domain.
- Alternatives: a friend's PC with port-forward + dynamic DNS, or a tunnel service.

All of these keep the same client code path; only the `--server` URL changes.

## Build executable (Windows)

- Run: `PyMessenger/build/windows/build.ps1`
- Output: `dist/PyMessenger/`

## Current feature set

- Direct and room chat
- Presence and typing indicators
- Read receipts
- File transfer (chunked)
- Encrypted local history store
- Encrypted direct messaging with TOFU key exchange
