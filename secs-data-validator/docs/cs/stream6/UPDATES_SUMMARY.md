# Stream 6 Documentation Updates Summary

## Overview

Updated all Stream 6 message documentation files (S6F1R–S6F12) with comprehensive **Format** and **Codebase** explanations. Created a unified `FORMAT_GUIDE.md` for Stream 6 that explains SECS-II notation, C# parsing patterns, and the secs4net library conventions.

---

## Files Updated

### Core Documentation

| File | Title | Direction | Description |
|------|-------|-----------|-------------|
| **FORMAT_GUIDE.md** | *NEW* Stream 6 Format and Codebase Guide | Reference | Master guide covering SECS notation, C# patterns, and parsing workflows |
| **README.md** | Stream 6 - Data Collection | Reference | Directory overview (unchanged) |

### Message Pair 1: Trace Data (S6F1-S6F2)

| File | Title | Direction | Status |
|------|-------|-----------|--------|
| **S6F1R.md** | Trace Data Send | Equipment → Host | ✅ Updated with Format explanation and Codebase walkthrough |
| **S6F2.md** | Trace Data Ack | Host → Equipment | ✅ Updated with Format explanation and reply parsing guide |

### Message Pair 2: Discrete Variable Data (S6F3-S6F4)

| File | Title | Direction | Status |
|------|-------|-----------|--------|
| **S6F3R.md** | Discrete Variable Data Send | Equipment → Host | ✅ Updated with three-level parsing explanation |
| **S6F4.md** | Discrete Variable Data Send Ack | Host → Equipment | ✅ Updated with Format explanation and reply parsing |

### Message Pair 3: Multi-block Data (S6F5-S6F6)

| File | Title | Direction | Status |
|------|-------|-----------|--------|
| **S6F5R.md** | Multi-block Data Send Inquire | Equipment → Host | ✅ Updated with use case and parsing workflow |
| **S6F6.md** | Multi-block Grant | Host → Equipment | ✅ Updated with grant code meanings |

### Message Pair 4: Formatted Variable Data (S6F9-S6F10)

| File | Title | Direction | Status |
|------|-------|-----------|--------|
| **S6F9R.md** | Formatted Variable Send | Equipment → Host | ✅ Updated with comparison to S6F3 and PFCD explanation |
| **S6F10.md** | Formatted Variable Ack | Host → Equipment | ✅ Updated with Format explanation and reply parsing |

### Message Pair 5: Event Reports (S6F11-S6F12)

| File | Title | Direction | Status |
|------|-------|-----------|--------|
| **S6F11R.md** | Event Report Send | Equipment → Host | ✅ Updated with three-level parsing and CEID explanation |
| **S6F12.md** | Event Report Ack | Host → Equipment | ✅ Updated with Format explanation and reply parsing |

---

## What Was Added to Each File

### Format Sections

Each message file now includes a **Format** section with:

1. **Message Structure Overview** — 1-2 sentence description of what the message does
2. **Format Explanation** — Detailed breakdown of SECS notation
   - Visual representation of the SECS structure
   - Element-by-element explanation with types and meanings
   - Nesting levels clearly labeled
3. **SECS Notation Reference** — Quick lookup table for notation elements
4. **Comparison Tables** (where relevant) — E.g., S6F9R vs. S6F3 differences

### Codebase Sections

Each message file now includes an enhanced **Codebase** section with:

1. **Codebase Explanation Header** — What the code demonstrates
2. **Key Components** — Numbered breakdown of code sections:
   - Message registration (for requests)
   - Handler signature explanation
   - Step-by-step parsing logic with line number references
   - Reply logic (if applicable)
3. **Parsing Workflow** — High-level summary of steps (for request handlers)
4. **Error Handling** — Validation strategies used in the code
5. **Common Patterns** — Domain-specific guidance (e.g., what CEID means, when DATAID is used)
6. **Common Codes** — Lookup tables (e.g., acknowledge codes, grant codes)

---

## Stream 6 Message Categories

### Data Collection Messages (S6F1-S6F4)
- **S6F1R/S6F2** — Trace data: continuous or periodic samples
- **S6F3R/S6F4** — Discrete event data: variable-length lists of named values

### Multi-block Transfer (S6F5-S6F6)
- **S6F5R/S6F6** — Inquiry/grant for large multi-block messages (SECS-I only; not required for HSMS)

### Formatted Reports (S6F7-S6F10)
- **S6F9R/S6F10** — Similar to S6F3 but with predefined variable structure (PFCD-based)

### Event Reports (S6F11-S6F14)
- **S6F11R/S6F12** — Basic event reports (DATAID + CEID + variable-length report list)
- **S6F13R/S6F14** — Annotated event reports (same structure + annotations)

### Remaining Messages (S6F15-S6F30)
- Request/data message pairs for report requests, notification reports, trace reports, etc.
- Follow similar patterns to S6F1-S6F14

---

## Key Concepts Explained

### SECS Notation
- `{L:n}` = Fixed-length list (n = count)
- `{L:a}`, `{L:n}` = Variable-length list (letter = loop counter)
- `[ITEMID]` = Single data item
- Type codes: `A:n` (ASCII), `B:1` (binary), `U4:1` (unsigned integer), `TF:1` (boolean)

### C# Parsing Patterns
- **ListSplit()** — Breaks SECS structures into arrays
- **Nested loops** — Handle variable-length list loops (a, b, n, m, etc.)
- **Type conversions** — BinToInt(), string parsing
- **Error handling** — Validation at each level, S9F7 for protocol errors

### Common Data Flow Patterns
- **Request/Reply** — Odd functions request, even functions reply
- **DATAID** — Correlates related multi-block messages
- **CEID** — Collection Event ID (what triggered the report)
- **RPTID/DSID** — Report/data set templates
- **Acknowledge Codes** — 0 = OK, 1 = BUSY, 2 = DENY

---

## Files NOT Updated

The following Stream 6 messages exist but were not covered in this update (use FORMAT_GUIDE.md as reference):
- S6F7-S6F8 — Data Transfer Request/Data
- S6F13-S6F14 — Annotated Event Report Send/Ack
- S6F15-S6F30 — Request/Data pairs for reports, tracing, notification, etc.

Future updates can use the same pattern as S6F1-S6F12.

---

## How to Use This Documentation

### For Developers

1. **Start with FORMAT_GUIDE.md** — Understand SECS notation and C# library basics
2. **Read the specific message file** (e.g., S6F11R.md)
   - Format section shows what data to expect
   - Codebase section shows how to parse it
3. **Reference the code examples** — Copy and adapt the C# templates to your implementation

### For System Integrators

1. **README.md** — See which functions do what
2. **Format section of each message** — Understand the message structure
3. **Common Patterns** sections — Learn when to use each message type

### For Reviewers / QA

1. **Check FORMAT_GUIDE.md** for standard notation and patterns
2. **Compare implementations** against the provided code examples
3. **Use Common Patterns sections** to identify bugs or deviations

---

## Standards Applied

All updates follow the conventions established in `/home/polo/secs/docs/secs/cs/FORMAT_GUIDE.md` (Stream 2 documentation), adapted for Stream 6 specifics:

- SECS notation explained inline
- C# secs4net library patterns
- Line-by-line code walkthroughs
- Error handling guidance
- Practical examples with comments

---

## Testing/Verification

Run the following to verify all files were updated:

```bash
# Check all S6Fx files have "## Format" and "## Codebase" sections
grep -l "## Format" docs/secs/cs/stream6/S6F*.md | wc -l
# Expected: 12 (S6F1R through S6F12)

# Check FORMAT_GUIDE.md exists
ls -l docs/secs/cs/stream6/FORMAT_GUIDE.md

# View updated files
ls -lh docs/secs/cs/stream6/*.md
```

---

## Next Steps (Optional Future Work)

- Update remaining Stream 6 messages (S6F7-S6F30) following the same pattern
- Create similar FORMAT_GUIDE.md files for other streams (S1, S3, S5, etc.)
- Add visual diagrams for complex nested structures
- Create a master SECS-II notation quick-reference guide
