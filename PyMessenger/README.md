# Intel Byte 256 (`PyMessenger`)

Desktop chat **client** (PySide6) plus a separate WebSocket **signaling server**. Friends use the same Pi URL; default URL for new installs is set in **[`app.client/messenger_app/hosting.py`](app.client/messenger_app/hosting.py)** (or env `INTELBYTE256_SERVER_URL`).

## Repo layout

| Path | What it is |
|------|------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Why client and server are split, Pi hosting idea. |
| [`app.client/`](app.client/) | GUI app (`messenger_app/`), `run_client.pyw`, `hosting.py`, client `requirements.txt`. |
| [`app.server/`](app.server/) | Signaling only (`signaling_service/`), `run_server.pyw`, `requirements.txt`. |
| [`requirements.txt`](requirements.txt) | Installs **both** app stacks (if present at repo root). |

## Quick start

**Signaling server** (e.g. on Raspberry Pi):

```bash
cd app.server
pip install -r requirements.txt
py -3 -m signaling_service
```

**Client** (each PC):

```bash
cd app.client
pip install -r requirements.txt
py -3 -m messenger_app.main
```

Windows: double-click **`app.client/run_client.pyw`** or **`app.server/run_server.pyw`**.

Server data: `app.server/.messenger/` when cwd is `app.server/`.  
Client data: `app.client/.messenger/` when cwd is `app.client/`.

## More documentation

- **[app.client/README.md](app.client/README.md)** — `hosting.py`, run, build EXE.
- **[app.server/README.md](app.server/README.md)** — Pi, port forward, systemd.
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — design overview.

## Build Windows EXE (client only)

```powershell
PyMessenger/build/windows/build.ps1
```

Output: **`app.client/dist/IntelByte256/`**
