# S5F9[R] - Exception Post Notify

**Direction:** Sent by Equipment Only

**Comment:** see E41

---

Format:

{L:5
[TIMESTAMP](http://hume.com/secs/items.html#TIMESTAMP)

[EXID](http://hume.com/secs/items.html#EXID)

[EXTYPE](http://hume.com/secs/items.html#EXTYPE)

[EXMESSAGE](http://hume.com/secs/items.html#EXMESSAGE)

{L:n

[EXRECVRA](http://hume.com/secs/items.html#EXRECVRA)

} }

```csharp
    // S5F9 C# Receive message - add next line to setup
    //SecsHost sp=your_SecsHost;
    sp.MessageTypeAdd( 5, 9, new SecsMsgReceiveDelegate(recv_S5F9));

// receive method
void recv_S5F9(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect L:5 TIMESTAMP EXID EXTYPE EXMESSAGE {L:n EXRECVRA}
        // variables for data items and parsing
        string TIMESTAMP;  	// A:32 (always)  ECV TimeFormat controls format, 0=A:12 YYMMDDHHMMSS, 1=A:16 YYYYMMDDHHMMSScc,2=YYYY-MM-DDTHH:MM:SS.s[s]*{Z|+hh:mm|-hh:mm}
        string EXID;  	// A:20 (always)  exception identifier
        string EXTYPE;  	// A:5 (always)  exception type, "ALARM" or "ERROR"
        string EXMESSAGE;  	// A:n (always)  exception description
        string EXRECVRA;  	// A:40 (always)  exception recovery action description
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length != 6 || list0[0] != "L:5") { ok=false; break; }
        string [] list1;
        list1 = SecsPort.ListSplit(list0[1]);
        if (list1.Length < 1) { ok = false; break; }
        if (!list1[0].StartsWith("A:")) { ok = false; break; }
        if (list1.Length == 2) { TIMESTAMP = list1[1];} else { TIMESTAMP = ""; }
        list1 = SecsPort.ListSplit(list0[2]);
        if (list1.Length < 1) { ok = false; break; }
        if (!list1[0].StartsWith("A:")) { ok = false; break; }
        if (list1.Length == 2) { EXID = list1[1];} else { EXID = ""; }
        list1 = SecsPort.ListSplit(list0[3]);
        if (list1.Length < 1) { ok = false; break; }
        if (!list1[0].StartsWith("A:")) { ok = false; break; }
        if (list1.Length == 2) { EXTYPE = list1[1];} else { EXTYPE = ""; }
        list1 = SecsPort.ListSplit(list0[4]);
        if (list1.Length < 1) { ok = false; break; }
        if (!list1[0].StartsWith("A:")) { ok = false; break; }
        if (list1.Length == 2) { EXMESSAGE = list1[1];} else { EXMESSAGE = ""; }
        list1 = SecsPort.ListSplit(list0[5]);
        if (list1.Length < 1) { ok=false; break; }
        int n;
        for(n=1; n < list1.Length; n++) {
            string [] list2;
            list2 = SecsPort.ListSplit(list1[n]);
            if (list2.Length < 1) { ok = false; break; }
            if (!list2[0].StartsWith("A:")) { ok = false; break; }
            if (list2.Length == 2) { EXRECVRA = list2[1];} else { EXRECVRA = ""; }
            }
        if (!ok) break;
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(5, 10, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S5F9
```
