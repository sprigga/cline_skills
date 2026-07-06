# Stream 6 Format and Codebase Guide

Stream 6 messages are used for **data collection**, **trace data**, **event reports**, and **notification reports**. This guide explains how to interpret the **Format** section and implement the corresponding C# **Codebase** examples using the **secs4net** library.

---

## Format Section Explanation

The **Format** section describes the SECS-II message structure using standard SECS notation.

### Key Notation Elements

| Notation | Meaning | Example |
|----------|---------|---------|
| `[ITEMID]` | A single SECS item with a unique identifier name | `[TRID]`, `[DATAID]`, `[CEID]` |
| `{L:n}` | A list containing exactly `n` items, where `n` is a fixed number | `{L:2` starts a list with 2 elements |
| `{L:a`, `{L:b`, `{L:n}` | A variable-length list where the letter (a, b, n, etc.) represents a loop counter | `{L:a` indicates the list repeats multiple times |
| `}` | Closes a list structure | Paired with opening `{` |

### Format Examples from Stream 6

**Simple Structure (S6F2 - Trace Data Ack):**
```
[ACKC6]
```
- Just a single ACKC6 item (acknowledge code)

**Two-level Structure (S6F1R - Trace Data Send):**
```
{L:4
[TRID]
[SMPLN]
[STIME]
{L:n
[SV]
}}
```
- Outer list with 4 elements:
  1. TRID (trace request ID)
  2. SMPLN (sample number)
  3. STIME (sample time)
  4. A variable-length list (looping `n` times) of status variables

**Three-level Structure (S6F11R - Event Report Send):**
```
{L:3
[DATAID]
[CEID]
{L:a
{L:2
[RPTID]
{L:b
[V]
}
}
}}
```
- Outermost list with 3 elements:
  1. DATAID (data identifier)
  2. CEID (collection event ID)
  3. A variable-length list (loop `a`) of reports, each containing:
     - A report ID
     - A variable-length list (loop `b`) of values

### Item Types in SECS

| Type Code | Meaning | Example |
|-----------|---------|---------|
| `L:n` | List with n items | `L:3`, `L:2` |
| `A:n` | ASCII string (length n or variable) | `A:12`, `A:32`, `A:n` |
| `B:n` | Binary item | `B:1` |
| `U4:n` | Unsigned 4-byte integer | `U4:1` |
| `TF:1` | Boolean (true/false) | `TF:1` |

---

## Codebase Section Explanation

The **Codebase** section provides C# implementation examples using the **secs4net** library, a .NET SECS-II/HSMS-SS/GEM protocol stack.

### Key C# Components

#### Message Registration (for receive handlers)
```csharp
sp.MessageTypeAdd(6, 1, new SecsMsgReceiveDelegate(recv_S6F1));
```
- `sp` = `SecsPort` or `SecsHost` connection object
- `6, 1` = Stream 6, Function 1
- `SecsMsgReceiveDelegate` = Delegate type for message handlers

#### Handler Signature
```csharp
void recv_SxFy(object sender, int stream, int function, 
               bool send_reply, int transID, string TSN_data, string header)
```
- `sender` = The SecsPort/SecsHost object (cast as needed)
- `stream`, `function` = Message identifiers
- `send_reply` = Whether a reply is expected (true if the sender wants a response)
- `transID` = Transaction ID for request/reply correlation
- `TSN_data` = The message data as a string in SECS item list notation
- `header` = Raw HSMS header bytes (used for S9 error replies)

#### Common Parsing Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `SecsPort.ListSplit(TSN_data)` | Splits a SECS list structure into array elements | `string[] list0 = SecsPort.ListSplit(TSN_data);` |
| `SecsPort.ListSplit(listElement)` | Recursively parse nested lists | `string[] list1 = SecsPort.ListSplit(list0[1]);` |
| `sp.BinToInt(binString)` | Convert binary item to integer | `int value = sp.BinToInt(list0[1]);` |
| `sp.SendReply(stream, fn, transID, data)` | Send a reply message | `sp.SendReply(6, 2, transID, reply);` |
| `sp.SendS9(7, header)` | Send S9F7 error (illegal/unsupported data) | `sp.SendS9(7, header);` on parse error |

### Parsing Workflow

1. **Split the incoming message**: `ListSplit(TSN_data)` breaks the message into components
2. **Validate structure**: Check array length and item types (e.g., `"L:4"`, `"B:1"`, `"A:n"`)
3. **Extract values**: Access list elements by index and parse to appropriate types
4. **Handle nested lists**: Recursively call `ListSplit()` for each nested list, use loops for variable-length lists
5. **Validate or error**: Send S9F7 if parsing fails
6. **Send reply**: Use `SendReply()` if the request expects a response (`send_reply == true`)

### Example Parsing (S6F11R - Event Report Send)

Message format: `{L:3 DATAID CEID {L:a {L:2 RPTID {L:b V}}}}`

```csharp
// Level 0: Split top-level list
list0 = SecsPort.ListSplit(TSN_data);  // [0]="L:3", [1]=DATAID, [2]=CEID, [3]=inner list

// Level 1: Extract DATAID and CEID
list1 = SecsPort.ListSplit(list0[1]);  // Parse DATAID item
DATAID = list1[1];                      // Get the actual value

list1 = SecsPort.ListSplit(list0[2]);  // Parse CEID item
CEID = list1[1];

// Level 1: Process inner list (loop a) - variable-length list of reports
list1 = SecsPort.ListSplit(list0[3]);  // Get the variable-length list
for(a=1; a < list1.Length; a++) {      // Loop through each report (start at [1], [0] is "L:a")
    // Level 2: Each report is {L:2 RPTID {L:b V}}
    list2 = SecsPort.ListSplit(list1[a]);
    
    // Level 2: Extract RPTID
    list3 = SecsPort.ListSplit(list2[1]);
    RPTID = list3[1];
    
    // Level 2: Process inner list (loop b) - variable-length list of values
    list3 = SecsPort.ListSplit(list2[2]);  // Get the variable-length list
    for(b=1; b < list3.Length; b++) {      // Loop through each value
        // Level 3: Each value item
        list4 = SecsPort.ListSplit(list3[b]);
        V = list4[1];  // Extract value
    }
}
```

### Common Stream 6 Patterns

#### Request/Reply Pattern
- **Odd functions** (S6F1R, S6F3R, S6F11R, etc.) are sent by equipment (requests)
- **Even functions** (S6F2, S6F4, S6F12, etc.) are sent by the host (replies/acknowledgments)
- Use `send_reply` flag to determine if a response is needed

#### Data Collection Pattern
Messages group data by:
- `DATAID` — identifier to correlate related messages
- `CEID` — collection event ID (what triggered the report)
- Variable-length lists of values or reports (loop counters like `a`, `b`, `n`)

#### Acknowledge Pattern
Simple reply messages (S6F2, S6F4, S6F6, S6F10, etc.) often contain just:
- `ACKC6` — acknowledge code (B:1, binary, 0 = ok)
- Parsed by checking if first element is `"B:1"`, then converting to integer

---

## Summary: Format vs. Codebase

| Aspect | Format | Codebase |
|--------|--------|----------|
| **Purpose** | Describes what the message should contain (data structure) | Shows how to implement message handling in C# |
| **Notation** | SECS item notation (`[ID]`, `{L:n}`, type codes) | C# syntax with secs4net library calls |
| **Usage** | Reference for equipment/system specifications | Implementation guide for developers |
| **Key Info** | Message structure, nesting, item types, loop counts | Parsing logic, validation, error handling, reply logic |
