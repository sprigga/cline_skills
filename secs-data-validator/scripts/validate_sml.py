#!/usr/bin/env python3
"""SECS-II SML format validator.

Usage:
    python validate_sml.py [file.sml]     # validate a file
    echo "S1F1 W\n." | python validate_sml.py   # validate from stdin
    python validate_sml.py --stdin        # read from stdin explicitly
"""

import re
import sys
from dataclasses import dataclass, field
from typing import Optional


VALID_ITEM_TYPES = {
    "L", "A", "J", "B", "BOOLEAN",
    "U1", "U2", "U4", "U8",
    "I1", "I2", "I4", "I8",
    "F4", "F8",
}

NUMERIC_TYPES = {"U1", "U2", "U4", "U8", "I1", "I2", "I4", "I8", "F4", "F8"}
NUMERIC_RANGES = {
    "U1": (0, 255), "U2": (0, 65535), "U4": (0, 4294967295),
    "U8": (0, 18446744073709551615),
    "I1": (-128, 127), "I2": (-32768, 32767),
    "I4": (-2147483648, 2147483647), "I8": (-9223372036854775808, 9223372036854775807),
}


@dataclass
class ValidationError:
    line: int
    message: str

    def __str__(self):
        return f"  Line {self.line}: {self.message}"


@dataclass
class ValidationResult:
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    message_count: int = 0


class SMLValidator:
    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationError] = []
        self.message_count = 0

    def error(self, line_num: int, msg: str):
        self.errors.append(ValidationError(line_num, msg))

    def warn(self, line_num: int, msg: str):
        self.warnings.append(ValidationError(line_num, msg))

    def validate(self) -> ValidationResult:
        messages = self._split_messages()
        for msg_lines, start_line in messages:
            self._validate_message(msg_lines, start_line)
            self.message_count += 1

        if self.message_count == 0 and not self.errors:
            self.error(1, "No SECS-II messages found")

        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            message_count=self.message_count,
        )

    @staticmethod
    def _is_log_noise(line: str) -> bool:
        """Return True for log lines that are not part of SML content."""
        # Timestamp lines: "2026-06-04 11:12:10.4189[TRACE]..." (may have leading quote)
        if re.match(r'^"?\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line):
            return True
        # Hex byte dump lines: "00 01 82 17 ..."
        if re.match(r'^([0-9A-Fa-f]{2} )+[0-9A-Fa-f]{2}$', line):
            return True
        # Direction/metadata lines: "S2F23 H2E Wbit(True) ..."
        if re.match(r'^S\d+F\d+\s+(H2E|E2H)\s+Wbit', line):
            return True
        # Empty body marker used by some loggers: "< >"
        if re.match(r'^<\s*>$', line):
            return True
        return False

    @staticmethod
    def _is_log_timestamp(line: str) -> bool:
        return bool(re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line))

    def _split_messages(self) -> list[tuple[list[tuple[int, str]], int]]:
        """Split text into individual messages terminated by '.'"""
        messages = []
        current: list[str] = []
        start_line = 1

        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # A new timestamp closes a pending header-only message (no '.' in log)
            if self._is_log_timestamp(stripped) and current:
                messages.append((current, start_line))
                current = []
                start_line = i
            if self._is_log_noise(stripped):
                continue
            # Support '>.' terminator: split into '>' and '.'
            if stripped.endswith(".") and stripped != ".":
                current.append((i, stripped[:-1]))
                stripped = "."
            current.append((i, stripped))
            if stripped == ".":
                if current:
                    messages.append((current, start_line))
                    current = []
                    start_line = i + 1

        if current:
            last_line = current[-1][0] if current else len(self.lines)
            self.error(last_line, "Message missing terminator '.'")
            messages.append((current, start_line))

        return messages

    def _validate_message(self, lines: list[tuple[int, str]], start_line: int):
        if not lines:
            return

        line_num, first = lines[0]
        self._validate_header(line_num, first)

        # Collect item body (excluding header and terminator)
        body_lines = [(ln, l) for ln, l in lines[1:] if l != "."]
        if body_lines:
            full_body = " ".join(l for _, l in body_lines)
            body_start_line = body_lines[0][0]
            self._validate_item_structure(full_body, body_start_line)

    def _validate_header(self, line_num: int, header: str):
        # Normalize log-style quoted header: 'S2F23'W → S2F23 W
        header = re.sub(r"^'(S\d+F\d+)'(W?)$", lambda m: m.group(1) + (" W" if m.group(2) else ""), header, flags=re.IGNORECASE)
        pattern = r"^S(\d+)F(\d+)(\s+W)?\s*$"
        m = re.match(pattern, header, re.IGNORECASE)
        if not m:
            self.error(line_num, f"Invalid message header: '{header}' (expected SxFy or SxFy W)")
            return

        stream = int(m.group(1))
        func = int(m.group(2))

        if stream == 0:
            self.error(line_num, f"Stream 0 is reserved (got S{stream}F{func})")
        elif stream > 127:
            self.error(line_num, f"Stream {stream} out of range (1–127)")

        if func > 255:
            self.error(line_num, f"Function {func} out of range (0–255)")

        if func % 2 == 0 and m.group(3):
            self.warn(line_num, f"S{stream}F{func}: even function (reply) should not have W bit")

    def _validate_item_structure(self, body: str, line_num: int):
        """Tokenize and validate item nesting."""
        tokens = self._tokenize(body)
        if not tokens:
            return
        try:
            pos, _ = self._parse_item(tokens, 0, line_num)
            if pos < len(tokens):
                self.error(line_num, f"Unexpected tokens after item: '{tokens[pos]}'")
        except ValueError as e:
            self.error(line_num, str(e))

    def _tokenize(self, text: str) -> list[str]:
        # Order matters: quoted strings and hex before generic word chars, angle brackets separate
        token_pattern = r"'[^']*'|\"[^\"]*\"|0x[0-9A-Fa-f]+|<|>|\[|\]|[^\s<>\[\]]+"
        return re.findall(token_pattern, text)

    def _parse_item(self, tokens: list[str], pos: int, line_num: int) -> tuple[int, dict]:
        if pos >= len(tokens) or tokens[pos] != "<":
            raise ValueError(f"Expected '<' at token position {pos}, got '{tokens[pos] if pos < len(tokens) else 'EOF'}'")

        pos += 1  # consume '<'

        if pos >= len(tokens):
            raise ValueError("Unexpected end of input after '<'")

        item_type = tokens[pos].upper()
        pos += 1

        if item_type not in VALID_ITEM_TYPES:
            self.error(line_num, f"Unknown item type: '{item_type}' (valid: {', '.join(sorted(VALID_ITEM_TYPES))})")

        # Optional length annotation [n]
        if pos < len(tokens) and tokens[pos] == "[":
            pos += 1  # consume '['
            if pos < len(tokens) and re.match(r"^\d+$", tokens[pos]):
                pos += 1  # consume length value
            if pos < len(tokens) and tokens[pos] == "]":
                pos += 1  # consume ']'
            else:
                self.error(line_num, "Expected ']' to close length annotation")

        values = []
        children = []

        if item_type == "L":
            # Parse child items
            while pos < len(tokens) and tokens[pos] == "<":
                pos, child = self._parse_item(tokens, pos, line_num)
                children.append(child)
        elif item_type == "A" or item_type == "J":
            # String value
            if pos < len(tokens) and tokens[pos] not in (">",):
                val = tokens[pos]
                if (val.startswith("'") and val.endswith("'")) or \
                   (val.startswith('"') and val.endswith('"')):
                    values.append(val[1:-1])
                else:
                    self.error(line_num, f"String value should be quoted: '{val}'")
                pos += 1
        elif item_type == "BOOLEAN":
            while pos < len(tokens) and tokens[pos] != ">":
                val = tokens[pos].upper()
                if val not in ("T", "F", "TRUE", "FALSE", "0", "1"):
                    self.error(line_num, f"Invalid BOOLEAN value: '{tokens[pos]}' (use T or F)")
                values.append(val)
                pos += 1
        elif item_type == "B":
            while pos < len(tokens) and tokens[pos] != ">":
                val = tokens[pos]
                if not re.match(r"^0x[0-9A-Fa-f]+$", val):
                    self.error(line_num, f"Binary value must be hex with 0x prefix: '{val}'")
                values.append(val)
                pos += 1
        elif item_type in NUMERIC_TYPES:
            while pos < len(tokens) and tokens[pos] != ">":
                val = tokens[pos]
                self._validate_numeric(item_type, val, line_num)
                values.append(val)
                pos += 1

        if pos >= len(tokens) or tokens[pos] != ">":
            raise ValueError(f"Expected '>' to close <{item_type}>, got '{tokens[pos] if pos < len(tokens) else 'EOF'}'")
        pos += 1  # consume '>'

        return pos, {"type": item_type, "values": values, "children": children}

    def _validate_numeric(self, item_type: str, value: str, line_num: int):
        try:
            if item_type in ("F4", "F8"):
                float(value)
            else:
                num = int(value)
                if item_type in NUMERIC_RANGES:
                    lo, hi = NUMERIC_RANGES[item_type]
                    if not (lo <= num <= hi):
                        self.error(line_num, f"Value {num} out of range for {item_type} ({lo}–{hi})")
        except ValueError:
            self.error(line_num, f"Invalid numeric value '{value}' for type {item_type}")


def format_result(result: ValidationResult, source: str) -> str:
    lines = [f"Source: {source}"]
    lines.append(f"Messages found: {result.message_count}")

    if result.warnings:
        lines.append(f"\nWarnings ({len(result.warnings)}):")
        lines.extend(str(w) for w in result.warnings)

    if result.valid:
        lines.append("\n✓ VALID — No format errors found")
    else:
        lines.append(f"\n✗ INVALID — {len(result.errors)} error(s) found:")
        lines.extend(str(e) for e in result.errors)

    return "\n".join(lines)


def main():
    use_stdin = "--stdin" in sys.argv
    file_path: Optional[str] = None

    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            file_path = arg
            break

    if file_path:
        try:
            with open(file_path, encoding="utf-8") as f:
                text = f.read()
            source = file_path
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(2)
        except OSError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(2)
    elif use_stdin or not sys.stdin.isatty():
        text = sys.stdin.read()
        source = "stdin"
    else:
        print("Usage: validate_sml.py [file.sml] | --stdin")
        print("  Validates SECS-II SML message format.")
        sys.exit(0)

    validator = SMLValidator(text)
    result = validator.validate()
    print(format_result(result, source))
    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
