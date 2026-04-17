"""First-run profile setup dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class SetupDialog(QDialog):
    def __init__(self, display_name: str, user_id: str, server_url: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Intel Byte 256 Setup")
        self.resize(420, 220)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Set your profile and server URL."))

        form = QFormLayout()
        self.display_name_input = QLineEdit(display_name)
        self.user_id_input = QLineEdit(user_id)
        self.server_url_input = QLineEdit(server_url)
        self.display_name_input.setPlaceholderText("e.g. Laurence")
        self.user_id_input.setPlaceholderText("e.g. laurence_01")
        self.server_url_input.setPlaceholderText("ws://127.0.0.1:8765")
        form.addRow("Display Name", self.display_name_input)
        form.addRow("User ID", self.user_id_input)
        form.addRow("Server URL", self.server_url_input)
        layout.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff6666;")
        layout.addWidget(self.error_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if not self.user_id_input.text().strip():
            self.error_label.setText("User ID is required.")
            return
        if not self.server_url_input.text().strip().startswith("ws://") and not self.server_url_input.text().strip().startswith(
            "wss://"
        ):
            self.error_label.setText("Server URL must start with ws:// or wss://")
            return
        self.accept()

    def result_settings(self) -> dict[str, str]:
        display_name = self.display_name_input.text().strip()
        user_id = self.user_id_input.text().strip()
        return {
            "display_name": display_name or user_id,
            "user_id": user_id,
            "server_url": self.server_url_input.text().strip(),
        }

