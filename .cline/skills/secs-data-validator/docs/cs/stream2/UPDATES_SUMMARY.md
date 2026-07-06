# S2F31–S2F42 Documentation Updates Summary

## Overview
All 9 message documentation files in `/docs/secs/cs/stream2/` have been updated with detailed explanations of the **Format** and **Codebase** sections.

## Files Updated

1. **S2F31R.md** — Date and Time Set Request
   - Explains single-item format `[TIME]`
   - Handler registration and parsing workflow
   - Error handling pattern

2. **S2F32.md** — Date and Time Set Acknowledge
   - Explains binary scalar reply format `[TIACK]`
   - Host-side reply parsing (as opposed to equipment-side receiver)
   - Return code checking

3. **S2F33R.md** — Define Report
   - Three-level nested list structure with dual loops
   - Explains `{L:2 [DATAID] {L:a {L:2 [RPTID] {L:b [VID]}}}}` notation
   - Nested loop parsing algorithm
   - Validation at each nesting level

4. **S2F34.md** — Define Report Acknowledge
   - Binary scalar reply acknowledgment
   - Host-side send-and-wait pattern
   - Error code interpretation

5. **S2F35R.md** — Link Event Report
   - Three-level nested structure (similar to S2F33)
   - Event-to-report linking semantics
   - Dual loop correspondence to message format

6. **S2F36.md** — Link Event Report Acknowledge
   - Binary scalar acknowledgment pattern
   - Consolidation of acknowledgment message pattern

7. **S2F37R.md** — Enable/Disable Event Report
   - Two-level structure with single loop
   - Boolean flag (CEED) for enable/disable semantics
   - Simpler parsing than three-level structures

8. **S2F38.md** — Enable/Disable Event Report Acknowledge
   - Binary scalar acknowledgment
   - Links back to S2F37 semantics

9. **S2F41R.md** — Host Command Send
   - Two-level structure with fixed L:2 parameter pairs
   - Command name + variable parameter list
   - Difference from double-variable-list structures

10. **S2F42.md** — Host Command Acknowledge
    - Two-level structure (reply to S2F41)
    - Sparse error reporting (only failed parameters listed)
    - Overall command code + per-parameter codes

## Additional Resource

**FORMAT_GUIDE.md** — Comprehensive reference document covering:
- SECS notation elements (`[ITEMID]`, `{L:n}`, type codes)
- Common parsing methods (ListSplit, BinToInt, etc.)
- Full parsing workflow
- Handler signatures and patterns
- Item type reference table

## Key Concepts Explained

### Format vs. Codebase Distinction
- **Format**: Describes the logical SECS-II message structure using standard notation
- **Codebase**: Shows how the secs4net C# library parses and creates these messages using string-based type codes

### Parsing Patterns Identified

1. **Simple scalar** (S2F31R, S2F32, S2F34, S2F36, S2F38):
   - Single item, minimal validation
   - Straightforward type checking and value extraction

2. **Two-level lists** (S2F37R, S2F41R):
   - Outer L:2 or fixed structure with a variable-length inner list
   - One loop counter for iteration

3. **Three-level nested** (S2F33R, S2F35R):
   - Complex nested structure with two variable-length loop counters
   - Recursive ListSplit calls for each nesting level
   - Dual `for` loops in code

### Common Library Elements
- `SecsPort.ListSplit()` — Parse list structure at each nesting level
- `sp.BinToInt()` — Convert binary items to integers
- `sp.SendReply()` — Send reply messages
- `sp.SendS9()` — Send error messages
- Message handler registration pattern with `MessageTypeAdd()`

## How to Use These Updates

1. **Developers**: Refer to the relevant message file when implementing handlers for that message type. The explanation shows exactly how the format maps to code.
2. **Testers**: Use the format section to understand what structure each message should have.
3. **Architects**: Review FORMAT_GUIDE.md for the overall SECS notation and parsing philosophy.
4. **Reference**: Use UPDATES_SUMMARY.md (this file) to find which file covers which pattern.

