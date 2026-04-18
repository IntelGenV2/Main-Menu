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
        self.setWindowTitle("Intel Byte 256 — Welcome")
        self.resize(460, 320)

        layout = QVBoxLayout(self)
        title = QLabel("Set up your profile")
        title.setObjectName("SetupTitle")
        layout.addWidget(title)

        sub = QLabel(
            "Pick how you appear, a unique user ID, and your chat server’s WebSocket address "
            "(starts with ws:// or wss://). You can change these later in Settings."
        )
        sub.setObjectName("SetupSub")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        form = QFormLayout()
        self.display_name_input = QLineEdit(display_name)
        self.user_id_input = QLineEdit(user_id)
        self.server_url_input = QLineEdit(server_url)
        self.display_name_input.setPlaceholderText("How you appear to friends")
        self.user_id_input.setPlaceholderText("Unique id, e.g. laurence_01")
        self.server_url_input.setPlaceholderText("Example: wss://chat.example.com:8765")
        form.addRow("Display name", self.display_name_input)
        form.addRow("User ID", self.user_id_input)
        form.addRow("Intel Byte server URL", self.server_url_input)
        layout.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setObjectName("SetupError")
        layout.addWidget(self.error_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setStyleSheet(
            """
            QDialog {
                background-color: #313338;
                color: #dbdee1;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 13px;
            }
            QLabel#SetupTitle {
                color: #f2f3f5;
                font-size: 20px;
                font-weight: 700;
            }
            QLabel#SetupSub { color: #949ba4; font-size: 12px; }
            QLabel#SetupError { color: #ed4245; font-size: 12px; }
            QLabel { color: #b5bac1; }
            QLineEdit {
                background-color: #1e1f22;
                border: 1px solid #1e1f22;
                border-radius: 4px;
                padding: 8px 10px;
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
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5c5f6a;
                border-color: #787c87;
            }
            QPushButton:pressed { background-color: #3c3f45; }
            """
        )

    def _on_accept(self) -> None:
        if not self.user_id_input.text().strip():
            self.error_label.setText("Please enter a user ID.")
            return
        url = self.server_url_input.text().strip()
        if not url.startswith("ws://") and not url.startswith("wss://"):
            self.error_label.setText("Server address must start with ws:// or wss://.")
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
