# S6F5R - Multi-block Data Send Inquire

**Direction:** Sent by Equipment Only

---

**Note:** Multi-block sending is required for SECS-I with S6F3, S6F9, S6F11, S6F13. Not required for HSMS.

---

## Format

**Message Structure:** Equipment inquires whether the host can accept a multi-block data transfer.

### Format Explanation

The **Format** shows a two-element list:

```
{L:2
[DATAID]
[DATALENGTH]
}
```

### Codebase Explanation

This C# code demonstrates how to **receive and parse** an S6F5R message (multi-block data send inquire) using the **secs4net** library.

#### Key Components

1. **Message Registration** (line 19)
   - `sp.MessageTypeAdd(6, 5, ...)` registers a handler for Stream 6, Function 5

2. **Parsing Logic**
   - **Line 31**: `ListSplit(TSN_data)` breaks the message into 3 elements:
     - `[0]` = "L:2" (list header)
     - `[1]` = DATAID element
     - `[2]` = DATALENGTH element

   - **Lines 34-36**: Extract DATAID by splitting and accessing element `[1]`
   - **Lines 37-39**: Extract DATALENGTH by splitting and accessing element `[1]`

3. **Reply** (lines 40-42)
   - If `send_reply == true`, send S6F6 (grant/deny permission) back to equipment
   - Use same `transID` to correlate request and reply

#### Parsing Workflow
1. Split top-level message → check for "L:2" with 3 array elements
2. Extract DATAID and DATALENGTH from each element
3. Send S6F6 reply with grant code

#### Use Case
- Equipment sends this inquiry before sending a large multi-block message
- Host responds with S6F6 (grant code: 0 = allow, 1 = busy, 2 = deny)
- If granted (0), equipment sends the full data in blocks
- DATAID is used to correlate the inquiry with subsequent block transfers

---

- **List `{L:2`** contains exactly 2 elements:
  1. **`[DATAID]`** — Data ID (U4:1) — identifier to correlate related messages (references prior messages like S6F1, S6F3, etc.)
  2. **`[DATALENGTH]`** — Data Length (U4:1) — total size in bytes of the complete multi-block message

### SECS Notation Reference
- `{L:2}` = List with 2 elements
- `[ITEMID]` = A single data item
- `U4:1` = Unsigned 4-byte integer

---

## Codebase

```
    // S6F5R C# Receive message - add next line to setup
    //SecsHost sp=your_SecsHost;
    sp.MessageTypeAdd( 6, 5, new SecsMsgReceiveDelegate(recv_S6F5R));

// receive method
void recv_S6F5R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect L:2 DATAID DATALENGTH
        // variables for data items and parsing
        string DATAID;  	// U4:1 (varies)  an identifier to correlate related messages
        string DATALENGTH;  	// U4:1 (varies)  total bytes of the message body
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length != 3 || list0[0] != "L:2") { ok=false; break; }
        string [] list1;
        list1 = SecsPort.ListSplit(list0[1]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { DATAID = list1[1];} else { DATAID = ""; }
        list1 = SecsPort.ListSplit(list0[2]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { DATALENGTH = list1[1];} else { DATALENGTH = ""; }
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(6, 6, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S6F5R
```
