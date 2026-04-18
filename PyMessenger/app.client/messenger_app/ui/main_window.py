"""PySide6 main window for the messenger desktop app."""

from __future__ import annotations

import asyncio
from collections import deque
from pathlib import Path
from threading import Thread

from PySide6.QtCore import QObject, Qt, QThread, Signal, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from messenger_app.net.client import MessengerClient
from messenger_app.net.file_transfer import build_transfer_id, iter_chunks_b64, validate_file
from messenger_app.net.protocol import Envelope
from messenger_app.storage.settings import load_settings, save_settings
from messenger_app.ui.activity_toast import ActivityToast
from messenger_app.ui.settings_dialog import SettingsDialog
from messenger_app.ui.setup_dialog import SetupDialog
from messenger_app.ui.widgets.chat_widgets import ConversationList


class UiBus(QObject):
    message_received = Signal(str)
    status_changed = Signal(str)
    presence_updated = Signal(str)
    typing_updated = Signal(str)
    header_refresh = Signal()
    diagnostics_changed = Signal()
    activity_logged = Signal(str)


class _ConnectWorker(QThread):
    """Runs asyncio future.result off the GUI thread so the UI can show a spinner."""

    finished_ok = Signal()
    failed = Signal(str)

    def __init__(self, future) -> None:
        super().__init__()
        self._future = future

    def run(self) -> None:
        try:
            self._future.result(timeout=45)
        except Exception as exc:
            self.failed.emit(str(exc))
        else:
            self.finished_ok.emit()


class MainWindow(QMainWindow):
    def __init__(self, server_url: str, user_id: str, display_name: str) -> None:
        super().__init__()
        self.server_url = server_url
        self.user_id = user_id
        self.display_name = display_name
        self.bus = UiBus()
        self.setWindowTitle(f"Intel Byte 256 - {display_name}")
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
        self._connect_worker: _ConnectWorker | None = None
        self._connect_spin_timer = QTimer(self)
        self._connect_spin_timer.timeout.connect(self._tick_connect_spinner)
        self._connect_spin_phase = 0
        self._trust_status_text = "Trust: n/a (room)"
        self._connect_line_mirror: QLabel | None = None
        self._activity_log_lines: deque[str] = deque(maxlen=4000)
        self._build_ui()
        self._connect_message_clear_timer = QTimer(self)
        self._connect_message_clear_timer.setSingleShot(True)
        self._connect_message_clear_timer.timeout.connect(self._clear_connect_line)
        self._wire_signals()
        self._start_client_thread()
        self._load_saved_conversations()
        self._update_server_diagnostics()
        self._update_action_states()
        self.push_toast(
            "Tip: Add your chat server address under ⚙ Settings, then use Connect. "
            "We’ll try to connect in a moment.",
            "hint",
        )
        QTimer.singleShot(400, self.connect_client)
        self._update_channel_header()
        self._update_message_placeholder()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---- Window chrome: status + connect + user settings (top right) ----
        title_row = QWidget()
        title_row.setObjectName("WindowTitleRow")
        tr = QHBoxLayout(title_row)
        tr.setContentsMargins(14, 10, 14, 10)
        app_title = QLabel("Intel Byte 256")
        app_title.setObjectName("WindowAppTitle")
        tr.addWidget(app_title)
        self.status_label = QLabel("Disconnected")
        self.status_label.setObjectName("WindowStatusLine")
        tr.addWidget(self.status_label)
        tr.addStretch()

        self.connect_detail_label = QLabel("")
        self.connect_detail_label.setObjectName("ConnectDetailLine")
        self.connect_detail_label.setWordWrap(False)
        self.connect_detail_label.setMaximumWidth(200)
        self.connect_detail_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        tr.addWidget(self.connect_detail_label)

        self.connect_spinner = QLabel("")
        self.connect_spinner.setObjectName("ConnectSpinner")
        self.connect_spinner.setFixedWidth(24)
        self.connect_spinner.hide()

        self.connect_btn = QPushButton("🔌 Connect")
        tr.addWidget(self.connect_spinner)
        tr.addWidget(self.connect_btn)
        root_layout.addWidget(title_row)

        outer = QWidget()
        outer_layout = QHBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # ---- Left: chat list + bottom user strip ----
        sidebar = QWidget()
        sidebar.setObjectName("DiscordSidebar")
        sidebar.setFixedWidth(260)
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(10, 14, 10, 12)
        sl.setSpacing(8)

        ch = QLabel("YOUR CHATS")
        ch.setObjectName("ChannelsSectionTitle")
        sl.addWidget(ch)

        quick = QGridLayout()
        self.quick_add_friend = QPushButton("➕ Add friend")
        self.quick_add_friend.setObjectName("SidebarQuickBtn")
        self.quick_new_room = QPushButton("📝 New room")
        self.quick_new_room.setObjectName("SidebarQuickBtn")
        self.quick_copy_invite = QPushButton("📨 Copy invite")
        self.quick_copy_invite.setObjectName("SidebarQuickBtn")
        quick.addWidget(self.quick_add_friend, 0, 0)
        quick.addWidget(self.quick_new_room, 0, 1)
        quick.addWidget(self.quick_copy_invite, 1, 0, 1, 2)
        sl.addLayout(quick)

        self.conv_search = QLineEdit()
        self.conv_search.setObjectName("SidebarSearch")
        self.conv_search.setPlaceholderText("Search chats…")
        sl.addWidget(self.conv_search)

        self.conversations = ConversationList()
        self.conversations.add_conversation("room:lobby")
        self.conversations.setCurrentRow(0)
        self.conversations.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        sl.addWidget(self.conversations, stretch=1)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setObjectName("SidebarDivider")
        sl.addWidget(div)

        self.user_footer_name = QLabel(self.display_name)
        self.user_footer_name.setObjectName("UserFooterName")
        sl.addWidget(self.user_footer_name)

        self.my_id_label = QLabel(f"My ID: {self.user_id}")
        self.my_id_label.setObjectName("UserFooterSub")
        self.my_id_label.setWordWrap(True)
        sl.addWidget(self.my_id_label)

        self.toast_host = QWidget()
        self.toast_host.setObjectName("ToastHost")
        self.toast_layout = QVBoxLayout(self.toast_host)
        self.toast_layout.setContentsMargins(0, 4, 0, 0)
        self.toast_layout.setSpacing(6)
        sl.addWidget(self.toast_host)

        foot_row = QHBoxLayout()
        self.copy_id_btn = QPushButton("📋 Copy ID")
        self.open_settings_btn = QPushButton("⚙ Settings")
        self.open_settings_btn.setObjectName("WindowSettingsBtn")
        foot_row.addWidget(self.copy_id_btn, stretch=1)
        foot_row.addWidget(self.open_settings_btn, stretch=1)
        sl.addLayout(foot_row)

        outer_layout.addWidget(sidebar)

        # ---- Center: channel bar + messages + composer ----
        center = QWidget()
        center.setObjectName("DiscordMain")
        cl = QVBoxLayout(center)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        top_bar = QWidget()
        top_bar.setObjectName("ChannelTopBar")
        tb = QHBoxLayout(top_bar)
        tb.setContentsMargins(16, 10, 16, 10)
        self.channel_header = QLabel("# lobby")
        self.channel_header.setObjectName("ChannelHeader")
        tb.addWidget(self.channel_header)
        tb.addStretch()
        self.mode_badge = QLabel("Room")
        self.mode_badge.setObjectName("ChannelModeBadge")
        tb.addWidget(self.mode_badge)
        cl.addWidget(top_bar)

        self.timeline = QTextEdit()
        self.timeline.setObjectName("MessageTimeline")
        self.timeline.setReadOnly(True)
        self.timeline.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.timeline.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.timeline.setPlaceholderText("No messages yet — say hello, or pick another chat on the left.")
        cl.addWidget(self.timeline, stretch=1)

        input_shell = QWidget()
        input_shell.setObjectName("MessageInputShell")
        isl = QVBoxLayout(input_shell)
        isl.setContentsMargins(16, 8, 16, 16)
        compose_row = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setObjectName("MessageInput")
        self.message_input.setPlaceholderText("Message #lobby")
        self.send_btn = QPushButton("➤ Send")
        self.file_btn = QPushButton("📎 Attach")
        compose_row.addWidget(self.message_input, stretch=1)
        compose_row.addWidget(self.send_btn)
        compose_row.addWidget(self.file_btn)
        isl.addLayout(compose_row)
        cl.addWidget(input_shell)

        outer_layout.addWidget(center, stretch=1)
        root_layout.addWidget(outer, stretch=1)

        self.setCentralWidget(root)

        self.send_btn.setToolTip("Send to this chat")
        self.file_btn.setToolTip("Send a file to this chat")
        self.connect_btn.setToolTip("Connect to your chat server")
        self.open_settings_btn.setToolTip("Account, server, friends, and help logs")

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #313338;
                color: #dbdee1;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 13px;
            }
            QWidget#DiscordSidebar { background-color: #2b2d31; color: #dbdee1; }
            QLineEdit#SidebarSearch {
                background-color: #1e1f22;
                border: 1px solid #1e1f22;
                border-radius: 4px;
                padding: 6px 8px;
                color: #dbdee1;
                selection-background-color: #4e5058;
                selection-color: #f2f3f5;
            }
            QLineEdit#SidebarSearch:focus { border-color: #3f4147; }
            QFrame#SidebarDivider {
                max-height: 1px;
                background-color: #3f4147;
                border: none;
            }
            QLabel#UserFooterName { color: #f2f3f5; font-weight: 600; font-size: 14px; }
            QLabel#UserFooterSub { color: #949ba4; font-size: 11px; }

            QWidget#DiscordMain { background-color: #313338; }
            QWidget#ChannelTopBar {
                background-color: #313338;
                border-bottom: 1px solid #26272b;
            }
            QLabel#ChannelHeader { color: #f2f3f5; font-size: 16px; font-weight: 600; }
            QLabel#ConnectSpinner { color: #b5bac1; font-size: 15px; }
            QWidget#WindowTitleRow {
                background-color: #2b2d31;
                border-bottom: 1px solid #1f2023;
            }
            QLabel#WindowAppTitle {
                color: #f2f3f5;
                font-size: 15px;
                font-weight: 700;
            }
            QLabel#WindowStatusLine {
                color: #949ba4;
                font-size: 13px;
                padding-left: 14px;
            }
            QLabel#ConnectDetailLine {
                color: #949ba4;
                font-size: 12px;
                padding-right: 8px;
            }
            QLabel#ChannelsSectionTitle {
                color: #949ba4;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.08em;
            }
            QPushButton#SidebarQuickBtn {
                padding: 8px 6px;
                font-size: 12px;
                background-color: #3c3f45;
                border: 1px solid #4e5058;
            }
            QPushButton#SidebarQuickBtn:hover {
                background-color: #4e5058;
                border-color: #6d6f78;
            }
            QLabel#ChannelModeBadge {
                color: #949ba4;
                font-size: 12px;
                font-weight: 600;
                padding: 4px 12px;
                background-color: #2b2d31;
                border-radius: 12px;
            }

            QTextEdit#MessageTimeline {
                background-color: #313338;
                color: #dbdee1;
                border: none;
                padding: 12px 18px;
                font-size: 14px;
                selection-background-color: #4e5058;
                selection-color: #f2f3f5;
            }
            QWidget#MessageInputShell { background-color: #313338; }
            QLineEdit#MessageInput {
                background-color: #383a40;
                border: 1px solid #383a40;
                border-radius: 8px;
                padding: 10px 14px;
                color: #f2f3f5;
                font-size: 15px;
                selection-background-color: #4e5058;
                selection-color: #f2f3f5;
            }
            QLineEdit#MessageInput:focus { border-color: #949ba4; }

            QListWidget#ConversationList {
                background-color: #2b2d31;
                color: #dbdee1;
                border: none;
                outline: none;
                padding: 4px 0;
                font-size: 14px;
            }
            QListWidget#ConversationList::item {
                padding: 8px 10px;
                border-radius: 4px;
                margin: 1px 6px;
            }
            QListWidget#ConversationList::item:hover { background-color: #35373c; }
            QListWidget#ConversationList::item:selected {
                background-color: #3f4248;
                color: #f2f3f5;
            }

            QLineEdit {
                background-color: #1e1f22;
                border: 1px solid #1e1f22;
                border-radius: 4px;
                padding: 6px 8px;
                color: #dbdee1;
                selection-background-color: #4e5058;
                selection-color: #f2f3f5;
            }
            QLineEdit:focus { border-color: #3f4147; }

            QPushButton {
                background-color: #4e5058;
                color: #f2f3f5;
                border: 1px solid #6d6f78;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5c5f6a;
                border-color: #787c87;
            }
            QPushButton:pressed {
                background-color: #3c3f45;
                border-color: #3c3f45;
            }
            QPushButton:disabled {
                background-color: #3c3f45;
                color: #5e6268;
                border-color: #3c3f45;
            }

            QScrollArea { background: transparent; border: none; }
            QMenu {
                background-color: #111214;
                color: #dbdee1;
                border: 1px solid #2b2d31;
                padding: 4px;
            }
            QMenu::item { padding: 8px 20px; border-radius: 2px; }
            QMenu::item:selected { background-color: #3f4248; }

            QWidget#ToastHost { background-color: transparent; }
            QFrame#ActivityToast {
                background-color: #1e1f22;
                border: 1px solid #3f4147;
                border-radius: 6px;
            }
            QLabel#ToastIcon { font-size: 14px; padding-top: 2px; }
            QLabel#ToastText { color: #dbdee1; font-size: 12px; }
            QPushButton#ToastClose {
                background-color: transparent;
                border: none;
                color: #949ba4;
                font-weight: 700;
                padding: 0;
            }
            QPushButton#ToastClose:hover { color: #f2f3f5; }
            """
        )

    def _log_activity(self, line: str) -> None:
        text = line.rstrip()
        if not text:
            return
        self._activity_log_lines.append(text)
        self.bus.activity_logged.emit(text)

    def get_activity_log_text(self) -> str:
        return "\n".join(self._activity_log_lines)

    def push_toast(self, message: str, kind: str = "default") -> None:
        self._log_activity(message)
        while self.toast_layout.count() >= 5:
            it = self.toast_layout.takeAt(0)
            w = it.widget()
            if w is not None:
                w.deleteLater()
        toast = ActivityToast(message, kind, self.toast_host)
        self.toast_layout.addWidget(toast)

    def register_connect_line_mirror(self, label: QLabel | None) -> None:
        """Settings dialog can mirror the grey connect hint while open."""
        self._connect_line_mirror = label
        if label is not None:
            label.setText(self.connect_detail_label.text())

    def _set_connect_line(self, text: str, clear_ms: int = 0) -> None:
        self._connect_message_clear_timer.stop()
        self.connect_detail_label.setText(text)
        if self._connect_line_mirror is not None:
            self._connect_line_mirror.setText(text)
        if clear_ms > 0:
            self._connect_message_clear_timer.start(clear_ms)

    def _clear_connect_line(self) -> None:
        self.connect_detail_label.clear()
        if self._connect_line_mirror is not None:
            self._connect_line_mirror.clear()

    def _on_bus_message(self, line: str) -> None:
        s = line.strip()
        self._log_activity(s)
        if s.startswith("[connect]") and "]" in s:
            detail = s[s.index("]") + 1 :].strip() or s
            if "connected" in detail.lower():
                self._set_connect_line("Connected", 8000)
            else:
                self._set_connect_line("Connecting…", 0)
            return
        if s.startswith("[error]") and "connect" in s.lower():
            self._set_connect_line("Connection failed", 0)
            return
        if s.startswith("[") and "]" in s[:36]:
            tag = s[1 : s.index("]")].lower()
            self._toast_only(s, tag)
            return
        self.timeline.append(s)

    def _toast_only(self, message: str, kind: str = "default") -> None:
        while self.toast_layout.count() >= 5:
            it = self.toast_layout.takeAt(0)
            w = it.widget()
            if w is not None:
                w.deleteLater()
        toast = ActivityToast(message, kind, self.toast_host)
        self.toast_layout.addWidget(toast)

    def _wire_signals(self) -> None:
        self.send_btn.clicked.connect(self.send_message)
        self.file_btn.clicked.connect(self.send_file)
        self.connect_btn.clicked.connect(self.connect_client)
        self.open_settings_btn.clicked.connect(self._open_settings_dialog)
        self.quick_add_friend.clicked.connect(self._quick_add_friend)
        self.quick_new_room.clicked.connect(self._quick_new_room)
        self.quick_copy_invite.clicked.connect(self.copy_invite_to_clipboard)
        self.copy_id_btn.clicked.connect(self.copy_my_id)
        self.conversations.itemSelectionChanged.connect(self.select_conversation)
        self.conversations.customContextMenuRequested.connect(self.open_conversation_menu)
        self.timeline.customContextMenuRequested.connect(self.open_timeline_menu)
        self.message_input.textEdited.connect(self.on_typing)
        self.bus.message_received.connect(self._on_bus_message)
        self.bus.status_changed.connect(self._on_connection_status_text)
        self.bus.presence_updated.connect(lambda x: self._log_activity(f"[presence] {x}"))
        self.bus.typing_updated.connect(lambda x: self._log_activity(f"[typing] {x}"))
        self.bus.header_refresh.connect(self._update_channel_header)
        self.conv_search.textChanged.connect(self._filter_conversations)

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
                f"[file] {env.sender_id} offered {env.payload.get('name')} ({env.payload.get('size')} bytes)"
            )
        elif env.type == "ack":
            if env.payload.get("joined_room"):
                room_id = env.payload.get("joined_room")
                self.bus.message_received.emit(f"[room] Joined room: {room_id}")
                self.status_label.setText(f"Joined room: {room_id}")
                self.conversations.add_conversation(f"room:{room_id}")
                self._save_conversations()
            elif env.payload.get("ok"):
                self.bus.message_received.emit("[connect] Connected to Intel Byte server.")
                self._connected = True
                self._set_server_state("Connected")
                self.status_label.setText("Connected to Intel Byte server")
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
            self.bus.header_refresh.emit()
        elif env.type == "read_receipt":
            msg_id = env.payload.get("message_id", "")
            preview = self._pending_messages.get(msg_id, "(message)")
            self.bus.message_received.emit(f"[read] {env.sender_id} read: {preview}")
        elif env.type == "key_exchange":
            state = self.client.peer_trust.get(env.sender_id, "unknown")
            self.bus.message_received.emit(f"[trust] {env.sender_id}: {state}")
            self._set_trust_status(f"Trust: {state}")
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
        target = (self.active_target or "lobby").strip() or "lobby"
        return target, self.active_is_room

    def _set_target(self, target: str, is_room: bool) -> None:
        self.active_target = target.strip() or "lobby"
        self.active_is_room = is_room
        if is_room:
            self._set_trust_status("Trust: n/a (room)")
        else:
            self._set_trust_status(f"Trust: {self.client.peer_trust.get(self.active_target, 'unknown')}")
        self.mode_badge.setText("Room" if is_room else "Direct message")
        self._update_channel_header()
        self._update_message_placeholder()
        self._update_action_states()

    def _set_trust_status(self, text: str) -> None:
        self._trust_status_text = text
        self.bus.diagnostics_changed.emit()

    def _open_settings_dialog(self) -> None:
        dlg = SettingsDialog(self, self)
        dlg.exec()

    def _quick_add_friend(self) -> None:
        uid, ok = QInputDialog.getText(self, "Add friend", "Your friend’s user ID:")
        if ok and uid.strip():
            self.add_direct(uid.strip())

    def _quick_new_room(self) -> None:
        rid, ok = QInputDialog.getText(self, "New room", "Room name or ID:")
        if ok and rid.strip():
            self.add_room(rid.strip())

    def _update_channel_header(self) -> None:
        if self.active_is_room:
            self.channel_header.setText(f"# {self.active_target}")
        else:
            disp = self.client.known_users.get(self.active_target, "")
            extra = f" — {disp}" if disp else ""
            self.channel_header.setText(f"@ {self.active_target}{extra}")

    def _update_message_placeholder(self) -> None:
        if self.active_is_room:
            self.message_input.setPlaceholderText(f"Message #{self.active_target}")
        else:
            self.message_input.setPlaceholderText(f"Message @{self.active_target}")

    def _filter_conversations(self, text: str) -> None:
        q = text.casefold().strip()
        for i in range(self.conversations.count()):
            item = self.conversations.item(i)
            item.setHidden(bool(q) and q not in item.text().casefold())

    def add_room(self, room_id: str) -> None:
        room_id = room_id.strip()
        if not room_id:
            return
        self.conversations.add_conversation(f"room:{room_id}")
        self._set_target(room_id, True)
        self.push_toast(f"[room] Added room target: {room_id}", "room")
        self._save_conversations()

    def add_direct(self, user_id: str) -> None:
        user_id = user_id.strip()
        if not user_id:
            return
        self.conversations.add_conversation(f"direct:{user_id}")
        self._set_target(user_id, False)
        self.push_toast(f"[friend] Added direct chat target: {user_id}", "friend")
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

    def _tick_connect_spinner(self) -> None:
        frames = ("◐", "◓", "◑", "◒")
        self._connect_spin_phase = (self._connect_spin_phase + 1) % len(frames)
        self.connect_spinner.setText(frames[self._connect_spin_phase])

    def _begin_connect_busy(self) -> None:
        self.connect_btn.setEnabled(False)
        self.connect_spinner.show()
        self._connect_spin_phase = 0
        self.connect_spinner.setText("◐")
        self._connect_spin_timer.start(140)

    def _end_connect_busy(self) -> None:
        self._connect_spin_timer.stop()
        self.connect_spinner.hide()
        self.connect_spinner.clear()
        self.connect_btn.setEnabled(True)
        self._update_action_states()

    def _log_connect_failure_block(self, detail: str) -> None:
        block = (
            "[error] Cannot reach Intel Byte server\n"
            f"Details: {detail}\n"
            "We couldn’t open a WebSocket to the address in Settings.\n"
            "Things to check:\n"
            "• The chat server is running and listening on the port you expect\n"
            "• If you’re on the internet, your router forwards that port to the machine running the server\n"
            "• The address uses ws:// or wss:// (use wss:// when TLS is enabled)\n"
            "• Firewalls allow that port through\n"
            f"Address tried: {self.client.server_url}\n"
        )
        self._log_activity(block.rstrip())

    def _on_connection_status_text(self, text: str) -> None:
        self._log_activity(f"[status] {text}")
        self.status_label.setText(text)

    def _on_connect_worker_finished_ok(self) -> None:
        self._end_connect_busy()
        self._log_activity("[connect] Socket ready; finishing handshake with Intel Byte server…")
        self._set_connect_line("Securing session…", 7000)

    def _on_connect_worker_failed(self, msg: str) -> None:
        self._end_connect_busy()
        self._set_connect_line("Connection failed", 0)
        self.status_label.setText("Connect failed")
        self._last_error = msg
        self._connected = False
        self._set_server_state("Error")
        self._update_server_diagnostics()
        self._update_action_states()
        self._log_connect_failure_block(msg)

    def _cleanup_connect_worker(self) -> None:
        self._connect_worker = None

    def connect_client(self) -> None:
        if self._connect_worker is not None and self._connect_worker.isRunning():
            return
        url = (self.client.server_url or "").strip()
        if not url.startswith("ws://") and not url.startswith("wss://"):
            self.push_toast(
                "[hint] Add a server address that starts with ws:// or wss:// in Settings, then try Connect again.",
                "hint",
            )
            self.status_label.setText("No server URL")
            return
        self._reconnect_attempts += 1
        self._set_server_state("Connecting")
        self._update_server_diagnostics()
        self.status_label.setText("Connecting…")
        self._log_activity(f"[connect] Connecting to Intel Byte server at {self.client.server_url}")
        self._set_connect_line("Connecting…", 0)
        self._begin_connect_busy()
        future = asyncio.run_coroutine_threadsafe(self.client.connect(), self.client_loop)
        self._connect_worker = _ConnectWorker(future)
        self._connect_worker.finished_ok.connect(self._on_connect_worker_finished_ok)
        self._connect_worker.failed.connect(self._on_connect_worker_failed)
        self._connect_worker.finished.connect(self._cleanup_connect_worker)
        self._connect_worker.start()

    def join_room(self) -> None:
        target, is_room = self._target()
        if not is_room:
            self.push_toast("[hint] Switch to a room chat first, then use Join room.", "hint")
            return
        self.conversations.add_conversation(f"room:{target}")
        self.push_toast(f"[room] Join requested: {target}", "room")
        asyncio.run_coroutine_threadsafe(self.client.join_room(target), self.client_loop)

    def on_typing(self, _text: str) -> None:
        target, is_room = self._target()
        asyncio.run_coroutine_threadsafe(self.client.send_typing(target, is_room, True), self.client_loop)

    def send_key_exchange(self) -> None:
        target, is_room = self._target()
        if is_room:
            self.push_toast("[hint] Key exchange is only for one-to-one chats, not rooms.", "hint")
            return
        if not self._connected:
            self.push_toast("[error] Connect to a server before sending key exchange.", "error")
            return
        asyncio.run_coroutine_threadsafe(self.client.send_key_exchange(target), self.client_loop)
        self.push_toast(f"[trust] sent key to {target}", "trust")
        self.status_label.setText(f"Sent key exchange to {target}")
        self._set_friend_progress(target, "key_sent")

    def copy_my_id(self) -> None:
        QGuiApplication.clipboard().setText(self.user_id)
        self.status_label.setText("Copied your user ID to clipboard")
        self.push_toast("[hint] Copied your user ID to the clipboard.", "hint")

    def copy_invite_to_clipboard(self) -> None:
        block = (
            "Intel Byte 256 chat invite\n"
            f"Server: {self.client.server_url}\n"
            f"User ID: {self.user_id}\n"
            f"Display: {self.display_name}\n"
        )
        QGuiApplication.clipboard().setText(block)
        self.status_label.setText("Copied invite to clipboard")
        self.push_toast("[hint] Copied invite block (server + your id) to clipboard.", "hint")

    def apply_server_url(self, new_url: str) -> bool:
        new_url = new_url.strip()
        if not (new_url.startswith("ws://") or new_url.startswith("wss://")):
            self.push_toast("[error] Server address must start with ws:// or wss://.", "error")
            return False
        if new_url == self.client.server_url:
            self._update_server_diagnostics()
            return True
        self.server_url = new_url
        self.client.server_url = new_url
        settings = load_settings()
        settings["server_url"] = new_url
        save_settings(settings)
        self.push_toast(f"[settings] Server URL saved: {new_url}", "settings")
        self._update_server_diagnostics()
        return True

    def trust_key_change(self) -> None:
        target, is_room = self._target()
        if is_room:
            return
        asyncio.run_coroutine_threadsafe(self.client.trust_peer_new_key(target), self.client_loop)
        self._set_trust_status(f"Trust: {self.client.peer_trust.get(target, 'trusted')}")
        self._set_friend_progress(target, "trusted")

    def send_message(self) -> None:
        text = self.message_input.text().strip()
        if not text:
            return
        if not self._connected:
            self.push_toast("[error] Connect to a server before sending messages.", "error")
            return
        target, is_room = self._target()
        self.conversations.add_conversation(f"{'room' if is_room else 'direct'}:{target}")
        future = asyncio.run_coroutine_threadsafe(self.client.send_chat(target, text, is_room), self.client_loop)
        try:
            message_id = future.result(timeout=3)
            self._pending_messages[message_id] = text[:80]
        except Exception as exc:
            self.push_toast(f"[error] {exc}", "error")
            return
        self.timeline.append(f"me: {text}")
        self.message_input.clear()

    def send_file(self) -> None:
        if not self._connected:
            self.push_toast("[error] Connect to a server before sending files.", "error")
            return
        file_name, _ = QFileDialog.getOpenFileName(self, "Pick file to send")
        if not file_name:
            return
        path = Path(file_name)
        try:
            validate_file(path)
        except Exception as exc:
            self.push_toast(f"[error] Can’t send this file: {exc}", "error")
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
        self._update_server_diagnostics()

    def _update_server_diagnostics(self) -> None:
        self.bus.diagnostics_changed.emit()

    def _set_friend_progress(self, user_id: str, state: str) -> None:
        self._friend_progress[user_id] = state
        display = self.client.known_users.get(user_id, "")
        state_text = f"{state} ({display})" if display else state
        self.conversations.set_conversation_state(f"direct:{user_id}", state_text)
        self.push_toast(f"[friend] {user_id}: {state}", "friend")

    def _update_action_states(self) -> None:
        self.send_btn.setEnabled(self._connected)
        self.file_btn.setEnabled(self._connected)

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
        self.user_footer_name.setText(self.display_name)
        self.my_id_label.setText(f"My ID: {self.user_id}")
        self.setWindowTitle(f"Intel Byte 256 - {self.display_name}")
        self.apply_server_url(updated["server_url"])
        self.push_toast("[settings] Profile updated.", "settings")
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
            self.push_toast(f"[ui] Removed chat: {raw_label}", "ui")
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
            self.push_toast("[ui] Message history cleared.", "ui")

