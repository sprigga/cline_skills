---
name: secs-data-validator
description: Validate SECS-II SML message format. Use when checking SML syntax, verifying item data types (L/A/B/U1/U2/I4/F4 etc.), validating SxFy message headers, analyzing .sml files, or validating SECS log files containing embedded SML. Triggers on phrases like "check SECS format", "validate SML", "SECS-II message correct?", "檢查 SECS log", or "幫我檢查 SML 格式".
---

# SECS-II SML Format Validator

Validate SECS-II SML (SECS Message Language) message structure and data item types.

## Quick Reference

For full SML syntax, item types, and value ranges, see [sml-syntax.md](docs/sml-syntax.md).

### Reference Documentation

- **SML syntax**: [docs/sml-syntax.md](docs/sml-syntax.md) — item types, value ranges, common errors
- **C# implementation** (secs4net): [docs/cs/](docs/cs/) — per-stream message format guides and handler examples
  - Stream 1: `docs/cs/stream1/`, Stream 2: `docs/cs/stream2/`, Stream 5–10: similarly organized
  - Format/codebase conventions: [docs/cs/FORMAT_GUIDE.md](docs/cs/FORMAT_GUIDE.md)
  - Examples: [docs/cs/example/](docs/cs/example/)
- **Python implementation**: [docs/python/](docs/python/) — per-stream message handler guides
  - Streams 1–3, 5–7, 9, 10 covered

## Validation Process

### Case 1: User pastes SML in chat

1. Extract the SML content from the user's message
2. Save to a temp file: `/tmp/sml_input.sml`
3. Run the validator:
   ```bash
   python scripts/validate_sml.py /tmp/sml_input.sml
   ```
4. Report results and explain each error clearly

### Case 2: User asks to validate a file

1. Confirm the file path with the user if unclear
2. Run the validator directly on the file:
   ```bash
   python scripts/validate_sml.py <path/to/file.sml>
   ```
3. Report results and explain each error clearly

### Case 3: User pastes or provides a SECS log

Log files contain extra metadata lines that the validator automatically ignores:

| Ignored line type | Example |
|-------------------|---------|
| Timestamp line | `2026-06-04 11:12:10.4189[TRACE]Send [S2F23] ...` |
| Hex byte dump | `00 01 82 17 00 00 00 00 00 24` |
| Direction/metadata | `S2F23 H2E Wbit(True) DeviceID(1) Systembytes(36)` |
| Empty body marker | `< >` |

Additional log-format normalizations applied automatically:

- **Quoted header**: `'S2F23'W` → treated as `S2F23 W`
- **Header-only messages**: some loggers omit the `.` terminator when there is no body (e.g. S1F17); a new timestamp line implicitly closes the previous message
- **`<Boolean ...>`**: `True` / `False` accepted in addition to `T` / `F`

Validate the same way as Case 1 or Case 2 — no special flags needed:
```bash
python scripts/validate_sml.py <path/to/file.log>
```

### Case 4: Validate multiple files

```bash
for f in path/to/*.sml; do
  echo "=== $f ==="; python scripts/validate_sml.py "$f"; echo
done
```

## Reporting Results

After running the validator, always:

1. **State the verdict clearly**: VALID ✓ or INVALID ✗
2. **For each error**, explain:
   - What the error is
   - Where it is (line number or message context)
   - How to fix it
3. **Show a corrected version** if there are errors

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| Invalid message header | Wrong SxFy format | Use S1–S127, F0–F255 |
| Unknown item type | Typo or unsupported type | Check valid types in sml-syntax.md |
| Value out of range | e.g. `<U1 300>` | U1 is 0–255; use U2 for larger values |
| Missing `>` | Unclosed item bracket | Add closing `>` |
| Missing `.` | No message terminator | Add `.` at end of message |
| Unquoted string | `<A text>` instead of `<A 'text'>` | Wrap strings in single quotes |

## Notes

- The validator script requires Python 3.10+ (uses `list[...]` type hints)
- Script exit code: 0 = valid, 1 = invalid, 2 = file error
- Multiple messages in one file are all validated; errors are reported per message
- **Log file support**: timestamp lines, hex dumps, `SxFy H2E/E2H Wbit(...)` metadata, and `< >` empty-body markers are automatically filtered; quoted headers and header-only messages (no `.`) are normalized before validation
- **Example files**:
  - `templates/example.sml` — pure SML, 4 messages (S1F1, S1F2, S6F11, S2F41)
  - `templates/init-sequence.log` — equipment init sequence, 19 messages (S1F13/14, S1F17/18, S2F33-38, S5F3/4, S1F3/4)
  - `templates/s5f3-alarm.log` — alarm enable/disable, 2 messages (S5F3/4)
