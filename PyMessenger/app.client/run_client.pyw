"""Double-click launcher for Intel Byte 256 client (no terminal window)."""

from pathlib import Path
import os

# Imports resolve `messenger_app` from the project root; ensure CWD is that folder
# when launched from Explorer, shortcuts, or another directory.
os.chdir(Path(__file__).resolve().parent)

from messenger_app.main import main


if __name__ == "__main__":
    raise SystemExit(main())

