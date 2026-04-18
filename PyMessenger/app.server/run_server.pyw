"""Double-click launcher for signaling server with visible status window."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
import os
import socket
import sys
import threading
import tkinter as tk
from tkinter import messagebox

# Resolve `signaling_service` and `.messenger` paths from project root.
os.chdir(Path(__file__).resolve().parent)

from signaling_service.server import run_server

SERVER_PORT = 8765


def _guess_lan_ip() -> str | None:
    """Optional: local IPv4 for same-network testing only (not used for routing or discovery)."""
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.connect(("8.8.8.8", 80))
            return probe.getsockname()[0]
        finally:
            probe.close()
    except OSError:
        return None


def _start_server(log_file: Path, status_label: tk.Label) -> None:
    try:
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(f"\n[{datetime.now().isoformat()}] Starting signaling server.\n")
            fh.flush()
            old_out, old_err = sys.stdout, sys.stderr
            sys.stdout = fh
            sys.stderr = fh
            try:
                status_label.after(0, lambda: status_label.config(text="Server state: running"))
                asyncio.run(run_server())
            finally:
                sys.stdout = old_out
                sys.stderr = old_err
    except Exception as exc:
        status_label.after(0, lambda: status_label.config(text=f"Server state: failed ({exc})"))


def main() -> None:
    log_dir = Path(".messenger")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "server.log"

    root = tk.Tk()
    root.title("Intel Byte Signaling Server")
    root.geometry("540x300")
    root.resizable(False, False)

    title = tk.Label(root, text="Intel Byte Signaling Server", font=("Segoe UI", 12, "bold"))
    title.pack(pady=(14, 6))

    status = tk.Label(root, text="Server state: starting")
    status.pack(pady=4)
    url = tk.Label(
        root,
        text=f"Listening on all interfaces: ws://0.0.0.0:{SERVER_PORT} (clients must NOT use 0.0.0.0)",
        font=("Segoe UI", 9),
    )
    url.pack(pady=2)
    tk.Label(
        root,
        text=(
            "Internet / anywhere — router: forward TCP "
            f"{SERVER_PORT} to this machine. Clients use your public hostname or IP, e.g. "
            f"ws://your-name.duckdns.org:{SERVER_PORT} or wss://… if you add TLS in front."
        ),
        font=("Segoe UI", 9),
        wraplength=500,
        justify="center",
    ).pack(pady=2)
    lan_ip = _guess_lan_ip()
    if lan_ip:
        lan_line = f"Optional same-network test only: ws://{lan_ip}:{SERVER_PORT}"
    else:
        lan_line = f"Optional same-network test: ws://<this machine's LAN IPv4>:{SERVER_PORT}"
    tk.Label(root, text=lan_line, font=("Segoe UI", 9), fg="#555555").pack(pady=2)
    log = tk.Label(root, text=f"Log file: {log_file}")
    log.pack(pady=4)

    hint = tk.Label(
        root,
        text="Keep this window open. Remote clients only need the desktop app and your public ws:// or wss:// URL.",
        wraplength=500,
    )
    hint.pack(pady=(2, 10))

    def on_close() -> None:
        if messagebox.askyesno("Stop Server", "Stop signaling server and close window?"):
            root.destroy()

    tk.Button(root, text="Stop Server", command=on_close).pack(pady=6)

    thread = threading.Thread(target=_start_server, args=(log_file, status), daemon=True)
    thread.start()
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()

