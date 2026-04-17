"""Entrypoint for the PySide6 messenger client."""

from __future__ import annotations

import argparse
import sys

from PySide6.QtWidgets import QApplication

from messenger_app.ui.main_window import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PyMessenger desktop app")
    parser.add_argument("--server", default="ws://127.0.0.1:8765", help="Signaling server websocket URL")
    parser.add_argument("--user", default="user1", help="User id for this client instance")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = QApplication(sys.argv)
    window = MainWindow(server_url=args.server, user_id=args.user)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

