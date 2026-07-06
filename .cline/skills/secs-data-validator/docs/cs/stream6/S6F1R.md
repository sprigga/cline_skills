# S6F1R - Trace Data Send

**Direction:** Sent by Equipment Only

---

## Format

**Message Structure:** Equipment sends trace data for logging/debugging purposes.

### Format Explanation

The **Format** shows the SECS-II message structure:

```
{L:4
[TRID]
[SMPLN]
[STIME]
{L:n
[SV]
}}
```

### Codebase Explanation

This C# code demonstrates how to **receive and parse** an S6F1R message in a host application using the **secs4net** library.

#### Key Components

1. **Message Registration** (lines 25)
   - `sp.MessageTypeAdd(6, 1, ...)` registers a handler for Stream 6, Function 1
   - When the equipment sends S6F1R, `recv_S6F1` is called automatically

2. **Handler Signature** (line 28)
   - `sender` = SecsHost object (the connection receiving the message)
   - `transID` = Transaction ID (used to send a reply with matching ID)
   - `TSN_data` = The SECS message data as a string (format above)

3. **Parsing Logic**
   - **Line 39**: `ListSplit(TSN_data)` breaks the top-level list into 5 elements:
     - `[0]` = "L:4" (list header)
     - `[1]` = TRID element
     - `[2]` = SMPLN element
     - `[3]` = STIME element
     - `[4]` = Inner list of status variables

   - **Lines 41-51**: Extract TRID, SMPLN, STIME by splitting each element
     - Each item splits into `[0]` = type (e.g., "U4:1", "A:n") and `[1]` = value

   - **Lines 52-60**: Loop through status variables (the `{L:n [SV]}` part)
     - `list1.Length` tells us how many SV items exist
     - For each, split and extract the value

4. **Reply** (lines 62-64)
   - If `send_reply == true`, send S6F2 (acknowledge) back to equipment
   - Use same `transID` to correlate request and reply

#### Parsing Workflow
1. Split top-level message → check for "L:4"
2. For each non-list element (TRID, SMPLN, STIME), split and extract value
3. For the variable-length list, loop through all items
4. Send reply if needed

#### Error Handling
- If any validation fails (`ok = false`), the loop breaks
- In production, you'd call `sp.SendS9(7, header)` to send an error message
- The template shows `// TBD create reply` — you need to fill in the reply data

---

- **Outer list `{L:4`** contains exactly 4 elements:
  1. **`[TRID]`** — Trace Request ID (string, A:n) — identifies which trace was requested
  2. **`[SMPLN]`** — Sample Number (U4:1) — increments with each sample in the trace
  3. **`[STIME]`** — Sample Time (A:32) — timestamp of when the sample was taken
  4. **`{L:n ...}`** — A variable-length list of status variables
     - **`[SV]`** — Status Variable value (A:n) — the actual data being traced, repeats `n` times

### SECS Notation Reference
- `{L:4}` = List with exactly 4 elements
- `[ITEMID]` = A single data item
- `{L:n}` = Variable-length list (loop counter `n`)
- `A:n` = ASCII string
- `U4:1` = Unsigned 4-byte integer

---

## Codebase

{L:4
[TRID](http://hume.com/secs/items.html#TRID)

[SMPLN](http://hume.com/secs/items.html#SMPLN)

[STIME](http://hume.com/secs/items.html#STIME)

{L:n

[SV](http://hume.com/secs/items.html#SV)

} }

## Schmoll S80/S50 設備觀察（KA01 Log 2026-03-18）

> **⚠️ Schmoll 實作差異：**
> Schmoll 設備 S6F1 的外層 list 首個欄位為 `DSID`（`UI4`，對應 S2F23 的 DATAID），而非標準 SECS-II 的 `TRID`（ASCII）。
> 且 `{L:n SV}` 的順序與 S2F23 的 SVID 清單一致：
>
> | 順序 | SVID | 類型 | 說明 |
> |------|------|------|------|
> | 1 | 2004 | `ASC` | Clock（時間戳，格式 `YYYYMMDDHHMMSScc`） |
> | 2 | 2008 | `ASC` | MDLN（機台型號，如 `MXY2-200-CCD`）|
> | 3 | 2030 | `UI1` | CONTROLSTATE（如 5=OnlineRemote）|
> | 4 | 2031 | `UI1` | PROCESSSTATE（如 4=Idle/WAIT）|
> | 5 | 2032 | `ASC` | ProcessState 字串（如 `WAIT`）|
>
> **實際 Log 範例（txid=70, SMPLN=1）：**
> ```
> L:4 [ DSID:0, SMPLN:1, STIME:"2026031815391731",
>   L:5 [ "2026031815391731", "MXY2-200-CCD", 5, 4, "WAIT" ] ]
> ```
> 兩筆 S6F1（txid=70, 71）值相同，SMPLN 遞增（1→2），符合 REPGSZ=1 每樣本回報一次的設定。

```
    // S6F1 C# Receive message - add next line to setup
    //SecsHost sp=your_SecsHost;
    sp.MessageTypeAdd( 6, 1, new SecsMsgReceiveDelegate(recv_S6F1));

// receive method
void recv_S6F1(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect L:4 TRID SMPLN STIME {L:n SV}
        // variables for data items and parsing
        string TRID;  	// A:n (varies)  trace request ID
        string SMPLN;  	// U4:1 (varies)  sample number
        string STIME;  	// A:32 (always)  ECV TimeFormat controls format, 0=A:12 YYMMDDHHMMSS, 1=A:16 YYYYMMDDHHMMSScc,2=YYYY-MM-DDTHH:MM:SS.s[s]*{Z|+hh:mm|-hh:mm}
        string SV;  	// A:n (varies)  status variable value
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length != 5 || list0[0] != "L:4") { ok=false; break; }
        string [] list1;
        list1 = SecsPort.ListSplit(list0[1]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { TRID = list1[1];} else { TRID = ""; }
        list1 = SecsPort.ListSplit(list0[2]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { SMPLN = list1[1];} else { SMPLN = ""; }
        list1 = SecsPort.ListSplit(list0[3]);
        if (list1.Length < 1) { ok = false; break; }
        if (!list1[0].StartsWith("A:")) { ok = false; break; }
        if (list1.Length == 2) { STIME = list1[1];} else { STIME = ""; }
        list1 = SecsPort.ListSplit(list0[4]);
        if (list1.Length < 1) { ok=false; break; }
        int n;
        for(n=1; n < list1.Length; n++) {
            string [] list2;
            list2 = SecsPort.ListSplit(list1[n]);
            if (list2.Length < 1) { ok = false; break; }
            if (list2.Length == 2) { SV = list2[1];} else { SV = ""; }
            }
        if (!ok) break;
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(6, 2, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S6F1
```
