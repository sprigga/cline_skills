# S2F31-S2F42 Format and Codebase Guide

## Format Section Explanation

The **Format** section describes the SECS-II message structure using standard SECS notation:

### Key Notation Elements

| Notation | Meaning | Example |
|----------|---------|---------|
| `[ITEMID]` | A single SECS item with a unique identifier name (e.g., `[TIME]`, `[DATAID]`) | `[DATAID]` represents a data ID item |
| `{L:n}` | A list containing `n` items, where `n` can be a number or a variable letter | `{L:2` starts a list with 2 elements |
| `{L:a` or `{L:n}` | A variable-length list where `a`, `b`, `n`, etc. represent loop counters | `{L:a` indicates the list can repeat multiple times |
| `}` | Closes a list structure | Paired with opening `{` |

### Format Examples from S2F31–S2F42

**Simple Structure (S2F31R):**
```
[TIME]
```
- Just a single TIME item

**Two-level Structure (S2F37R):**
```
{L:2
[CEED]
{L:n
[CEID]
}}
```
- Outer list with 2 elements:
  1. A CEED item
  2. A variable-length list of CEID items (repeating `n` times)

**Three-level Structure (S2F33R):**
```
{L:2
[DATAID]
{L:a
{L:2
[RPTID]
{L:b
[VID]
}
}
}}
```
- Outermost list with 2 elements:
  1. DATAID
  2. A variable-length list of reports (loop `a`), each containing:
     - A report ID
     - A variable-length list of variables (loop `b`)

---

## Codebase Section Explanation

The **Codebase** section provides C# implementation examples using the **secs4net** library. This is a .NET SECS-II/HSMS-SS/GEM protocol stack.

### Key C# Components

#### Message Registration (for receive handlers)
```csharp
sp.MessageTypeAdd(2, 31, new SecsMsgReceiveDelegate(recv_S2F31R));
```
- `sp` = `SecsPort` or `SecsHost` connection object
- `2, 31` = Stream 2, Function 31
- `SecsMsgReceiveDelegate` = Delegate type for message handlers

#### Handler Signature
```csharp
void recv_SxFy(object sender, int stream, int function, 
               bool send_reply, int transID, string TSN_data, string header)
```
- `sender` = The SecsPort/SecsHost object (cast as needed)
- `stream`, `function` = Message identifiers
- `send_reply` = Whether a reply is expected
- `transID` = Transaction ID for request/reply correlation
- `TSN_data` = The message data as a string (SECS item list notation)
- `header` = Raw HSMS header bytes

#### Common Parsing Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `SecsPort.ListSplit(TSN_data)` | Splits a list structure into elements | `string[] list0 = SecsPort.ListSplit(TSN_data);` |
| `SecsPort.ListSplit(listElement)` | Recursively parse nested lists | `string[] list1 = SecsPort.ListSplit(list0[1]);` |
| `sp.BinToInt(binString)` | Convert binary item to integer | `int value = sp.BinToInt(list0[1]);` |
| `sp.SendReply(stream, fn, transID, data)` | Send a reply message | `sp.SendReply(2, 32, transID, reply);` |
| `sp.SendS9(7, header)` | Send S9F7 error (illegal data) | `sp.SendS9(7, header);` on parse error |

### Parsing Workflow

1. **Split the incoming message**: `ListSplit(TSN_data)` breaks the message into components
2. **Validate structure**: Check array length and item types (e.g., `"L:2"`, `"B:1"`, `"A:n"`)
3. **Extract values**: Access list elements and parse to appropriate types
4. **Handle nested lists**: Recursively call `ListSplit()` for each nested list
5. **Validate or error**: Send S9F7 if parsing fails
6. **Send reply**: Use `SendReply()` if the request expects a response

### Item Types in SECS

| Type Code | Meaning | Example |
|-----------|---------|---------|
| `L:n` | List with n items | `L:2` |
| `A:n` | ASCII string (length n or variable) | `A:12`, `A:n` |
| `B:n` | Binary item | `B:1` |
| `U4:n` | Unsigned 4-byte integer | `U4:1` |
| `TF:1` | Boolean (true/false) | `TF:1` |

### Example Parsing (S2F33R - Define Report)

```csharp
// Message: {L:2 DATAID {L:a {L:2 RPTID {L:b VID}}}}

// Level 0: Split top-level list
list0 = SecsPort.ListSplit(TSN_data);  // [0]="L:2", [1]=DATAID element, [2]=inner list

// Level 1: Extract DATAID
list1 = SecsPort.ListSplit(list0[1]);  // Parse DATAID item
DATAID = list1[1];                      // Get the actual value

// Level 1: Process inner list (loop a)
list1 = SecsPort.ListSplit(list0[2]);  // Get variable-length list
for(a=1; a < list1.Length; a++) {      // Loop through each report (starting at [1])
    // Level 2: Each report is {L:2 RPTID {L:b VID}}
    list2 = SecsPort.ListSplit(list1[a]);
    // ... continue parsing nested structures
}
```

---

## Summary: Format vs. Codebase

| Aspect | Format | Codebase |
|--------|--------|----------|
| **Purpose** | Describes what the message should contain (data structure) | Shows how to implement message handling in C# |
| **Notation** | SECS item notation (`[ID]`, `{L:n}`, type codes) | C# syntax with secs4net library calls |
| **Usage** | Reference for equipment/system specifications | Implementation guide for developers |
| **Key Info** | Message structure, nesting, item types, loop counts | Parsing logic, validation, error handling |

