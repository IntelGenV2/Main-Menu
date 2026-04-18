"""Small dismissible toasts for connection / system messages (bottom-left stack)."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget


_KIND_ICONS: dict[str, str] = {
    "hint": "💡",
    "connect": "🔌",
    "error": "⚠",
    "server": "🖥",
    "presence": "●",
    "typing": "…",
    "trust": "🔑",
    "friend": "👤",
    "room": "#",
    "settings": "⚙",
    "ui": "◇",
    "read": "✓",
    "ack": "✉",
    "file": "📎",
    "default": "•",
}


class ActivityToast(QFrame):
    def __init__(
        self,
        message: str,
        kind: str,
        parent: QWidget,
        dismiss_ms: int = 8500,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("ActivityToast")
        icon = _KIND_ICONS.get(kind.lower(), _KIND_ICONS["default"])
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 6, 6)
        layout.setSpacing(8)
        ic = QLabel(icon)
        ic.setObjectName("ToastIcon")
        layout.addWidget(ic, alignment=Qt.AlignmentFlag.AlignTop)
        text = QLabel(message)
        text.setWordWrap(True)
        text.setObjectName("ToastText")
        layout.addWidget(text, stretch=1)
        close = QPushButton("✕")
        close.setObjectName("ToastClose")
        close.setFixedSize(22, 22)
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.clicked.connect(self._dismiss)
        layout.addWidget(close, alignment=Qt.AlignmentFlag.AlignTop)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dismiss)
        self._timer.start(dismiss_ms)

    def _dismiss(self) -> None:
        self._timer.stop()
        host = self.parentWidget()
        if host is not None:
            ly = host.layout()
            if ly is not None:
                ly.removeWidget(self)
        self.deleteLater()
