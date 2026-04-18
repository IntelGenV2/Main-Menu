# Intel Byte — signaling server

Lightweight **WebSocket** router: presence, rooms, message fan-out. **No PySide6** — only [`websockets`](https://websockets.readthedocs.io/). The process **does not scan the LAN** or prefer local networks; it listens on **`0.0.0.0`** so it can accept connections from **any** path that reaches the Pi (same Wi‑Fi, another city, another country), as long as the **client** is given the correct **`ws://` or `wss://`** URL (usually your **public** hostname or IP and forwarded port).

## Run (any OS)

```bash
cd app.server   # this folder
pip install -r requirements.txt
python3 -m signaling_service
```

Optional bind (defaults are correct for a Raspberry Pi behind a router):

```bash
python3 -m signaling_service --host 0.0.0.0 --port 8765
```

Same as `python3 signaling_service/server.py` if your working directory is **`app.server/`**.

### Windows (small status window)

Double-click **`run_server.pyw`** — logs append to **`app.server/.messenger/server.log`**.

### Linux / Raspberry Pi 5 (headless)

Raspberry Pi OS (64-bit) on **Pi 5** is supported: use **Python 3** from the OS (`python3` is usually 3.11+). Dependencies are pure Python wheels on **aarch64** in most cases.

```bash
chmod +x run_server.sh
./run_server.sh
```

Custom port example:

```bash
./run_server.sh --port 9000
```

Or run under **systemd** so it survives reboots (adjust paths and user):

```ini
[Unit]
Description=Intel Byte signaling (WebSocket)
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Main-Menu/PyMessenger/app.server
ExecStart=/usr/bin/python3 -m signaling_service --host 0.0.0.0 --port 8765
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then: `sudo systemctl enable --now intelbyte256-signaling.service`

## Remote clients (e.g. server in Fraser Valley, client in the US)

No LAN is required.

1. **Router** at the server site: **forward TCP** (e.g. **8765**) to the Pi’s **LAN IP** (DHCP reservation recommended so the forward target does not drift).
2. **Firewall** on the Pi (e.g. UFW): `sudo ufw allow 8765/tcp` if applicable.
3. **Clients** enter **`ws://YOUR_PUBLIC_HOSTNAME_OR_IP:8765`** (or **`wss://…`** if you terminate TLS with a reverse proxy). They must **not** use `0.0.0.0` or a private `192.168.x.x` address unless that client is actually on the same private network.
4. If your ISP uses **CGNAT**, a simple port forward may not work from the public internet; use a tunnel (Tailscale, Cloudflare Tunnel, etc.) or a VPS with a public IP.

## Optional: same-building / LAN testing

If a phone or laptop is on the **same** Wi‑Fi as the Pi, you *may* use the Pi’s **private** `ws://192.168.x.x:8765` URL. That is optional convenience only; **cross-region use always goes through your public URL (or VPN), not LAN discovery.**

## Files

Server state lives under **`app.server/.messenger/`** when the working directory is `app.server/` (`server_users.json`, `server_rooms.json`, `server.log`).

## Security note

The bundled server speaks **plain `ws://`** unless you put **TLS** in front (e.g. nginx / Caddy) and give clients **`wss://`**. There are no built-in accounts; do not expose broadly without hardening.
