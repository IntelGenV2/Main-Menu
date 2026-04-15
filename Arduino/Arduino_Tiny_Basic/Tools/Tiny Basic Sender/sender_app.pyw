# Launcher: double-click to run without opening a console (Windows).
# Uses pythonw.exe so no command window appears.
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
import sender_app
sender_app.main()
