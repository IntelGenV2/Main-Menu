"""PySide6 main window for the messenger desktop app."""

from __future__ import annotations

import asyncio
from pathlib import Path
from threading import Thread

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
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
            history_path=Path(".messenger/history.sqlite"),
            history_secret=f"{user_id}-local-history",
        )
        self.client.on_message = self._on_message_async
        self.client.on_status = self._on_status_async

        self.active_target = "lobby"
        self.active_is_room = True
        self._pending_messages: dict[str, str] = {}
        self._build_ui()
        self._wire_signals()
        self._start_client_thread()

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
        splitter.addWidget(self.conversations)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        self.timeline = QTextEdit()
        self.timeline.setReadOnly(True)
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
        right_layout.addWidget(QLabel("Details / Settings"))
        self.my_id_label = QLabel(f"My ID: {self.user_id}")
        self.copy_id_btn = QPushButton("Copy My ID")
        right_layout.addWidget(self.my_id_label)
        right_layout.addWidget(self.copy_id_btn)
        right_layout.addWidget(QLabel(f"Display Name: {self.display_name}"))
        self.target_input = QLineEdit("lobby")
        self.target_input.setReadOnly(True)
        self.mode_info = QLabel("Mode: room")
        self.new_room_input = QLineEdit()
        self.new_room_input.setPlaceholderText("new room id")
        self.new_direct_input = QLineEdit()
        self.new_direct_input.setPlaceholderText("direct user id")
        self.server_input = QLineEdit(self.server_url)
        self.save_server_btn = QPushButton("Save Server URL")
        self.trust_label = QLabel("Trust: n/a")
        self.connect_btn = QPushButton("Connect")
        self.join_btn = QPushButton("Join Room")
        self.add_room_btn = QPushButton("Add Room")
        self.add_direct_btn = QPushButton("Add Direct")
        self.key_exchange_btn = QPushButton("Send Key")
        self.trust_key_btn = QPushButton("Trust Key Change")
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
        self.add_room_btn.clicked.connect(self.add_room)
        self.add_direct_btn.clicked.connect(self.add_direct)
        self.copy_id_btn.clicked.connect(self.copy_my_id)
        self.save_server_btn.clicked.connect(self.save_server_url)
        self.key_exchange_btn.clicked.connect(self.send_key_exchange)
        self.trust_key_btn.clicked.connect(self.trust_key_change)
        self.conversations.itemSelectionChanged.connect(self.select_conversation)
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
        elif env.type == "presence":
            self.bus.presence_updated.emit(f"{env.sender_id} -> {env.payload.get('online')}")
        elif env.type == "typing":
            self.bus.typing_updated.emit(f"{env.sender_id} typing={env.payload.get('typing')}")
        elif env.type == "file_offer":
            self.bus.message_received.emit(
                f"{env.sender_id} offered file {env.payload.get('name')} ({env.payload.get('size')} bytes)"
            )
        elif env.type == "ack":
            self.bus.message_received.emit(f"ACK: {env.payload}")
        elif env.type == "read_receipt":
            msg_id = env.payload.get("message_id", "")
            preview = self._pending_messages.get(msg_id, "(message)")
            self.bus.message_received.emit(f"[read] {env.sender_id} read: {preview}")
        elif env.type == "key_exchange":
            state = self.client.peer_trust.get(env.sender_id, "unknown")
            self.bus.message_received.emit(f"[trust] {env.sender_id}: {state}")
            self.trust_label.setText(f"Trust: {state}")
            self.conversations.set_conversation_state(f"direct:{env.sender_id}", state)

    async def _on_status_async(self, text: str) -> None:
        self.bus.status_changed.emit(text)

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

    def add_room(self) -> None:
        room_id = self.new_room_input.text().strip()
        if not room_id:
            return
        self.conversations.add_conversation(f"room:{room_id}")
        self.new_room_input.clear()
        self._set_target(room_id, True)

    def add_direct(self) -> None:
        user_id = self.new_direct_input.text().strip()
        if not user_id:
            return
        self.conversations.add_conversation(f"direct:{user_id}")
        self.new_direct_input.clear()
        self._set_target(user_id, False)
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

    def connect_client(self) -> None:
        future = asyncio.run_coroutine_threadsafe(self.client.connect(), self.client_loop)
        try:
            future.result(timeout=3)
        except Exception as exc:
            self.timeline.append(f"[error] connect failed: {exc}")

    def join_room(self) -> None:
        target, is_room = self._target()
        if not is_room:
            QMessageBox.information(self, "Join Room", "Set mode to room before joining.")
            return
        self.conversations.add_conversation(f"room:{target}")
        asyncio.run_coroutine_threadsafe(self.client.join_room(target), self.client_loop)

    def on_typing(self, _text: str) -> None:
        target, is_room = self._target()
        asyncio.run_coroutine_threadsafe(self.client.send_typing(target, is_room, True), self.client_loop)

    def send_key_exchange(self) -> None:
        target, is_room = self._target()
        if is_room:
            QMessageBox.information(self, "Key Exchange", "Key exchange is for direct chats.")
            return
        asyncio.run_coroutine_threadsafe(self.client.send_key_exchange(target), self.client_loop)
        self.timeline.append(f"[trust] sent key to {target}")

    def copy_my_id(self) -> None:
        QGuiApplication.clipboard().setText(self.user_id)
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
        self.timeline.append(f"[settings] server URL saved: {new_url}")

    def trust_key_change(self) -> None:
        target, is_room = self._target()
        if is_room:
            return
        asyncio.run_coroutine_threadsafe(self.client.trust_peer_new_key(target), self.client_loop)
        self.trust_label.setText(f"Trust: {self.client.peer_trust.get(target, 'trusted')}")

    def send_message(self) -> None:
        text = self.message_input.text().strip()
        if not text:
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

