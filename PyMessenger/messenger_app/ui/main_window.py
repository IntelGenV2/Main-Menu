"""PySide6 main window for the messenger desktop app."""

from __future__ import annotations

import asyncio
from pathlib import Path
import subprocess
import sys
from threading import Thread
from urllib.parse import urlparse

from PySide6.QtCore import QObject, Qt, Signal, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from messenger_app.net.client import MessengerClient
from messenger_app.net.file_transfer import build_transfer_id, iter_chunks_b64, validate_file
from messenger_app.net.protocol import Envelope
from messenger_app.storage.settings import load_settings, save_settings
from messenger_app.ui.setup_dialog import SetupDialog
from messenger_app.ui.widgets.chat_widgets import ConversationList


class UiBus(QObject):
    message_received = Signal(str)
    status_changed = Signal(str)
    presence_updated = Signal(str)
    typing_updated = Signal(str)


class MainWindow(QMainWindow):
    def __init__(self, server_url: str, user_id: str, display_name: str) -> None:
        super().__init__()
        self.server_url = server_url
        self.user_id = user_id
        self.display_name = display_name
        self.bus = UiBus()
        self.setWindowTitle(f"Intel Byte 256 - {display_name} ({user_id})")
        self.resize(1100, 720)

        self.client_loop = asyncio.new_event_loop()
        self.client = MessengerClient(
            server_url=self.server_url,
            user_id=self.user_id,
            display_name=self.display_name,
            history_path=Path(".messenger/history.sqlite"),
            history_secret=f"{user_id}-local-history",
        )
        self.client.on_message = self._on_message_async
        self.client.on_status = self._on_status_async

        self.active_target = "lobby"
        self.active_is_room = True
        self._pending_messages: dict[str, str] = {}
        self._friend_progress: dict[str, str] = {}
        self._online_peers: set[str] = set()
        self._server_state = "Disconnected"
        self._last_error = "-"
        self._reconnect_attempts = 0
        self._connected = False
        self._build_ui()
        self._wire_signals()
        self._start_client_thread()
        self._load_saved_conversations()
        self._update_server_diagnostics()
        self._update_action_states()
        self.timeline.append("[hint] Click Connect to check server reachability.")
        self.timeline.append("[hint] Add a friend by User ID in 'Start Direct Chat'.")
        QTimer.singleShot(300, lambda: self.connect_client(auto_start_local=True))

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)

        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("padding: 6px; color: #9aa0a6;")
        layout.addWidget(self.status_label)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, stretch=1)

        self.conversations = ConversationList()
        self.conversations.add_conversation("room:lobby")
        self.conversations.add_conversation("direct:friend1")
        self.conversations.setCurrentRow(0)
        self.conversations.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        splitter.addWidget(self.conversations)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        self.timeline = QTextEdit()
        self.timeline.setReadOnly(True)
        self.timeline.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.timeline.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.timeline.setPlaceholderText("Messages appear here...")
        center_layout.addWidget(self.timeline, stretch=1)

        compose_row = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")
        self.send_btn = QPushButton("Send")
        self.file_btn = QPushButton("Send File")
        compose_row.addWidget(self.message_input, stretch=1)
        compose_row.addWidget(self.send_btn)
        compose_row.addWidget(self.file_btn)
        center_layout.addLayout(compose_row)
        splitter.addWidget(center)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Profile"))
        self.edit_profile_btn = QPushButton("⚙ Profile Settings")
        self.my_id_label = QLabel(f"My ID: {self.user_id}")
        self.copy_id_btn = QPushButton("Copy My ID")
        right_layout.addWidget(self.edit_profile_btn)
        right_layout.addWidget(self.my_id_label)
        right_layout.addWidget(self.copy_id_btn)
        self.display_name_label = QLabel(f"Display Name: {self.display_name}")
        right_layout.addWidget(self.display_name_label)
        right_layout.addWidget(QLabel("Server Diagnostics"))
        self.server_state_label = QLabel("State: Disconnected")
        self.server_state_badge = QLabel("Disconnected")
        self.server_state_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.server_url_label = QLabel(f"URL: {self.server_url}")
        self.server_last_error_label = QLabel("Last Error: -")
        self.server_reconnect_label = QLabel("Reconnect Attempts: 0")
        self.server_peers_label = QLabel("Peers Online: 0")
        right_layout.addWidget(self.server_state_label)
        right_layout.addWidget(self.server_state_badge)
        right_layout.addWidget(self.server_url_label)
        right_layout.addWidget(self.server_last_error_label)
        right_layout.addWidget(self.server_reconnect_label)
        right_layout.addWidget(self.server_peers_label)
        self.target_input = QLineEdit("lobby")
        self.target_input.setReadOnly(True)
        self.mode_info = QLabel("Mode: room")
        self.new_room_input = QLineEdit()
        self.new_room_input.setPlaceholderText("new room id")
        self.new_direct_input = QLineEdit()
        self.new_direct_input.setPlaceholderText("direct user id")
        self.server_input = QLineEdit(self.server_url)
        self.save_server_btn = QPushButton("⚙ Server Settings")
        self.trust_label = QLabel("Trust: n/a")
        self.connect_btn = QPushButton("Connect")
        self.join_btn = QPushButton("Join Room")
        self.add_room_btn = QPushButton("Add Room")
        self.add_direct_btn = QPushButton("Add Direct")
        self.key_exchange_btn = QPushButton("Send Key")
        self.trust_key_btn = QPushButton("Trust Key Change")
        self.send_btn.setToolTip("Send message to selected room or friend")
        self.file_btn.setToolTip("Send a file to selected room or friend")
        self.connect_btn.setToolTip("Connect to the server URL shown below")
        self.join_btn.setToolTip("Join currently selected room")
        self.key_exchange_btn.setToolTip("Share your key with selected friend")
        self.trust_key_btn.setToolTip("Trust a changed friend key after verification")
        right_layout.addWidget(QLabel("Target ID"))
        right_layout.addWidget(self.target_input)
        right_layout.addWidget(self.mode_info)
        right_layout.addWidget(QLabel("Create / Add Room"))
        right_layout.addWidget(self.new_room_input)
        right_layout.addWidget(self.add_room_btn)
        right_layout.addWidget(QLabel("Start Direct Chat"))
        right_layout.addWidget(self.new_direct_input)
        right_layout.addWidget(self.add_direct_btn)
        right_layout.addWidget(QLabel("Server URL"))
        right_layout.addWidget(self.server_input)
        right_layout.addWidget(self.save_server_btn)
        right_layout.addWidget(self.trust_label)
        right_layout.addWidget(self.key_exchange_btn)
        right_layout.addWidget(self.trust_key_btn)
        right_layout.addWidget(self.connect_btn)
        right_layout.addWidget(self.join_btn)
        right_layout.addStretch(1)
        splitter.addWidget(right)

        splitter.setSizes([220, 620, 260])
        self.setCentralWidget(root)

        self.setStyleSheet(
            """
            QMainWindow, QWidget { background-color: #121417; color: #e6edf3; font-size: 13px; }
            QLineEdit, QTextEdit, QListWidget { background-color: #1d2128; border: 1px solid #2f3742; border-radius: 8px; padding: 6px; }
            QPushButton { background-color: #2563eb; border: 0; border-radius: 8px; padding: 8px 12px; color: white; }
            QPushButton:hover { background-color: #1d4ed8; }
            """
        )

    def _wire_signals(self) -> None:
        self.send_btn.clicked.connect(self.send_message)
        self.file_btn.clicked.connect(self.send_file)
        self.connect_btn.clicked.connect(self.connect_client)
        self.join_btn.clicked.connect(self.join_room)
        self.edit_profile_btn.clicked.connect(self.edit_profile)
        self.add_room_btn.clicked.connect(self.add_room)
        self.add_direct_btn.clicked.connect(self.add_direct)
        self.copy_id_btn.clicked.connect(self.copy_my_id)
        self.save_server_btn.clicked.connect(self.save_server_url)
        self.key_exchange_btn.clicked.connect(self.send_key_exchange)
        self.trust_key_btn.clicked.connect(self.trust_key_change)
        self.conversations.itemSelectionChanged.connect(self.select_conversation)
        self.conversations.customContextMenuRequested.connect(self.open_conversation_menu)
        self.timeline.customContextMenuRequested.connect(self.open_timeline_menu)
        self.message_input.textEdited.connect(self.on_typing)
        self.bus.message_received.connect(self.timeline.append)
        self.bus.status_changed.connect(self.status_label.setText)
        self.bus.presence_updated.connect(lambda x: self.timeline.append(f"[presence] {x}"))
        self.bus.typing_updated.connect(lambda x: self.timeline.append(f"[typing] {x}"))

    def _start_client_thread(self) -> None:
        def runner() -> None:
            asyncio.set_event_loop(self.client_loop)
            self.client_loop.run_forever()

        t = Thread(target=runner, daemon=True)
        t.start()

    async def _on_message_async(self, env: Envelope) -> None:
        if env.type == "chat":
            text = env.payload.get("text", "")
            self.bus.message_received.emit(f"{env.sender_id}: {text}")
            if env.sender_id != self.user_id:
                self._set_friend_progress(env.sender_id, "ready")
        elif env.type == "presence":
            online = bool(env.payload.get("online"))
            if online:
                self._online_peers.add(env.sender_id)
            else:
                self._online_peers.discard(env.sender_id)
            self._update_server_diagnostics()
            self.bus.presence_updated.emit(f"{env.sender_id} -> {online}")
        elif env.type == "typing":
            self.bus.typing_updated.emit(f"{env.sender_id} typing={env.payload.get('typing')}")
        elif env.type == "file_offer":
            self.bus.message_received.emit(
                f"{env.sender_id} offered file {env.payload.get('name')} ({env.payload.get('size')} bytes)"
            )
        elif env.type == "ack":
            if env.payload.get("joined_room"):
                room_id = env.payload.get("joined_room")
                self.bus.message_received.emit(f"[room] Joined room: {room_id}")
                self.status_label.setText(f"Joined room: {room_id}")
                self.conversations.add_conversation(f"room:{room_id}")
                self._save_conversations()
            elif env.payload.get("ok"):
                self.bus.message_received.emit("[connect] Connected to signaling server.")
                self._connected = True
                self._set_server_state("Connected")
                self.status_label.setText("Connected to signaling server")
                self._update_action_states()
            else:
                self.bus.message_received.emit(f"[ack] {env.payload}")
            known_users = env.payload.get("known_users")
            if isinstance(known_users, dict):
                for peer_id, name in known_users.items():
                    if peer_id != self.user_id:
                        self.conversations.add_conversation(f"direct:{peer_id}")
                        self.conversations.set_conversation_state(f"direct:{peer_id}", f"known:{name}")
                self._save_conversations()
            rooms = env.payload.get("rooms")
            if isinstance(rooms, list):
                for room_id in rooms:
                    self.conversations.add_conversation(f"room:{room_id}")
                self._save_conversations()
        elif env.type == "read_receipt":
            msg_id = env.payload.get("message_id", "")
            preview = self._pending_messages.get(msg_id, "(message)")
            self.bus.message_received.emit(f"[read] {env.sender_id} read: {preview}")
        elif env.type == "key_exchange":
            state = self.client.peer_trust.get(env.sender_id, "unknown")
            self.bus.message_received.emit(f"[trust] {env.sender_id}: {state}")
            self.trust_label.setText(f"Trust: {state}")
            self.conversations.set_conversation_state(f"direct:{env.sender_id}", state)
            if state == "new":
                self._set_friend_progress(env.sender_id, "key_received")
            elif state == "trusted":
                self._set_friend_progress(env.sender_id, "trusted")
            elif state == "key_changed":
                self._set_friend_progress(env.sender_id, "key_changed")

    async def _on_status_async(self, text: str) -> None:
        self.bus.status_changed.emit(text)
        if text.startswith("Connection error:"):
            self._connected = False
            self._last_error = text.replace("Connection error:", "").strip()
            self._set_server_state("Error")
            self._update_action_states()
        elif text == "Disconnected":
            self._connected = False
            self._set_server_state("Disconnected")
            self._update_action_states()
        elif text == "Connected":
            self._connected = True
            self._set_server_state("Connected")
            self._update_action_states()

    def _target(self) -> tuple[str, bool]:
        target = self.target_input.text().strip() or "lobby"
        is_room = self.mode_info.text().strip().lower().endswith("room")
        return target, is_room

    def _set_target(self, target: str, is_room: bool) -> None:
        self.target_input.setText(target)
        self.mode_info.setText(f"Mode: {'room' if is_room else 'direct'}")
        self.active_target = target
        self.active_is_room = is_room
        if is_room:
            self.trust_label.setText("Trust: n/a")
        else:
            self.trust_label.setText(f"Trust: {self.client.peer_trust.get(target, 'unknown')}")
        self._update_action_states()

    def add_room(self) -> None:
        room_id = self.new_room_input.text().strip()
        if not room_id:
            return
        self.conversations.add_conversation(f"room:{room_id}")
        self.new_room_input.clear()
        self._set_target(room_id, True)
        self.timeline.append(f"[room] Added room target: {room_id}")
        self._save_conversations()

    def add_direct(self) -> None:
        user_id = self.new_direct_input.text().strip()
        if not user_id:
            return
        self.conversations.add_conversation(f"direct:{user_id}")
        self.new_direct_input.clear()
        self._set_target(user_id, False)
        self.timeline.append(f"[friend] Added direct chat target: {user_id}")
        self._set_friend_progress(user_id, "added")
        self._save_conversations()
        self.send_key_exchange()

    def select_conversation(self) -> None:
        item = self.conversations.currentItem()
        if not item:
            return
        label = item.text().strip()
        if label.startswith("room:"):
            self._set_target(label[5:].split(" [", 1)[0], True)
        elif label.startswith("direct:"):
            self._set_target(label[7:].split(" [", 1)[0], False)

    def connect_client(self, auto_start_local: bool = False) -> None:
        self._reconnect_attempts += 1
        self._set_server_state("Connecting")
        self._update_server_diagnostics()
        self.status_label.setText("Connecting...")
        self.timeline.append(f"[connect] Connecting to {self.client.server_url} ...")
        future = asyncio.run_coroutine_threadsafe(self.client.connect(), self.client_loop)
        try:
            future.result(timeout=3)
        except Exception as exc:
            self.timeline.append(f"[error] connect failed: {exc}")
            self.status_label.setText("Connect failed")
            self._last_error = str(exc)
            self._connected = False
            self._set_server_state("Error")
            self._update_action_states()
            if auto_start_local and self._is_local_server_url(self.client.server_url):
                self.timeline.append("[server] Trying to start local server automatically...")
                self._start_local_server_process()
                QTimer.singleShot(1500, lambda: self.connect_client(auto_start_local=False))

    def join_room(self) -> None:
        target, is_room = self._target()
        if not is_room:
            QMessageBox.information(self, "Join Room", "Set mode to room before joining.")
            return
        self.conversations.add_conversation(f"room:{target}")
        self.timeline.append(f"[room] Join requested: {target}")
        asyncio.run_coroutine_threadsafe(self.client.join_room(target), self.client_loop)

    def on_typing(self, _text: str) -> None:
        target, is_room = self._target()
        asyncio.run_coroutine_threadsafe(self.client.send_typing(target, is_room, True), self.client_loop)

    def send_key_exchange(self) -> None:
        target, is_room = self._target()
        if is_room:
            QMessageBox.information(self, "Key Exchange", "Key exchange is for direct chats.")
            return
        if not self._connected:
            self.timeline.append("[error] Connect to a server before sending key exchange.")
            return
        asyncio.run_coroutine_threadsafe(self.client.send_key_exchange(target), self.client_loop)
        self.timeline.append(f"[trust] sent key to {target}")
        self.status_label.setText(f"Sent key exchange to {target}")
        self._set_friend_progress(target, "key_sent")

    def copy_my_id(self) -> None:
        QGuiApplication.clipboard().setText(self.my_id_label.text().replace("My ID: ", "", 1))
        self.status_label.setText("Copied your user ID to clipboard")

    def save_server_url(self) -> None:
        new_url = self.server_input.text().strip()
        if not (new_url.startswith("ws://") or new_url.startswith("wss://")):
            QMessageBox.warning(self, "Server URL", "Use ws:// or wss:// URL.")
            return
        self.server_url = new_url
        self.client.server_url = new_url
        settings = load_settings()
        settings["server_url"] = new_url
        save_settings(settings)
        self.server_url_label.setText(f"URL: {new_url}")
        self.timeline.append(f"[settings] server URL saved: {new_url}")

    def trust_key_change(self) -> None:
        target, is_room = self._target()
        if is_room:
            return
        asyncio.run_coroutine_threadsafe(self.client.trust_peer_new_key(target), self.client_loop)
        self.trust_label.setText(f"Trust: {self.client.peer_trust.get(target, 'trusted')}")
        self._set_friend_progress(target, "trusted")

    def send_message(self) -> None:
        text = self.message_input.text().strip()
        if not text:
            return
        if not self._connected:
            self.timeline.append("[error] Connect to a server before sending messages.")
            return
        target, is_room = self._target()
        self.conversations.add_conversation(f"{'room' if is_room else 'direct'}:{target}")
        future = asyncio.run_coroutine_threadsafe(self.client.send_chat(target, text, is_room), self.client_loop)
        try:
            message_id = future.result(timeout=3)
            self._pending_messages[message_id] = text[:80]
        except Exception as exc:
            self.timeline.append(f"[error] {exc}")
            return
        self.timeline.append(f"me: {text}")
        self.message_input.clear()

    def send_file(self) -> None:
        if not self._connected:
            self.timeline.append("[error] Connect to a server before sending files.")
            return
        file_name, _ = QFileDialog.getOpenFileName(self, "Pick file to send")
        if not file_name:
            return
        path = Path(file_name)
        try:
            validate_file(path)
        except Exception as exc:
            QMessageBox.warning(self, "File send error", str(exc))
            return
        target, is_room = self._target()
        transfer_id = build_transfer_id()
        size = path.stat().st_size
        asyncio.run_coroutine_threadsafe(
            self.client.send_file_offer(target, transfer_id, path.name, size, is_room),
            self.client_loop,
        )
        for index, chunk in iter_chunks_b64(path):
            asyncio.run_coroutine_threadsafe(
                self.client.send_file_chunk(target, transfer_id, chunk, is_room),
                self.client_loop,
            )
            self.status_label.setText(f"Sending {path.name} chunk {index + 1}")
        asyncio.run_coroutine_threadsafe(
            self.client.send_file_done(target, transfer_id, is_room),
            self.client_loop,
        )
        self.status_label.setText(f"Sent file: {path.name}")

    def _set_server_state(self, state: str) -> None:
        self._server_state = state
        self.server_state_label.setText(f"State: {state}")
        badge_color = {
            "Connected": "#2e7d32",
            "Connecting": "#f9a825",
            "Disconnected": "#546e7a",
            "Error": "#c62828",
        }.get(state, "#546e7a")
        self.server_state_badge.setText(state)
        self.server_state_badge.setStyleSheet(
            f"background-color: {badge_color}; color: white; border-radius: 8px; padding: 4px 8px;"
        )
        self._update_server_diagnostics()

    def _update_server_diagnostics(self) -> None:
        self.server_url_label.setText(f"URL: {self.client.server_url}")
        self.server_last_error_label.setText(f"Last Error: {self._last_error}")
        self.server_reconnect_label.setText(f"Reconnect Attempts: {self._reconnect_attempts}")
        self.server_peers_label.setText(f"Peers Online: {len(self._online_peers)}")

    def _set_friend_progress(self, user_id: str, state: str) -> None:
        self._friend_progress[user_id] = state
        display = self.client.known_users.get(user_id, "")
        state_text = f"{state} ({display})" if display else state
        self.conversations.set_conversation_state(f"direct:{user_id}", state_text)
        self.timeline.append(f"[friend] {user_id}: {state}")

    def _update_action_states(self) -> None:
        is_direct = not self.active_is_room
        self.send_btn.setEnabled(self._connected)
        self.file_btn.setEnabled(self._connected)
        self.join_btn.setEnabled(self._connected and self.active_is_room)
        self.key_exchange_btn.setEnabled(self._connected and is_direct)
        self.trust_key_btn.setEnabled(is_direct)

    def edit_profile(self) -> None:
        settings = load_settings()
        dialog = SetupDialog(
            settings.get("display_name", self.display_name),
            settings.get("user_id", self.user_id),
            settings.get("server_url", self.server_url),
            self,
        )
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        updated = dialog.result_settings()
        old_user = self.user_id
        settings.update(updated)
        save_settings(settings)
        self.display_name = updated["display_name"]
        self.user_id = updated["user_id"]
        self.client.display_name = self.display_name
        self.my_id_label.setText(f"My ID: {self.user_id}")
        self.display_name_label.setText(f"Display Name: {self.display_name}")
        self.setWindowTitle(f"Intel Byte 256 - {self.display_name} ({self.user_id})")
        self.server_input.setText(updated["server_url"])
        self.server_url = updated["server_url"]
        self.client.server_url = updated["server_url"]
        self.server_url_label.setText(f"URL: {updated['server_url']}")
        self.timeline.append("[profile] Profile updated.")
        if updated["user_id"] != old_user:
            QMessageBox.information(
                self,
                "Restart Required",
                "User ID changed. Restart Intel Byte 256 to use the new identity and keys.",
            )

    def _load_saved_conversations(self) -> None:
        settings = load_settings()
        for room_id in settings.get("rooms", []):
            self.conversations.add_conversation(f"room:{room_id}")
        for friend_id in settings.get("friends", []):
            self.conversations.add_conversation(f"direct:{friend_id}")

    def _save_conversations(self) -> None:
        rooms: list[str] = []
        friends: list[str] = []
        for idx in range(self.conversations.count()):
            label = self.conversations.item(idx).text().split(" [", 1)[0]
            if label.startswith("room:"):
                rooms.append(label[5:])
            elif label.startswith("direct:"):
                friends.append(label[7:])
        settings = load_settings()
        settings["rooms"] = sorted(set(rooms))
        settings["friends"] = sorted(set(friends))
        save_settings(settings)

    def _is_local_server_url(self, url: str) -> bool:
        try:
            host = (urlparse(url).hostname or "").lower()
        except Exception:
            return False
        return host in {"127.0.0.1", "localhost", "0.0.0.0", "::1"}

    def _start_local_server_process(self) -> None:
        try:
            project_root = Path(__file__).resolve().parents[2]
            launcher = project_root / "run_server.pyw"
            subprocess.Popen([sys.executable, str(launcher)], cwd=str(project_root))
            self.timeline.append("[server] Local server launcher started.")
        except Exception as exc:
            self.timeline.append(f"[server] Failed to auto-start local server: {exc}")

    def open_conversation_menu(self, position) -> None:
        item = self.conversations.itemAt(position)
        if not item:
            return
        raw_label = item.text().split(" [", 1)[0]
        menu = QMenu(self)
        copy_id = menu.addAction("Copy ID")
        remove_chat = menu.addAction("Remove Chat Entry")
        send_key = menu.addAction("Send Key Exchange")
        selected = menu.exec(self.conversations.mapToGlobal(position))
        if selected == copy_id:
            peer_id = raw_label.split(":", 1)[1] if ":" in raw_label else raw_label
            QGuiApplication.clipboard().setText(peer_id)
            self.status_label.setText("Copied ID")
        elif selected == remove_chat:
            row = self.conversations.row(item)
            self.conversations.takeItem(row)
            self.timeline.append(f"[ui] Removed chat: {raw_label}")
            self._save_conversations()
        elif selected == send_key and raw_label.startswith("direct:"):
            peer_id = raw_label.split(":", 1)[1]
            self._set_target(peer_id, False)
            self.send_key_exchange()

    def open_timeline_menu(self, position) -> None:
        menu = QMenu(self)
        copy_selected = menu.addAction("Copy Selected")
        copy_all = menu.addAction("Copy All")
        clear_log = menu.addAction("Clear Log")
        selected = menu.exec(self.timeline.mapToGlobal(position))
        if selected == copy_selected:
            self.timeline.copy()
        elif selected == copy_all:
            QGuiApplication.clipboard().setText(self.timeline.toPlainText())
            self.status_label.setText("Copied all log text")
        elif selected == clear_log:
            self.timeline.clear()
            self.timeline.append("[ui] Timeline cleared")

