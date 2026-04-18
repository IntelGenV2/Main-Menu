"""Reusable UI widgets for conversation and message panels."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem


class ConversationList(QListWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("ConversationList")

    def add_conversation(self, label: str) -> None:
        if not self.findItems(label, Qt.MatchFlag.MatchExactly):
            self.addItem(QListWidgetItem(label))

    def set_conversation_state(self, base_label: str, state: str) -> None:
        for index in range(self.count()):
            item = self.item(index)
            if item.text() == base_label or item.text().startswith(f"{base_label} ["):
                item.setText(f"{base_label} [{state}]")
                return

