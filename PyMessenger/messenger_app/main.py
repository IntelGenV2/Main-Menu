"""Entrypoint for the PySide6 messenger client."""

from __future__ import annotations

import argparse
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from messenger_app.storage.settings import load_settings, save_settings
from messenger_app.ui.setup_dialog import SetupDialog
from messenger_app.ui.main_window import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Intel Byte 256 desktop app")
    parser.add_argument("--server", default="", help="Signaling server websocket URL")
    parser.add_argument("--user", default="", help="User id for this client instance")
    parser.add_argument("--name", default="", help="Display name")
    parser.add_argument("--setup", action="store_true", help="Force setup dialog")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = QApplication(sys.argv)
    settings = load_settings()
    if args.user:
        settings["user_id"] = args.user
    if args.server:
        settings["server_url"] = args.server
    if args.name:
        settings["display_name"] = args.name

    needs_setup = args.setup or not settings.get("user_id") or not settings.get("server_url")
    if needs_setup:
        dialog = SetupDialog(
            settings.get("display_name", ""),
            settings.get("user_id", ""),
            settings.get("server_url", "ws://127.0.0.1:8765"),
        )
        if dialog.exec() != dialog.DialogCode.Accepted:
            return 0
        settings.update(dialog.result_settings())
        save_settings(settings)
    else:
        # Keep cli overrides persistent for non-technical users.
        save_settings(settings)

    if not settings.get("user_id"):
        QMessageBox.warning(None, "Missing user id", "User ID is required to start the client.")
        return 1

    window = MainWindow(
        server_url=settings["server_url"],
        user_id=settings["user_id"],
        display_name=settings.get("display_name", settings["user_id"]),
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

