"""
Tiny BASIC syntax checker. Rules from Manual/TINYBASIC_SYNTAX.md and
PS2_Keyboard_Master_v0_30_commented.ino.
"""
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Keywords (interpreter order; we use for validation)
# SD commands (LOAD, SAVE, FILES, CHAIN) removed to match .ino.
KEYWORDS = {
    "LIST", "NEW", "RUN", "NEXT", "LET", "IF", "THEN", "GOTO", "GOSUB",
    "RETURN", "REM", "DATA", "READ", "RESTORE", "FOR", "INPUT", "PRINT", "BYE",
    "CLS", "MEM", "AWRITE", "DWRITE", "DELAY", "END", "RSEED",
    "TONEW", "!", "TONE", "NOTONE", "ECHAIN", "ELIST", "ELOAD", "EFORMAT", "ESAVE",
}
# Statement shorthands (matches firmware): ? = INPUT, . = PRINT
KEYWORDS_EXTRA = {"?", "."}

FUNCTIONS = {"ABS", "AREAD", "DREAD", "RND"}


def _is_firmware_glued_for(token: str) -> bool:
    """FOR + single letter A–Z with no space (interpreter matches FOR then var)."""

    return bool(re.fullmatch(r"FOR[A-Z]", token, re.I))


def _is_firmware_glued_next(token: str) -> bool:
    """NEXT + single letter A–Z with no space (interpreter matches NEXT then var)."""

    return bool(re.fullmatch(r"NEXT[A-Z]", token, re.I))
RELOPS = (">=", "<>", ">", "=", "<=", "<", "!=")
HIGH_LOW = {"HIGH", "HI", "LOW", "LO"}

# Max bytes in firmware program[] (lines + scratch only). Must match #define kRamSize
# in Arduino_Tiny_Basic_1/PS2_Keyboard_Master_v0_30_commented/PS2_Keyboard_Master_v0_30_commented.ino.
DEFAULT_BASIC_BYTES = 1024
BASIC_PROGRAM_LIMIT_BYTES = DEFAULT_BASIC_BYTES
MAX_STORED_LINE_RECORD_BYTES = 255  # [LINENUM 2][LEN 1][TEXT][NL], LEN is one byte


def _stored_line_record_bytes(line: str) -> int:
    """Firmware line record size: 2-byte line num + 1-byte LEN + text bytes + NL (in len(line))."""
    return len(line) + 3


@dataclass
class SyntaxError:
    line_no: int
    message: str
    line_content: str


def _strip_rem(line: str) -> str:
    """Remove REM ... to end of line for parsing rest (apostrophe-as-REM removed in firmware)."""
    for marker in ("REM ", "REM\t"):
        if marker in line and line.strip().upper().startswith("REM"):
            idx = line.upper().find("REM")
            if idx >= 0:
                return line[:idx].strip()
    # REM in middle (after statement)
    upper = line.upper()
    i = 0
    in_string = None
    while i < len(line):
        c = line[i]
        if in_string:
            if c == in_string and (i == 0 or line[i - 1] != "\\"):
                in_string = None
            i += 1
            continue
        if c in ('"', "'"):
            in_string = c
            i += 1
            continue
        if i < len(line) - 3 and upper[i : i + 4] == " REM" and line[i].isspace():
            return line[:i].strip()
        i += 1
    return line.strip()


def _tokenize_for_check(s: str) -> List[str]:
    """Simple tokenize: strings, numbers, identifiers, symbols."""
    tokens = []
    i = 0
    s = s.strip()
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        if s[i] in ('"', "'"):
            q = s[i]
            start = i
            i += 1
            while i < len(s) and s[i] != q:
                if s[i] == "\\":
                    i += 1
                i += 1
            if i < len(s):
                i += 1
            tokens.append(s[start:i])
            continue
        if s[i].isdigit():
            start = i
            while i < len(s) and s[i].isdigit():
                i += 1
            tokens.append(s[start:i])
            continue
        if s[i].isalpha() or s[i] == "_":
            start = i
            while i < len(s) and (s[i].isalnum() or s[i] == "_"):
                i += 1
            tokens.append(s[start:i].upper())
            continue
        # symbols
        for op in (">=", "<=", "<>", "!=", "=", ">", "<", "+", "-", "*", "/", "(", ")", ",", ":", ";"):
            if s[i : i + len(op)] == op:
                tokens.append(op)
                i += len(op)
                break
        else:
            tokens.append(s[i])
            i += 1
    return tokens


def check_delay_terminates_line(content: str, line_no: int, raw_line: str) -> List[SyntaxError]:
    """
    Interpreter quirk (PS2_Keyboard_Master KW_DELAY): after DELAY expr, execution does
    goto execnextline — it never continues with further ':' statements on the same line.
    Unreachable code after DELAY often causes confusing failures (e.g. GOSUB ERROR when a
    subroutine line runs without a matching GOSUB).
    """
    errors: List[SyntaxError] = []
    tokens = _tokenize_for_check(content)
    n = len(tokens)
    i = 0
    if n and tokens[0].isdigit():
        i = 1
    while i < n:
        if tokens[i] == ":":
            i += 1
            continue
        if tokens[i] == "DELAY":
            i += 1
            depth = 0
            while i < n:
                t = tokens[i]
                if t == "(":
                    depth += 1
                elif t == ")":
                    depth -= 1
                elif t == ":" and depth == 0:
                    if i + 1 < n:
                        errors.append(
                            SyntaxError(
                                line_no,
                                "DELAY always jumps to the next program line in this interpreter; "
                                "statements after ':' on the same line are never executed. "
                                "Put DELAY on its own line.",
                                raw_line,
                            )
                        )
                    break
                i += 1
            continue
        depth = 0
        while i < n:
            t = tokens[i]
            if t == "(":
                depth += 1
            elif t == ")":
                depth -= 1
            elif t == ":" and depth == 0:
                break
            i += 1
    return errors


def _split_colon_statements(s: str) -> List[str]:
    """Split on ':' outside quoted strings."""
    parts: List[str] = []
    n = len(s)
    i = 0
    start = 0
    in_string: Optional[str] = None
    while i < n:
        c = s[i]
        if in_string:
            if c == in_string and (i == 0 or s[i - 1] != "\\"):
                in_string = None
            i += 1
            continue
        if c in ('"', "'"):
            in_string = c
            i += 1
            continue
        if c == ":":
            parts.append(s[start:i])
            start = i + 1
        i += 1
    parts.append(s[start:])
    return parts


def _semicolon_in_print_rest(rest: str, line_no: int, line: str) -> List[SyntaxError]:
    """rest = source after PRINT or after '.' print shorthand; REM-trimmed tail."""
    errors: List[SyntaxError] = []
    if not rest:
        return errors
    rest = _strip_rem("X " + rest)[1:].strip()
    in_string = None
    i = 0
    while i < len(rest):
        c = rest[i]
        if in_string:
            if c == in_string:
                in_string = None
            i += 1
            continue
        if c in ('"', "'"):
            in_string = c
            i += 1
            continue
        if c == ";":
            tail = rest[i + 1 :].strip()
            if tail and not tail.startswith(":") and not tail.startswith("'"):
                errors.append(
                    SyntaxError(
                        line_no,
                        "PRINT: semicolon (;) only allowed at end of PRINT list to suppress newline, not between items. Use comma (,) between items.",
                        line,
                    )
                )
            break
        if c == ",":
            i += 1
            continue
        if c == ":" or c == "'":
            break
        i += 1
    return errors


def check_print_semicolon(line: str, line_no: int) -> List[SyntaxError]:
    """PRINT / '.': semicolon only at end of item list. No ; between items."""
    errors: List[SyntaxError] = []
    content = _strip_rem(line.rstrip("\r\n"))
    if not content.strip():
        return errors
    for raw_seg in _split_colon_statements(content):
        seg = raw_seg.strip()
        if not seg:
            continue
        seg = re.sub(r"^\d+\s+", "", seg).lstrip()
        up = seg.upper()
        if up.startswith("PRINT"):
            rest = seg[5:].lstrip()
            errors.extend(_semicolon_in_print_rest(rest, line_no, line))
        elif seg.startswith("."):
            rest = seg[1:].lstrip()
            errors.extend(_semicolon_in_print_rest(rest, line_no, line))
    return errors


def check_line_format(line: str, line_no: int, is_program_line: bool) -> List[SyntaxError]:
    """Line format: [line_number] statement [: statement ...]. Program lines need line numbers."""
    errors = []
    stripped = line.strip()
    if not stripped:
        return errors
    # Optional line number at start
    if stripped[0].isdigit():
        num_part = re.match(r"^(\d+)\s*", stripped)
        if num_part:
            try:
                n = int(num_part.group(1))
                if n <= 0 or n > 65535:
                    errors.append(SyntaxError(line_no, "Line number must be 1-65535", line))
            except ValueError:
                pass
    elif is_program_line:
        # Direct mode line in a file: no line number. Many .bas files have first line with number.
        pass  # Allow; interpreter accepts both
    return errors


def check_variables(tokens: List[str], line_no: int, line: str) -> List[SyntaxError]:
    """Variables: single letters A-Z only."""
    errors = []
    for i, t in enumerate(tokens):
        if t in KEYWORDS or t in FUNCTIONS or t in HIGH_LOW or t in ("TO", "STEP"):
            continue
        if t in RELOPS or t in "()[],:;=+-*/<>!.":
            continue
        if t.startswith('"') or t.startswith("'") or t.isdigit():
            continue
        if len(t) == 1 and t.isalpha():
            if not ("A" <= t <= "Z"):
                errors.append(SyntaxError(line_no, f"Variable must be A-Z only (single letter): '{t}'", line))
        elif len(t) > 1 and t.isalpha() and t not in KEYWORDS and t not in FUNCTIONS and t not in HIGH_LOW:
            if _is_firmware_glued_for(t) or _is_firmware_glued_next(t):
                continue
            # Multi-letter identifier that isn't a keyword
            errors.append(SyntaxError(line_no, f"Unknown keyword or invalid variable (A-Z only): '{t}'", line))
    return errors


def check_keyword_usage(tokens: List[str], line_no: int, line: str) -> List[SyntaxError]:
    """Check that first token after line number is a known statement keyword or LET/assignment."""
    if not tokens:
        return []
    i = 0
    if tokens[0].isdigit():
        i = 1
    if i >= len(tokens):
        return []
    first = tokens[i]
    if first in KEYWORDS or first == "?" or first == ".":
        return []
    if _is_firmware_glued_for(first):
        return []
    # LET or bare assignment: variable = expr (single letter A-Z)
    if len(first) == 1 and "A" <= first <= "Z":
        return []
    # Unknown keyword
    if first.isalpha():
        return [SyntaxError(line_no, f"Unknown or invalid Tiny BASIC keyword: '{first}'", line)]
    return []


def estimate_program_storage_bytes(lines: List[str]) -> int:
    """
    Bytes the interpreter will use for stored program lines (3-byte line header
    plus full source line per non-blank, non–REM-only line). Matches the tally
    in check_tiny_basic_syntax.
    """
    approx = 0
    for raw in lines:
        line = raw.rstrip("\r\n")
        stripped = line.strip()
        if not stripped:
            continue
        content = _strip_rem(line)
        if not content.strip():
            continue
        approx += _stored_line_record_bytes(line)
    return approx


def format_basic_memory_usage_line(approx_program_bytes: int) -> str:
    """Wording shared with the over-capacity syntax error (minus the 'Program is large' prefix)."""
    return (
        f"approx {approx_program_bytes} bytes of BASIC code; "
        f"BASIC program buffer is {BASIC_PROGRAM_LIMIT_BYTES} bytes"
    )


def check_tiny_basic_syntax(lines: List[str], is_program: bool = True) -> List[SyntaxError]:
    """
    Check a list of lines for Tiny BASIC compliance.
    is_program: True if these are program lines (typically have line numbers).
    """
    errors: List[SyntaxError] = []
    seen_line_numbers: set[int] = set()
    approx_program_bytes = 0

    for idx, raw in enumerate(lines):
        line_no = idx + 1
        line = raw.rstrip("\r\n")
        stripped = line.strip()
        if not stripped:
            continue
        # Strip REM for structure checks
        content = _strip_rem(line)
        if not content.strip():
            continue

        # Duplicate line number: second line replaces first and usually breaks FOR/NEXT, GOTOs
        if stripped and stripped[0].isdigit():
            m = re.match(r"^\s*(\d+)\s*", line)
            if m:
                try:
                    n = int(m.group(1))
                    if n in seen_line_numbers:
                        errors.append(SyntaxError(
                            line_no,
                            f"Duplicate line number {n} (later line replaces earlier; often breaks FOR/NEXT or GOTOs).",
                            line,
                        ))
                    seen_line_numbers.add(n)
                except ValueError:
                    pass

        line_record_bytes = _stored_line_record_bytes(line)
        approx_program_bytes += line_record_bytes

        # Firmware stores per-line LEN in one byte; records >255 bytes cannot be stored.
        if is_program and line_record_bytes > MAX_STORED_LINE_RECORD_BYTES:
            errors.append(
                SyntaxError(
                    line_no,
                    (
                        f"Line is too long for firmware line format: {line_record_bytes} bytes "
                        f"(max {MAX_STORED_LINE_RECORD_BYTES}). Split this line into shorter lines."
                    ),
                    line,
                )
            )

        errors.extend(check_line_format(line, line_no, is_program))
        errors.extend(check_print_semicolon(line, line_no))
        errors.extend(check_delay_terminates_line(content, line_no, line))

        # Use content (code before REM/') for token checks so REM lines aren't flagged
        tokens = _tokenize_for_check(content)
        errors.extend(check_variables(tokens, line_no, line))
        errors.extend(check_keyword_usage(tokens, line_no, line))

    # After scanning all lines, approximate BASIC space usage vs available
    if is_program:
        if approx_program_bytes > BASIC_PROGRAM_LIMIT_BYTES:
            core = format_basic_memory_usage_line(approx_program_bytes)
            errors.append(
                SyntaxError(
                    line_no=1,
                    message=(
                        f"Program is large: {core}. Program may be too big to load."
                    ),
                    line_content=lines[0].rstrip("\r\n") if lines else "",
                )
            )

    return errors
