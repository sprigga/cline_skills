# S6F3R - Discrete Variable Data Send

**Direction:** Sent by Equipment Only

---

**Note:** Discrete implies event-based data such as analysis completion. Configure supported events using S2F15.

---

## Format

**Message Structure:** Equipment sends discrete variable data triggered by a collection event.

### Format Explanation

The **Format** shows a three-level nested structure:

```
{L:3
[DATAID]
[CEID]
{L:n
{L:2
[DSID]
{L:m
{L:2
[DVNAME]
[DVVAL]
}
}
}
}}
```

### Codebase Explanation

This C# code demonstrates how to **receive and parse** an S6F3R message (discrete variable data) using the **secs4net** library.

#### Key Components

1. **Message Registration** (line 41)
   - `sp.MessageTypeAdd(6, 3, ...)` registers a handler for Stream 6, Function 3

2. **Three-Level Nested Parsing**
   - **Level 0** (line 56): Split top-level list → expect "L:3" with 4 elements
     - `[0]` = "L:3"
     - `[1]` = DATAID element
     - `[2]` = CEID element
     - `[3]` = Inner list of data sets

   - **Level 1** (lines 58-64): Extract DATAID and CEID
     - Each splits to get the actual value

   - **Level 1** (lines 65-92): Loop through data sets (the `{L:n ...}` part)
     - `list1` is the variable-length list, loop from `[1]` to `Length-1`
     - For each `list1[n]`, expect a `{L:2 DSID {L:m ...}}` structure

   - **Level 2** (lines 69-75): Extract DSID from each data set
     - `list2[0]` = "L:2"
     - `list2[1]` = DSID element
     - `list2[2]` = Inner list of variables

   - **Level 2** (lines 76-90): Loop through variables (the `{L:m ...}` part)
     - `list3` is the variable-length list of variable pairs
     - For each `list3[m]`, expect a `{L:2 DVNAME DVVAL}` structure

   - **Level 3** (lines 80-89): Extract DVNAME and DVVAL from each variable pair
     - `list4[0]` = "L:2"
     - `list4[1]` = DVNAME element
     - `list4[2]` = DVVAL element

3. **Reply** (lines 94-96)
   - If `send_reply == true`, send S6F4 (acknowledge) back to equipment

#### Parsing Workflow
1. Split top-level → check for "L:3"
2. Extract DATAID and CEID (scalar items)
3. **Loop 1 (n)**: For each data set
   - Split and extract DSID
4. **Loop 2 (m)**: For each variable within the data set
   - Split each `{L:2 DVNAME DVVAL}` and extract both values

#### Common Patterns
- **DATAID** — Used to correlate multiple messages (e.g., multi-block data)
- **CEID** — The event that triggered this report (configured via S2F15)
- **DSID** — Groups related variables (like a report template)
- **DVNAME/DVVAL** — Individual measured values or status items

#### Error Handling
- Validates each nested list has expected element count
- Breaks on any parse error
- In production, send S9F7 on error

---

- **Outer list `{L:3`** contains exactly 3 elements:
  1. **`[DATAID]`** — Data ID (U4:1) — identifier to correlate related messages
  2. **`[CEID]`** — Collection Event ID (U4:1) — identifies what event triggered this report
  3. **`{L:n ...}`** — Variable-length list of data sets (loop `n`):
     - **`{L:2`** — Each data set is a 2-element list:
       - **`[DSID]`** — Data Set ID (A:n) — identifies the type of data (like a report type)
       - **`{L:m ...}`** — Variable-length list of discrete variables (loop `m`):
         - **`{L:2`** — Each variable is a 2-element list:
           - **`[DVNAME]`** — Variable Name (U4:1) — VID (Variable ID)
           - **`[DVVAL]`** — Variable Value (A:n) — the actual data

### SECS Notation Reference
- `{L:n}` = Fixed-length list with n elements
- `{L:a`, `{L:n}` = Variable-length list (loop counters)
- `[ITEMID]` = A single data item
- `U4:1` = Unsigned 4-byte integer
- `A:n` = ASCII string

---

## Codebase

{L:3
[DATAID](http://hume.com/secs/items.html#DATAID)

[CEID](http://hume.com/secs/items.html#CEID)

{L:n

{L:2

[DSID](http://hume.com/secs/items.html#DSID)

{L:m

{L:2

[DVNAME](http://hume.com/secs/items.html#DVNAME)

[DVVAL](http://hume.com/secs/items.html#DVVAL)

 }

}

 }

} }

```
    // S6F3 C# Receive message - add next line to setup
    //SecsHost sp=your_SecsHost;
    sp.MessageTypeAdd( 6, 3, new SecsMsgReceiveDelegate(recv_S6F3));

// receive method
void recv_S6F3(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect L:3 DATAID CEID {L:n {L:2 DSID {L:m {L:2 DVNAME DVVAL}}}}
        // variables for data items and parsing
        string DATAID;  	// U4:1 (varies)  an identifier to correlate related messages
        string CEID;  	// U4:1 (varies)  collection event identifier, GEM requires type Un
        string DSID;  	// A:n (varies)  data set ID, akin to a report type
        string DVNAME;  	// U4:1 (varies)  data value name, generically a VID, therefore GEM requires Un type
        string DVVAL;  	// A:n (varies)  data value, any format including list
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length != 4 || list0[0] != "L:3") { ok=false; break; }
        string [] list1;
        list1 = SecsPort.ListSplit(list0[1]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { DATAID = list1[1];} else { DATAID = ""; }
        list1 = SecsPort.ListSplit(list0[2]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { CEID = list1[1];} else { CEID = ""; }
        list1 = SecsPort.ListSplit(list0[3]);
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
                if (list4.Length != 3 || list4[0] != "L:2") { ok=false; break; }
                string [] list5;
                list5 = SecsPort.ListSplit(list4[1]);
                if (list5.Length < 1) { ok = false; break; }
                if (list5.Length == 2) { DVNAME = list5[1];} else { DVNAME = ""; }
                list5 = SecsPort.ListSplit(list4[2]);
                if (list5.Length < 1) { ok = false; break; }
                if (list5.Length == 2) { DVVAL = list5[1];} else { DVVAL = ""; }
                }
            if (!ok) break;
            }
        if (!ok) break;
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(6, 4, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S6F3
```
