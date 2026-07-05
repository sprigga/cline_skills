# S6F9R - Formatted Variable Send

**Direction:** Sent by Equipment Only

---

**Note:** Similar to S6F3 (Discrete Variable Data Send) but without variable names. Variable IDs are predefined by the format code (PFCD).

---

## Format

**Message Structure:** Equipment sends formatted variable data with predefined structure (no per-variable names).

### Format Explanation

The **Format** shows a four-element list with two-level nesting:

```
{L:4
[PFCD]
[DATAID]
[CEID]
{L:n
{L:2
[DSID]
{L:m
[DVVAL]
}
}
}}
```

### Codebase Explanation

This C# code demonstrates how to **receive and parse** an S6F9R message (formatted variable data send) using the **secs4net** library.

#### Key Components

1. **Message Registration** (line 37)
   - `sp.MessageTypeAdd(6, 9, ...)` registers a handler for Stream 6, Function 9

2. **Four-Level Nested Parsing**
   - **Level 0** (line 52): Split top-level list → expect "L:4" with 5 elements
     - `[0]` = "L:4"
     - `[1]` = PFCD element
     - `[2]` = DATAID element
     - `[3]` = CEID element
     - `[4]` = Inner list of data sets

   - **Level 1** (lines 55-58): Extract PFCD as binary and convert to integer
     - PFCD determines the variable structure (predefined format)

   - **Level 1** (lines 59-64): Extract DATAID and CEID (scalar items)

   - **Level 1** (lines 65-86): Loop through data sets (the `{L:n ...}` part)
     - `list1` is the variable-length list, loop from `[1]` to `Length-1`

   - **Level 2** (lines 69-75): Extract DSID from each data set
     - Expect `{L:2 DSID {L:m ...}}`

   - **Level 2** (lines 76-84): Loop through values within each data set
     - Each value is a single item `[DVVAL]`
     - Variable names come from PFCD, not from the message

3. **Reply** (lines 88-90)
   - If `send_reply == true`, send S6F10 (acknowledge) back to equipment

#### Parsing Workflow
1. Split top-level → check for "L:4"
2. Extract PFCD (binary), DATAID, and CEID (scalar items)
3. **Loop 1 (n)**: For each data set
   - Split and extract DSID
4. **Loop 2 (m)**: For each value within the data set
   - Split and extract DVVAL

#### Common Patterns
- **PFCD** — Acts as a template selector; variable names are configured separately
- **DATAID** — Used to correlate multiple related messages
- **CEID** — The event that triggered this report
- **DSID** — Report type
- **DVVAL** — Values only (no names in message; names come from PFCD template)

#### Error Handling
- Validates list structures match expected format
- Checks PFCD is binary type (B:1)
- Breaks on parse errors
- In production, send S9F7 on error

---

- **Outer list `{L:4`** contains exactly 4 elements:
  1. **`[PFCD]`** — Predefined Form Code (B:1) — selects which report format to use (determines variable names/IDs)
  2. **`[DATAID]`** — Data ID (U4:1) — identifier to correlate related messages
  3. **`[CEID]`** — Collection Event ID (U4:1) — identifies what event triggered this report
  4. **`{L:n ...}`** — Variable-length list of data sets (loop `n`):
     - **`{L:2`** — Each data set is a 2-element list:
       - **`[DSID]`** — Data Set ID (A:n) — identifies the report type
       - **`{L:m ...}`** — Variable-length list of values (loop `m`):
         - **`[DVVAL]`** — Data Value (A:n) — the actual data (variable names come from PFCD)

### Key Differences from S6F3
| Aspect | S6F3 | S6F9R |
|--------|------|-------|
| **Variable Names** | Included (DVNAME) | Predefined by PFCD |
| **Structure** | {L:3} outer | {L:4} outer |
| **Additional Field** | None | PFCD (format selector) |
| **Use Case** | Dynamic variable lists | Fixed format per PFCD |

### SECS Notation Reference
- `{L:4}` = List with 4 elements
- `[ITEMID]` = A single data item
- `B:1` = Binary item, 1 byte
- `U4:1` = Unsigned 4-byte integer
- `A:n` = ASCII string

---

## Codebase

{L:4
[PFCD](http://hume.com/secs/items.html#PFCD)

[DATAID](http://hume.com/secs/items.html#DATAID)

[CEID](http://hume.com/secs/items.html#CEID)

{L:n

{L:2

[DSID](http://hume.com/secs/items.html#DSID)

{L:m

[DVVAL](http://hume.com/secs/items.html#DVVAL)

}

 }

} }

```
    // S6F9 C# Receive message - add next line to setup
    //SecsHost sp=your_SecsHost;
    sp.MessageTypeAdd( 6, 9, new SecsMsgReceiveDelegate(recv_S6F9));

// receive method
void recv_S6F9(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect L:4 PFCD DATAID CEID {L:n {L:2 DSID {L:m DVVAL}}}
        // variables for data items and parsing
        int PFCD;  	// B:1 (always)  predefined form selector
        string DATAID;  	// U4:1 (varies)  an identifier to correlate related messages
        string CEID;  	// U4:1 (varies)  collection event identifier, GEM requires type Un
        string DSID;  	// A:n (varies)  data set ID, akin to a report type
        string DVVAL;  	// A:n (varies)  data value, any format including list
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length != 5 || list0[0] != "L:4") { ok=false; break; }
        string [] list1;
        list1 = SecsPort.ListSplit(list0[1]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1[0] != "B:1") { ok = false; break; }
        PFCD = sp.BinToInt(list1[1]);
        list1 = SecsPort.ListSplit(list0[2]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { DATAID = list1[1];} else { DATAID = ""; }
        list1 = SecsPort.ListSplit(list0[3]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { CEID = list1[1];} else { CEID = ""; }
        list1 = SecsPort.ListSplit(list0[4]);
        if (list1.Length < 1) { ok=false; break; }
        int n;
        for(n=1; n < list1.Length; n++) {
            string [] list2;
            list2 = SecsPort.ListSplit(list1[n]);
            if (list2.Length != 3 || list2[0] != "L:2") { ok=false; break; }
            string [] list3;
            list3 = SecsPort.ListSplit(list2[1]);
            if (list3.Length < 1) { ok = false; break; }
            if (list3.Length == 2) { DSID = list3[1];} else { DSID = ""; }
            list3 = SecsPort.ListSplit(list2[2]);
            if (list3.Length < 1) { ok=false; break; }
            int m;
            for(m=1; m < list3.Length; m++) {
                string [] list4;
                list4 = SecsPort.ListSplit(list3[m]);
                if (list4.Length < 1) { ok = false; break; }
                if (list4.Length == 2) { DVVAL = list4[1];} else { DVVAL = ""; }
                }
            if (!ok) break;
            }
        if (!ok) break;
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(6, 10, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S6F9
```
