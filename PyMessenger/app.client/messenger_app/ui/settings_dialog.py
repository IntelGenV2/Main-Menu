"""Settings window (Discord-style) for Intel Byte 256."""

from __future__ import annotations

import re
from typing import Any, Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication, QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

def _parse_invite_block(text: str) -> tuple[str | None, str | None]:
    server: str | None = None
    user_id: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        low = line.lower()
        if low.startswith("server:"):
            server = line.split(":", 1)[1].strip()
        elif low.startswith("user id:") or low.startswith("userid:"):
            user_id = line.split(":", 1)[1].strip()
    m = re.search(r"ws[s]?://[^\s]+", text)
    if server is None and m:
        server = m.group(0).strip()
    return server, user_id


class SettingsDialog(QDialog):
    """Modal settings matching the legacy tabbed layout (My account, server, friends, voice, logs)."""

    def __init__(self, main: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent or main)
        self._main = main
        self.setWindowTitle("Settings — Intel Byte 256")
        self.setMinimumSize(920, 640)
        self.resize(980, 700)
        self.setModal(True)

        root = QVBoxLayout(self)
        center = QWidget()
        center_layout = QHBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        self._nav = QListWidget()
        self._nav.setObjectName("SettingsNavList")
        self._nav.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._nav.setFixedWidth(220)
        for label in (
            "👤  My account",
            "🖧  Intel Byte server",
            "👥  Friends & channels",
            "🎤  Voice & video",
            "📋  Activity logs",
        ):
            self._nav.addItem(QListWidgetItem(label))
        self._nav.setCurrentRow(0)
        self._nav.currentRowChanged.connect(self._on_nav_changed)
        center_layout.addWidget(self._nav)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_account_tab())
        self._stack.addWidget(self._build_server_tab())
        self._stack.addWidget(self._build_friends_tab())
        self._stack.addWidget(self._build_voice_tab())
        self._stack.addWidget(self._build_logs_tab())
        center_layout.addWidget(self._stack, stretch=1)
        root.addWidget(center, stretch=1)

        bottom = QHBoxLayout()
        bottom.addStretch(1)
        close_btn = QPushButton("✕  Close")
        close_btn.clicked.connect(self.accept)
        bottom.addWidget(close_btn)
        root.addLayout(bottom)

        self._apply_stylesheet()
        self._refresh_diagnostics()
        self._refresh_account_labels()

        self._diag_timer = QTimer(self)
        self._diag_timer.timeout.connect(self._refresh_diagnostics)
        self._diag_timer.start(600)
        self._main.bus.diagnostics_changed.connect(self._refresh_diagnostics)
        self.finished.connect(self._on_dialog_finished)

        self._log_conn: Callable[[str], None] | None = None
        self._attach_activity_log()
        self._main.register_connect_line_mirror(self._server_connect_detail)

    def _on_nav_changed(self, index: int) -> None:
        if 0 <= index < self._stack.count():
            self._stack.setCurrentIndex(index)

    def _on_dialog_finished(self, _result: int) -> None:
        self._diag_timer.stop()
        try:
            self._main.bus.diagnostics_changed.disconnect(self._refresh_diagnostics)
        except Exception:
            pass
        self._detach_activity_log()
        self._main.register_connect_line_mirror(None)

    def _apply_stylesheet(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
                background-color: #313338;
                color: #dbdee1;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 13px;
            }
            QListWidget#SettingsNavList {
                background-color: #2b2d31;
                color: #dbdee1;
                border: none;
                border-right: 1px solid #1f2023;
                outline: none;
                padding: 8px 0;
            }
            QListWidget#SettingsNavList::item {
                padding: 12px 14px;
                margin: 2px 8px;
                border-radius: 6px;
            }
            QListWidget#SettingsNavList::item:selected {
                background-color: #3f4248;
                color: #f2f3f5;
                font-weight: 600;
            }
            QListWidget#SettingsNavList::item:hover:!selected {
                background-color: #35373c;
            }
            QLabel#ConnectDetailLine {
                color: #949ba4;
                font-size: 12px;
            }
            QLabel#SettingsHeading { color: #f2f3f5; font-size: 18px; font-weight: 700; }
            QLabel#SettingsSub { color: #949ba4; font-size: 12px; }
            QLabel#SettingsMuted { color: #949ba4; font-size: 11px; }
            QLineEdit, QTextEdit, QPlainTextEdit {
                background-color: #1e1f22;
                border: 1px solid #1e1f22;
                border-radius: 4px;
                padding: 8px 10px;
                color: #dbdee1;
                selection-background-color: #4e5058;
                selection-color: #f2f3f5;
            }
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus { border-color: #3f4147; }
            QPlainTextEdit#ActivityLogSettings {
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 12px;
                line-height: 1.35;
            }
            QGroupBox {
                margin-top: 12px;
                font-weight: 600;
                color: #b5bac1;
                border: 1px solid #3f4147;
                border-radius: 6px;
                padding: 12px 10px 10px 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QPushButton {
                background-color: #4e5058;
                color: #f2f3f5;
                border: 1px solid #6d6f78;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5c5f6a;
                border-color: #787c87;
            }
            QPushButton:pressed { background-color: #3c3f45; }
            """
        )

    def _build_account_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        h = QLabel("My account")
        h.setObjectName("SettingsHeading")
        lay.addWidget(h)
        sub = QLabel("Profile, identity, and quick share for friends.")
        sub.setObjectName("SettingsSub")
        sub.setWordWrap(True)
        lay.addWidget(sub)

        self._acc_name = QLabel()
        self._acc_name.setWordWrap(True)
        self._acc_id = QLabel()
        self._acc_id.setWordWrap(True)
        lay.addWidget(self._acc_name)
        lay.addWidget(self._acc_id)

        row = QHBoxLayout()
        copy_uid = QPushButton("📋  Copy user ID")
        copy_uid.clicked.connect(self._copy_user_id)
        copy_inv = QPushButton("📨  Copy invite")
        copy_inv.clicked.connect(lambda: self._main.copy_invite_to_clipboard())
        row.addWidget(copy_uid)
        row.addWidget(copy_inv)
        lay.addLayout(row)

        edit = QPushButton("✏️  Edit profile…")
        edit.clicked.connect(self._edit_profile_from_settings)
        lay.addWidget(edit)
        lay.addStretch(1)
        return w

    def _build_server_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        h = QLabel("Intel Byte server")
        h.setObjectName("SettingsHeading")
        lay.addWidget(h)

        note = QLabel(
            "Enter the WebSocket address your server gives you (often looks like ws://… or wss://…). "
            "Use wss:// when your server uses TLS."
        )
        note.setObjectName("SettingsMuted")
        note.setWordWrap(True)
        lay.addWidget(note)

        form = QFormLayout()
        self._server_url_edit = QLineEdit(self._main.client.server_url)
        form.addRow("Server address", self._server_url_edit)
        lay.addLayout(form)

        save = QPushButton("💾  Save URL")
        save.clicked.connect(self._save_server_from_dialog)
        lay.addWidget(save)

        connect_row = QHBoxLayout()
        self._server_connect_detail = QLabel("")
        self._server_connect_detail.setObjectName("ConnectDetailLine")
        self._server_connect_detail.setWordWrap(True)
        self._server_connect_detail.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        connect = QPushButton("🔌  Connect / reconnect")
        connect.clicked.connect(lambda: self._main.connect_client())
        connect_row.addWidget(self._server_connect_detail, stretch=1)
        connect_row.addWidget(connect)
        lay.addLayout(connect_row)

        foot = QLabel(
            "This app only connects to the address you enter — it does not start a server for you. "
            "Run your chat server separately on the machine you control."
        )
        foot.setObjectName("SettingsMuted")
        foot.setWordWrap(True)
        lay.addWidget(foot)

        diag = QGroupBox("Diagnostics")
        dlay = QVBoxLayout(diag)
        self._diag_state = QLabel()
        self._diag_badge = QLabel()
        self._diag_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._diag_url = QLabel()
        self._diag_url.setWordWrap(True)
        self._diag_err = QLabel()
        self._diag_err.setWordWrap(True)
        self._diag_attempts = QLabel()
        self._diag_peers = QLabel()
        self._diag_trust = QLabel()
        self._diag_trust.setWordWrap(True)
        for lab in (
            self._diag_state,
            self._diag_badge,
            self._diag_url,
            self._diag_err,
            self._diag_attempts,
            self._diag_peers,
            self._diag_trust,
        ):
            dlay.addWidget(lab)
        lay.addWidget(diag)
        lay.addStretch(1)
        return w

    def _build_friends_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        h = QLabel("Friends & chats")
        h.setObjectName("SettingsHeading")
        lay.addWidget(h)
        sub = QLabel("Find chats you already have, add someone by ID, or paste an invite someone sent you.")
        sub.setObjectName("SettingsSub")
        sub.setWordWrap(True)
        lay.addWidget(sub)

        self._friend_search = QLineEdit()
        self._friend_search.setPlaceholderText("Search by user id or display name…")
        self._friend_search.textChanged.connect(self._on_friend_search)
        lay.addWidget(self._friend_search)

        self._friend_results = QTextEdit()
        self._friend_results.setReadOnly(True)
        self._friend_results.setPlaceholderText("Matching chats show up here.")
        self._friend_results.setMaximumHeight(120)
        lay.addWidget(self._friend_results)

        row = QHBoxLayout()
        self._friend_id_edit = QLineEdit()
        self._friend_id_edit.setPlaceholderText("Friend's user id")
        add_dm = QPushButton("➕  Add / open DM")
        add_dm.clicked.connect(self._add_friend_from_dialog)
        row.addWidget(self._friend_id_edit, stretch=1)
        row.addWidget(add_dm)
        lay.addLayout(row)

        inv = QGroupBox("Invite")
        il = QVBoxLayout(inv)
        self._invite_edit = QTextEdit()
        self._invite_edit.setPlaceholderText("Paste an invite (includes server and user ID)")
        self._invite_edit.setMaximumHeight(100)
        il.addWidget(self._invite_edit)
        apply_inv = QPushButton("📥  Apply invite")
        apply_inv.clicked.connect(self._apply_invite)
        il.addWidget(apply_inv)
        lay.addWidget(inv)

        room_row = QHBoxLayout()
        self._room_id_edit = QLineEdit()
        self._room_id_edit.setPlaceholderText("Room id")
        add_rm = QPushButton("📝  Add room")
        add_rm.clicked.connect(self._add_room_from_dialog)
        join_rm = QPushButton("🔗  Join room")
        join_rm.clicked.connect(self._main.join_room)
        room_row.addWidget(self._room_id_edit, stretch=1)
        room_row.addWidget(add_rm)
        room_row.addWidget(join_rm)
        lay.addLayout(room_row)

        krow = QHBoxLayout()
        sk = QPushButton("🔑  Send security key")
        sk.clicked.connect(self._main.send_key_exchange)
        tk = QPushButton("✓  Trust key change")
        tk.clicked.connect(self._main.trust_key_change)
        krow.addWidget(sk)
        krow.addWidget(tk)
        lay.addLayout(krow)
        lay.addStretch(1)
        return w

    def _build_voice_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        h = QLabel("Voice & video")
        h.setObjectName("SettingsHeading")
        lay.addWidget(h)
        body = QLabel(
            "Voice and video need extra technology (WebRTC) that isn’t in this version yet. "
            "Right now you can chat and send files through your server."
        )
        body.setWordWrap(True)
        lay.addWidget(body)
        box = QGroupBox("Coming in a future update")
        gl = QVBoxLayout(box)
        for label in ("Join voice (stub)", "Microphone (stub)", "Camera (stub)", "Screen share (stub)"):
            cb = QCheckBox(label)
            cb.setEnabled(False)
            gl.addWidget(cb)
        lay.addWidget(box)
        lay.addStretch(1)
        return w

    def _build_logs_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        h = QLabel("Activity logs")
        h.setObjectName("SettingsHeading")
        lay.addWidget(h)
        sub = QLabel(
            "Technical messages and connection details since you opened the app. "
            "New lines appear here while this window stays open — nothing is sent off your computer."
        )
        sub.setObjectName("SettingsSub")
        sub.setWordWrap(True)
        lay.addWidget(sub)
        self._activity_log = QPlainTextEdit()
        self._activity_log.setObjectName("ActivityLogSettings")
        self._activity_log.setReadOnly(True)
        self._activity_log.setPlaceholderText("Activity will show here after you use Connect or chat.")
        lay.addWidget(self._activity_log, stretch=1)
        return w

    def _refresh_account_labels(self) -> None:
        self._acc_name.setText(f"<b>Display name</b>: {self._main.display_name}")
        self._acc_id.setText(f"<b>User ID</b>: {self._main.user_id}")
        self._acc_name.setTextFormat(Qt.TextFormat.RichText)
        self._acc_id.setTextFormat(Qt.TextFormat.RichText)

    def _refresh_diagnostics(self) -> None:
        m = self._main
        state = getattr(m, "_server_state", "?")
        self._diag_state.setText(f"State: {state}")
        colors = {
            "Connected": "#2e7d32",
            "Connecting": "#f9a825",
            "Disconnected": "#546e7a",
            "Error": "#c62828",
        }
        col = colors.get(state, "#546e7a")
        self._diag_badge.setText(state)
        self._diag_badge.setStyleSheet(
            f"background-color: {col}; color: white; border-radius: 6px; padding: 6px 10px; font-weight: 700;"
        )
        self._diag_url.setText(f"Active URL: {m.client.server_url}")
        self._diag_err.setText(f"Last error: {getattr(m, '_last_error', '-')}")
        self._diag_attempts.setText(f"Connect attempts: {getattr(m, '_reconnect_attempts', 0)}")
        self._diag_peers.setText(f"Peers online (seen): {len(getattr(m, '_online_peers', set()))}")
        self._diag_trust.setText(getattr(m, "_trust_status_text", "Trust: n/a"))

    def _copy_user_id(self) -> None:
        QGuiApplication.clipboard().setText(self._main.user_id)

    def _edit_profile_from_settings(self) -> None:
        self._main.edit_profile()
        self._server_url_edit.setText(self._main.client.server_url)
        self._refresh_account_labels()
        self._refresh_diagnostics()

    def _save_server_from_dialog(self) -> None:
        if self._main.apply_server_url(self._server_url_edit.text()):
            self._refresh_diagnostics()

    def _add_friend_from_dialog(self) -> None:
        uid = self._friend_id_edit.text().strip()
        if not uid:
            return
        self._main.add_direct(uid)
        self._friend_id_edit.clear()

    def _add_room_from_dialog(self) -> None:
        rid = self._room_id_edit.text().strip()
        if not rid:
            return
        self._main.add_room(rid)
        self._room_id_edit.clear()

    def _apply_invite(self) -> None:
        text = self._invite_edit.toPlainText()
        server, uid = _parse_invite_block(text)
        if server and not self._main.apply_server_url(server):
            return
        if uid:
            self._main.add_direct(uid)
        if not server and not uid:
            self._main.push_toast(
                "[hint] Paste an invite that includes a ws:// or wss:// line and a user ID.",
                "hint",
            )
            return
        self._invite_edit.clear()
        self._server_url_edit.setText(self._main.client.server_url)
        self._refresh_diagnostics()

    def _on_friend_search(self, q: str) -> None:
        qn = q.casefold().strip()
        lines: list[str] = []
        conv = self._main.conversations
        for i in range(conv.count()):
            t = conv.item(i).text()
            if not qn or qn in t.casefold():
                lines.append(t.split(" [", 1)[0])
        self._friend_results.setPlainText("\n".join(lines) if lines else "(no matches)")

    def _append_activity_line(self, line: str) -> None:
        self._activity_log.moveCursor(QTextCursor.MoveOperation.End)
        self._activity_log.insertPlainText(line + "\n")

    def _attach_activity_log(self) -> None:
        if self._log_conn is not None:
            return
        self._log_conn = self._append_activity_line
        self._activity_log.setPlainText(self._main.get_activity_log_text())
        self._main.bus.activity_logged.connect(self._append_activity_line)

    def _detach_activity_log(self) -> None:
        if self._log_conn is None:
            return
        try:
            self._main.bus.activity_logged.disconnect(self._append_activity_line)
        except Exception:
            pass
        self._log_conn = None
