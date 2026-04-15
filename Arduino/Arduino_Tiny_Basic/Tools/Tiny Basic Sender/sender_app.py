"""
Tiny BASIC Serial Sender – Dark-mode GUI to send .bas files to Arduino Tiny BASIC.
Double-click sender_app.py or sender_app.pyw to run (no console with .pyw).
"""
import os
import re
import sys
import threading

# Allow running from project root or from this directory
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)


import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Optional: pyserial (install via pip install pyserial)
try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

from tiny_basic_syntax import (
    BASIC_PROGRAM_LIMIT_BYTES,
    check_tiny_basic_syntax,
    estimate_program_storage_bytes,
)

DEFAULT_BAUD = 4800
BAUD_CHOICES = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]


class SerialSender:
    """Handles serial open/close and send-one-line; reads serial only when waiting for prompt."""

    def __init__(self, port: str, baud: int, log_callback):
        self.port = port
        self.baud = baud
        self.log = log_callback
        self.ser = None
        self._stop = threading.Event()
        self._rx_buffer = ""
        self._lock = threading.Lock()
        self._logged_stages = set()  # stages we've already logged this session

    def open(self, reset_on_connect: bool = True) -> bool:
        if not HAS_SERIAL:
            self.log("[ERROR] pyserial not installed. Run: pip install pyserial", "error")
            return False
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=0.1,
                write_timeout=2.0,
            )
            if reset_on_connect:
                self.ser.dtr = False
                import time
                time.sleep(0.05)
                self.ser.dtr = True
                time.sleep(0.1)
                self.log("[ARDUINO] Reset (DTR).", "arduino")
            self._stop.clear()
            self._rx_buffer = ""
            self._logged_stages = set()
            self.log(f"[CONNECTED] {self.port} @ {self.baud} baud", "info")
            return True
        except Exception as e:
            self.log(f"[ERROR] Open serial: {e}", "error")
            return False

    def close(self):
        self._stop.set()
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None
        self.log("[DISCONNECTED]", "info")

    def _read_available(self):
        """Read any available serial data into buffer (call only when waiting for prompt)."""
        if not self.ser or not self.ser.is_open:
            return
        try:
            if self.ser.in_waiting:
                data = self.ser.read(self.ser.in_waiting)
                if data:
                    text = data.decode("utf-8", errors="replace")
                    with self._lock:
                        self._rx_buffer += text
        except Exception:
            pass

    # Stage order for one-time logging (check buffer in this order, log each once)
    # "Linking" step removed – boot no longer shows GRID/SYNC progress bars.
    _STAGE_ORDER = [
        ("boot", "&~~~~", "[ARDUINO] Booting..."),
        ("boot", "TRON GRID", "[ARDUINO] Booting..."),
        ("password", "Password:", "[ARDUINO] Asking for password..."),
        ("boot_complete", "WELCOME", "[ARDUINO] Boot complete."),
        ("prompt", ">", None),
    ]

    def _log_stages_from_buffer(self):
        """Log each boot stage at most once, in order, based on current buffer."""
        with self._lock:
            buf = self._rx_buffer
        buf_upper = buf.upper()
        for stage_key, marker, msg in self._STAGE_ORDER:
            if stage_key in self._logged_stages:
                continue
            if stage_key == "prompt":
                continue  # handled in wait_for_prompt
            found = (marker in buf) or (marker.upper() in buf_upper)
            if found:
                self._logged_stages.add(stage_key)
                if msg:
                    self.log(msg, "arduino")
                break  # one new stage per call

    def wait_for_prompt(self, timeout_sec: float = 60.0, require_ok: bool = False) -> bool:
        """Wait until ready for next line. If require_ok=True (first time), wait for OK then >.
        Consumes up to and including the '>'."""
        import time
        start = time.monotonic()
        while (time.monotonic() - start) < timeout_sec:
            self._read_available()
            self._log_stages_from_buffer()
            with self._lock:
                buf = self._rx_buffer
            has_ok = "OK" in buf
            has_prompt = ">" in buf
            if require_ok and not has_ok:
                time.sleep(0.05)
                continue
            if not has_prompt:
                time.sleep(0.05)
                continue
            with self._lock:
                idx = self._rx_buffer.rfind(">")
                self._rx_buffer = self._rx_buffer[idx + 1 :]
            return True
        self.log("[TIMEOUT] Did not see prompt (>).", "error")
        return False

    def send_line(self, line: str) -> bool:
        if not self.ser or not self.ser.is_open:
            return False
        # Arduino expects ASCII " and ' for PRINT strings; normalize smart/Unicode quotes
        line = line.rstrip("\r\n")
        for old, new in [("\u201c", '"'), ("\u201d", '"'), ("\u2018", "'"), ("\u2019", "'")]:
            line = line.replace(old, new)
        payload = (line + "\r").encode("utf-8")
        try:
            self.ser.write(payload)
            return True
        except Exception as e:
            self.log(f"[ERROR] Write: {e}", "error")
            return False


def get_serial_ports():
    """Return list of (device, display_string) for dropdown. display_string shows device + description."""
    if not HAS_SERIAL:
        return []
    result = []
    for p in serial.tools.list_ports.comports():
        device = p.device
        desc = (p.description or "").strip()
        product = (p.product or "").strip() if hasattr(p, "product") else ""
        # Prefer description, fall back to product, else just device
        extra = desc or product
        if extra and extra.lower() != "n/a":
            display = f"{device} — {extra}"
        else:
            display = device
        result.append((device, display))
    return result


class TinyBasicSenderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tiny BASIC → Arduino Sender")
        self.root.minsize(520, 420)
        self.root.geometry("640x520")

        # Dark theme
        bg = "#1e1e2e"
        fg = "#cdd6f4"
        entry_bg = "#313244"
        accent = "#89b4fa"
        self.colors = {
            "bg": bg,
            "fg": fg,
            "entry_bg": entry_bg,
            "accent": accent,
            "log_arduino": "#a6e3a1",
            "log_app": "#89b4fa",
            "log_error": "#f38ba8",
            "log_info": "#b4befe",
        }
        self.root.configure(bg=bg)
        self._style_ttk_dark()

        self.sender: SerialSender | None = None
        self.sending = False
        self._build_ui()

    def _style_ttk_dark(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure("TButton", background=self.colors["entry_bg"], foreground=self.colors["fg"])
        style.configure("TCheckbutton", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure("TFrame", background=self.colors["bg"])
        style.map("TButton", background=[("active", self.colors["accent"])])

    def _build_ui(self):
        f = ttk.Frame(self.root, padding=10)
        f.pack(fill=tk.BOTH, expand=True)

        # File
        row1 = ttk.Frame(f)
        row1.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row1, text="BASIC file:").pack(side=tk.LEFT, padx=(0, 8))
        self.file_var = tk.StringVar()
        self.file_entry = tk.Entry(
            row1, textvariable=self.file_var, width=50,
            bg=self.colors["entry_bg"], fg=self.colors["fg"],
            insertbackground=self.colors["fg"], relief=tk.FLAT, font=("Consolas", 10)
        )
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(row1, text="Browse…", command=self._browse).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(row1, text="Check syntax", command=self._check_syntax_clicked).pack(side=tk.LEFT)

        # COM + Baud
        row2 = ttk.Frame(f)
        row2.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row2, text="Device:").pack(side=tk.LEFT, padx=(0, 8))
        self.com_var = tk.StringVar()
        ports = get_serial_ports()
        ports_init = [p[1] for p in ports] if ports else [""]
        self._com_menu = tk.OptionMenu(row2, self.com_var, *ports_init)
        self._com_menu.config(
            bg=self.colors["entry_bg"], fg=self.colors["fg"],
            activebackground=self.colors["entry_bg"], activeforeground=self.colors["fg"],
            highlightthickness=0
        )
        self._com_menu["menu"].config(
            bg=self.colors["entry_bg"], fg=self.colors["fg"],
            activebackground=self.colors["accent"], activeforeground=self.colors["fg"]
        )
        self._com_menu.pack(side=tk.LEFT, padx=(0, 16))
        ttk.Button(row2, text="Refresh", command=self._refresh_ports).pack(side=tk.LEFT, padx=(0, 16))
        ttk.Label(row2, text="Baud:").pack(side=tk.LEFT, padx=(0, 8))
        self.baud_var = tk.StringVar(value=str(DEFAULT_BAUD))
        baud_list = [str(b) for b in BAUD_CHOICES]
        self._baud_menu = tk.OptionMenu(row2, self.baud_var, *baud_list)
        self._baud_menu.config(
            bg=self.colors["entry_bg"], fg=self.colors["fg"],
            activebackground=self.colors["entry_bg"], activeforeground=self.colors["fg"],
            highlightthickness=0
        )
        self._baud_menu["menu"].config(
            bg=self.colors["entry_bg"], fg=self.colors["fg"],
            activebackground=self.colors["accent"], activeforeground=self.colors["fg"]
        )
        self._baud_menu.pack(side=tk.LEFT)

        # Run after send
        row3 = ttk.Frame(f)
        row3.pack(fill=tk.X, pady=(0, 6))
        self.run_after_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            row3, text="Run program after send", variable=self.run_after_var
        ).pack(side=tk.LEFT)

        # Send button
        row4 = ttk.Frame(f)
        row4.pack(fill=tk.X, pady=(0, 8))
        self.send_btn = ttk.Button(row4, text="Send to Arduino", command=self._send_clicked)
        self.send_btn.pack(side=tk.LEFT)

        # Program memory (bar: green = within limit, red = over)
        mem_row = ttk.Frame(f)
        mem_row.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(mem_row, text="Program memory:").pack(side=tk.LEFT, padx=(0, 8))
        self._mem_canvas = tk.Canvas(
            mem_row,
            height=16,
            bg=self.colors["entry_bg"],
            highlightthickness=0,
            bd=0,
        )
        self._mem_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self._mem_text_var = tk.StringVar(value="")
        ttk.Label(mem_row, textvariable=self._mem_text_var).pack(side=tk.LEFT)
        self._mem_approx: int | None = None
        self._mem_canvas.bind("<Configure>", lambda _e: self._redraw_memory_bar())

        # Log
        log_header = ttk.Frame(f)
        log_header.pack(fill=tk.X, pady=(4, 2))
        ttk.Label(log_header, text="Serial Log:").pack(side=tk.LEFT)
        ttk.Button(log_header, text="Clear log", command=self._log_clear).pack(side=tk.RIGHT)
        self.log_text = scrolledtext.ScrolledText(
            f, height=18, wrap=tk.WORD, state=tk.DISABLED,
            bg="#11111b", fg=self.colors["fg"], insertbackground=self.colors["fg"],
            font=("Consolas", 9), relief=tk.FLAT, padx=6, pady=6
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        self.log_text.tag_configure("arduino", foreground=self.colors["log_arduino"])
        self.log_text.tag_configure("app", foreground=self.colors["log_app"])
        self.log_text.tag_configure("error", foreground=self.colors["log_error"])
        self.log_text.tag_configure("info", foreground=self.colors["log_info"])

        self.file_var.trace_add("write", lambda *_: self.root.after_idle(self._refresh_memory_from_file))

        self._refresh_ports()
        self._refresh_memory_from_file()

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select BASIC file",
            filetypes=[("BASIC files", "*.bas *.txt"), ("All files", "*.*")]
        )
        if path:
            self.file_var.set(path)

    def _check_syntax_clicked(self):
        path = self.file_var.get().strip()
        if not path or not os.path.isfile(path):
            self._log("[ERROR] Please select a BASIC file.", "error")
            return
        self._log_clear()
        self._run_syntax_check(path)

    def _run_syntax_check(self, path: str) -> bool:
        """Run syntax check and log results. Returns True if OK, False if errors."""
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception as e:
            self._log(f"[SYNTAX] Cannot read file: {e}", "error")
            return False
        errors = check_tiny_basic_syntax(lines, is_program=True)
        if not errors:
            self._log(f"[SYNTAX] OK: {len(lines)} lines, Tiny BASIC compliant.", "info")
            return True
        self._log(f"[SYNTAX] {len(errors)} issue(s) found:", "error")
        for err in errors[:15]:
            m = re.match(r"^\s*(\d+)\s*", err.line_content)
            line_label = m.group(1) if m else str(err.line_no)
            self._log(f"  Line {line_label}: {err.message}", "error")
        if len(errors) > 15:
            self._log(f"  ... and {len(errors) - 15} more.", "error")
        return False

    def _refresh_ports(self):
        ports = get_serial_ports()  # list of (device, display)
        menu = self._com_menu["menu"]
        menu.delete(0, tk.END)
        for device, display in ports:
            menu.add_command(label=display, command=lambda v=display: self.com_var.set(v))
        if ports and not self.com_var.get():
            self.com_var.set(ports[0][1])  # set display string
        elif not ports:
            self.com_var.set("")

    def _log_clear(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _log(self, msg: str, tag: str = "info"):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _refresh_memory_from_file(self):
        path = self.file_var.get().strip()
        if not path or not os.path.isfile(path):
            self._mem_approx = None
            self._redraw_memory_bar()
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            self._mem_approx = estimate_program_storage_bytes(lines)
        except OSError:
            self._mem_approx = None
        self._redraw_memory_bar()

    def _redraw_memory_bar(self):
        self._mem_canvas.delete("all")
        w = max(40, self._mem_canvas.winfo_width())
        h = 16
        track = "#313244"
        self._mem_canvas.create_rectangle(0, 0, w, h, fill=track, outline="")
        approx = self._mem_approx
        limit = BASIC_PROGRAM_LIMIT_BYTES
        if approx is None:
            self._mem_text_var.set("—")
            return
        over = approx > limit
        ratio = (approx / limit) if limit > 0 else 0.0
        if over:
            fill_w = w
            color = "#f38ba8"
        else:
            fill_w = max(0, min(w, int(ratio * w)))
            color = "#a6e3a1"
        if fill_w > 0:
            self._mem_canvas.create_rectangle(0, 0, fill_w, h, fill=color, outline="")
        self._mem_text_var.set(f"{approx} / {limit} bytes")

    def _device_from_port_var(self, port_var: str) -> str:
        """Extract device (e.g. COM3) from port var which may be 'COM3 — Arduino Uno'."""
        s = (port_var or "").strip()
        if " — " in s:
            return s.split(" — ", 1)[0].strip()
        return s

    def _send_clicked(self):
        self._log_clear()  # Clear log at start of Send action
        path = self.file_var.get().strip()
        if not path or not os.path.isfile(path):
            self._log("[ERROR] Please select a BASIC file.", "error")
            return
        port_var = self.com_var.get().strip()
        if not port_var:
            self._log("[ERROR] Please select a COM port.", "error")
            return
        port = self._device_from_port_var(port_var)
        try:
            baud = int(self.baud_var.get())
        except ValueError:
            self._log("[ERROR] Invalid baud rate.", "error")
            return

        # Optional: warn if syntax errors
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        errors = check_tiny_basic_syntax(lines, is_program=True)
        if errors:
            self._log(f"[SYNTAX] {len(errors)} issue(s) found.", "error")
            for err in errors[:5]:
                m = re.match(r"^\s*(\d+)\s*", err.line_content)
                line_label = m.group(1) if m else str(err.line_no)
                self._log(f"  Line {line_label}: {err.message}", "error")
            if len(errors) > 5:
                self._log(f"  ... and {len(errors) - 5} more.", "error")
            if not messagebox.askyesno("Syntax issues", f"Found {len(errors)} syntax issue(s). Send anyway?"):
                return
            self._log("[APP] Sending despite syntax issues...", "app")
        else:
            self._log("[SYNTAX] OK.", "info")

        self.send_btn.configure(state=tk.DISABLED)
        self.sending = True
        threading.Thread(
            target=self._send_worker,
            args=(path, port, baud),
            daemon=True
        ).start()

    def _send_worker(self, path: str, port: str, baud: int):
        import time
        run_after = self.run_after_var.get()
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = [ln.rstrip("\r\n") for ln in f.readlines()]

            self.root.after(0, lambda: self._log("[APP] Opening serial (DTR reset)…", "app"))
            sender = SerialSender(port, baud, self._log_cb)
            if not sender.open():
                self.root.after(0, lambda: self._done_sending())
                return

            self.sender = sender
            program_lines = [ln for ln in lines if ln.strip()]

            if not sender.wait_for_prompt(timeout_sec=90.0, require_ok=True):
                self.root.after(0, lambda: self._log("[APP] Aborting send: prompt not seen.", "error"))
                self.root.after(0, lambda: self._done_sending())
                return

            for line in program_lines:
                self.root.after(0, lambda l=line: self._log(f"[SENT] {l.strip()}", "info"))
                if not sender.send_line(line):
                    break
                if not sender.wait_for_prompt(timeout_sec=15.0, require_ok=False):
                    self.root.after(0, lambda: self._log("[APP] Timeout waiting for prompt after line.", "error"))
                    break
            else:
                if run_after:
                    self.root.after(0, lambda: self._log("[APP] Sending RUN.", "app"))
                    sender.send_line("RUN")
                    time.sleep(0.5)
                self.root.after(0, lambda: self._log("[APP] Send complete.", "app"))
        except Exception as e:
            self.root.after(0, lambda: self._log(f"[ERROR] {e}", "error"))
        finally:
            if self.sender:
                self.sender.close()
                self.sender = None
            self.root.after(0, lambda: self._done_sending())

    def _log_cb(self, msg: str, tag: str = "info"):
        self.root.after(0, lambda: self._log(msg, tag))

    def _done_sending(self):
        self.sending = False
        self.send_btn.configure(state=tk.NORMAL)

    def run(self):
        self.root.mainloop()


def main():
    app = None
    try:
        app = TinyBasicSenderApp()
        app.run()
    except Exception as e:
        import traceback
        err_msg = f"[ERROR] {e}\n\n{traceback.format_exc()}"
        if app is not None:
            try:
                app._log(err_msg, "error")
                app.root.deiconify()
                app.root.lift()
            except Exception:
                sys.stderr.write(err_msg)
        else:
            sys.stderr.write(err_msg)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        sys.stderr.write(f"{e}\n\n{traceback.format_exc()}")
        sys.exit(1)
