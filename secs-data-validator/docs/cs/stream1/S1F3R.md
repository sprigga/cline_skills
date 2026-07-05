# S1F3R - Selected Equipment Status Request

**Direction:** Sent by Host Only

---

| **S1F3R** | Selected Equipment Status Request | Sent by Host Only |

## Format

```
{L:n
[SVID](http://hume.com/secs/items.html#SVID)}
```

### Format Explanation

- **`L:n`** — A list containing `n` elements, where `n` is the number of status variable IDs being requested
- **`SVID`** — Status Variable ID in `U4:1` format (4-byte unsigned integer), identifying which equipment status variable to query. The number of SVID elements in the list determines `n`.

### Purpose

**S1F3R** is sent by the Host to request the current values of specific equipment status variables. The message contains a list of one or more SVIDs, telling the Equipment which status variables to report. The Equipment replies with **S1F4** (Selected Equipment Status Data) containing the actual value for each requested SVID.

#### Example

If the Host wants to query two status variables (ID 1001 and 1002):
- Message content: `L:2 [U4:1001] [U4:1002]`
- Equipment replies with **S1F4** (Selected Equipment Status Data) containing the actual value for each SVID

### Codebase Pattern

> The C# code below follows the standard `secs4net` receive-handler pattern:
> - `SecsPort.ListSplit(TSN_data)` parses the TSN (Type-Size-Name) list structure into a string array. The first element is the list header (e.g., `L:2`), and subsequent elements are the list items.
> - A `while(ok)` / `break` loop is used for early-exit error handling — any validation failure sets `ok = false` and breaks out.
> - The outer `list0` holds the top-level list. `list0[0]` is the list header (`L:n`), and `list0[1..n]` are the SVID elements.
> - Each SVID element is re-parsed with `ListSplit()` into `list1`. `list1[0]` is the type tag (e.g., `U4:1`), and `list1[1]` is the value (e.g., `1001`).
> - On successful parse, the handler calls `sp.SendReply(1, 4, ...)` to send the S1F4 reply.
> - On any parse failure, `sp.SendS9(7, header)` sends an S9F7 (illegal data) error back to the Host.

```
    // S1F3R C# Receive message - add next line to setup
    //SecsPort sp=your_SecsPort;
    sp.MessageTypeAdd( 1, 3, new SecsMsgReceiveDelegate(recv_S1F3R));

// receive method
void recv_S1F3R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsPort sp = (SecsPort)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect L:n SVID
        // variables for data items and parsing
        string SVID;  	// U4:1 (varies)  status variable ID
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length < 1) { ok=false; break; }
        int n;
        for(n=1; n < list0.Length; n++) {
            string [] list1;
            list1 = SecsPort.ListSplit(list0[n]);
            if (list1.Length < 1) { ok = false; break; }
            if (list1.Length == 2) { SVID = list1[1];} else { SVID = ""; }
            }
        if (!ok) break;
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(1, 4, transID, reply);
            }
        return;
        } // end while(ok)
    // bad data
    sp.SendS9(7, header);
    } // end recv_S1F3R
```

|     |     |     |
| --- | --- | --- |
