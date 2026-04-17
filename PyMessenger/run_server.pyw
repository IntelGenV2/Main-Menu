"""Double-click launcher for signaling server with visible status window."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
import sys
import threading
import tkinter as tk
from tkinter import messagebox

from signaling_service.server import run_server


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
    root.title("Intel Byte 256 Server")
    root.geometry("520x180")
    root.resizable(False, False)

    title = tk.Label(root, text="Intel Byte 256 Signaling Server", font=("Segoe UI", 12, "bold"))
    title.pack(pady=(14, 6))

    status = tk.Label(root, text="Server state: starting")
    status.pack(pady=4)
    url = tk.Label(root, text="URL: ws://0.0.0.0:8765")
    url.pack(pady=4)
    log = tk.Label(root, text=f"Log file: {log_file}")
    log.pack(pady=4)

    hint = tk.Label(root, text="Keep this window open while others connect.")
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

