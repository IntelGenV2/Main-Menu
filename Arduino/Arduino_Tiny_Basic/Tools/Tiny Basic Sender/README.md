# Tiny BASIC Serial Sender

GUI app to send `.bas` files to your Arduino Tiny BASIC computer over serial.

## Run without command line

- **Double-click `sender_app.pyw`** (Windows) – opens the app with no console window.
- Or run: `python sender_app.py` (or `python sender_app.pyw`) from this folder.

## Requirements

```bash
pip install -r requirements.txt
```

(Installs `pyserial`.)

## Usage

1. **BASIC file** – Click **Browse…** and select your `.bas` file. Syntax is checked when you pick a file.
2. **COM port** – Select the Arduino’s COM port; use **Refresh** if it doesn’t appear.
3. **Baud** – Default **4800** (matches the Master sketch). Change only if your firmware uses another baud rate.
4. **Run after send** – If checked, sends `RUN` after the last line (default: off).
5. Click **Send to Arduino**.

## What the app does

- Opens the serial port and **resets the Arduino** (DTR) so it boots from a known state.
- Waits for the boot sequence and logs it in order:
  - Arduino reset  
  - Boot (TRON GRID)  
  - Asking for password (you must type the password on the **device keyboard**)  
  - Boot checks (Linking Grid, SYNC, Identifying, Testing, storage)  
  - Boot complete (WELCOME, GRID LINK)  
  - Ready at prompt (`>`)  
- Sends the BASIC file **one line at a time**, each line ending with CR. After each line it waits for `>` before sending the next.
- If **Run after send** is on, it sends `RUN` after the last line.

## Syntax checker

The checker uses `Manual/TINYBASIC_SYNTAX.md` and the Master code rules, including:

- Line format: `[line_number] statement [: statement ...]`
- **Duplicate line numbers**: reports an error; in Tiny BASIC the second line replaces the first and often breaks FOR/NEXT or GOTOs.
- Variables: single letters A–Z only
- **PRINT**: items separated by **comma**; **semicolon** only at the very end (to suppress newline)
- Known keywords and no semicolons between PRINT items

You can still send a file if the checker reports issues (you’ll be asked to confirm).
