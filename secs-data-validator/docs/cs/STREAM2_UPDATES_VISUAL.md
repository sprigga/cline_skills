# Stream 2 (S2F31–S2F42) Documentation Updates — Visual Summary

## What Was Done

Updated 9 documentation files in `docs/secs/cs/stream2/` with detailed explanations mapping SECS format structures to C# implementation code using the **secs4net** library.

## Files Updated

```
docs/secs/cs/stream2/
├── S2F31R.md ✓ (Date and Time Set Request)
├── S2F32.md  ✓ (Date and Time Set Acknowledge)
├── S2F33R.md ✓ (Define Report)
├── S2F34.md  ✓ (Define Report Acknowledge)
├── S2F35R.md ✓ (Link Event Report)
├── S2F36.md  ✓ (Link Event Report Acknowledge)
├── S2F37R.md ✓ (Enable/Disable Event Report)
├── S2F38.md  ✓ (Enable/Disable Event Report Acknowledge)
├── S2F41R.md ✓ (Host Command Send)
└── S2F42.md  ✓ (Host Command Acknowledge)
```

## New Reference Documents

```
docs/secs/cs/
├── FORMAT_GUIDE.md (comprehensive reference)
└── stream2/
    ├── UPDATES_SUMMARY.md (summary of changes)
    ├── README.md (updated with links to guides)
    └── [message files with enhanced documentation]
```

## What Each Updated File Now Contains

### Before (Original Structure)
```markdown
# S2FxxY - Message Name

**Direction:** Host/Equipment Only

Format:
[ITEM_NOTATION]

Code:
C# code example
```

### After (Enhanced Structure)
```markdown
# S2FxxY - Message Name

**Direction:** Host/Equipment Only

Format:
[ITEM_NOTATION]

Code:
C# code example

## Understanding Format and Codebase

### Format
- Explanation of SECS notation used
- Structure breakdown
- List nesting explanation

### Codebase (C# / secs4net)
- Step-by-step parsing explanation
- Library method usage
- Validation patterns
- Key semantic information
```

## Message Patterns Explained

### Pattern 1: Simple Scalar (S2F31R, S2F32, S2F34, S2F36, S2F38)
```
Format:   [ITEM]
Pattern:  Single value (no nesting)
Code:     Type check → value extraction → use/reply
Parsing:  One ListSplit() call
```

### Pattern 2: Two-Level List (S2F37R, S2F41R)
```
Format:   {L:2 [ITEM] {L:n [ITEM2]}}
Pattern:  Outer structure + variable inner list
Code:     Extract outer item, loop through inner items
Parsing:  Two ListSplit() calls with one loop
```

### Pattern 3: Three-Level Nested (S2F33R, S2F35R)
```
Format:   {L:2 [ITEM] {L:a {L:2 [ITEM2] {L:b [ITEM3]}}}}
Pattern:  Complex nested with dual variable lists
Code:     Outer → first loop → nested structure → second loop
Parsing:  Multiple ListSplit() calls with nested loops
```

## Key Documentation Features

### FORMAT_GUIDE.md
- **SECS Notation Reference** — All notation elements explained
- **C# Library Reference** — All common parsing methods
- **Parsing Workflow** — Step-by-step process
- **Type Code Table** — Item type reference
- **Summary Table** — Format vs. Codebase comparison

### UPDATES_SUMMARY.md
- **File-by-file overview** — What each file covers
- **Pattern identification** — Which files demonstrate which patterns
- **Usage guide** — How to use these documents
- **Concept summary** — Key parsing concepts

### Individual Message Files
Each message file now includes:
1. **Format explanation** — What the structure notation means
2. **Codebase walkthrough** — How the C# code implements parsing
3. **Key patterns** — Parsing algorithms and validation
4. **Semantic context** — What the message does in the protocol
5. **Cross-references** — How this message relates to others

## Example: S2F33R Explanation Structure

```
Format Section:
┌─────────────────────────────────────────────┐
│ Shows the nested list structure              │
│ {L:2 DATAID {L:a {L:2 RPTID {L:b VID}}}}    │
│ Explains each nesting level and loop counter│
└─────────────────────────────────────────────┘
           ↓
Codebase Section:
┌──────────────────────────────────────────────┐
│ Shows how secs4net parses this structure:    │
│ 1. ListSplit(TSN_data) for level 0          │
│ 2. Extract DATAID from list0[1]             │
│ 3. Loop through reports with counter 'a'    │
│ 4. ListSplit() for each nested L:2          │
│ 5. Loop through variables with counter 'b'  │
│ 6. Extract VID values                       │
│ 7. Error handling on validation failure     │
└──────────────────────────────────────────────┘
           ↓
Understanding Section:
┌──────────────────────────────────────────────┐
│ Explains the mapping between Format and Code │
│ - Notation ↔ Type codes                     │
│ - Structure ↔ Parsing calls                 │
│ - Loop counters ↔ for loop nesting          │
│ - Validation ↔ Error handling               │
└──────────────────────────────────────────────┘
```

## How to Navigate

1. **Learning SECS concepts**: Start with `FORMAT_GUIDE.md`
2. **Implementing a handler**: Go to the specific message file (e.g., `S2F33R.md`)
3. **Understanding patterns**: Refer to `UPDATES_SUMMARY.md`
4. **Quick reference**: Use the message table in `README.md`

## Key Insights Documented

- **Format notation** (`[ITEM]`, `{L:n}`, type codes) maps directly to C# string representations
- **ListSplit()** is the fundamental operation for parsing SECS structures
- **Nested loops** in code correspond to nested variable-length lists in format
- **Type validation** (e.g., `list0[0] == "B:1"`) is critical before value extraction
- **S9F7 error messages** are sent when parsing validation fails
- **Request/reply patterns** differ between Host and Equipment sides, but parsing is identical

## Files Created

```
NEW FILES:
  docs/secs/cs/FORMAT_GUIDE.md              (comprehensive reference)
  docs/secs/cs/stream2/UPDATES_SUMMARY.md   (change summary)

MODIFIED FILES:
  docs/secs/cs/stream2/README.md
  docs/secs/cs/stream2/S2F31R.md
  docs/secs/cs/stream2/S2F32.md
  docs/secs/cs/stream2/S2F33R.md
  docs/secs/cs/stream2/S2F34.md
  docs/secs/cs/stream2/S2F35R.md
  docs/secs/cs/stream2/S2F36.md
  docs/secs/cs/stream2/S2F37R.md
  docs/secs/cs/stream2/S2F38.md
  docs/secs/cs/stream2/S2F41R.md
  docs/secs/cs/stream2/S2F42.md
```

