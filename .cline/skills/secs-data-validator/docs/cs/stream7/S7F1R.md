# S7F1R - Process Program Load Inquire

**Source:** [SECS-II Automated Code Generation Tool](http://hume.com/secs/msgsCS.html)

**Sent by:** Host and Equipment

## Format

{L:2
[PPID](http://hume.com/secs/items.html#PPID)

[LENGTH](http://hume.com/secs/items.html#LENGTH) }

## Details

Request message to inquire about loading a process program. Contains the process program ID and its length in bytes.

## C# Code

```csharp
    // S7F1R C# Receive message - add next line to setup
    //sp is a SecsPort or SecsHost object reference
    sp.MessageTypeAdd( 7, 1, new SecsMsgReceiveDelegate(recv_S7F1R));

// receive method
void recv_S7F1R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    //SecsPort sp = (SecsPort)sender;
    //SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect L:2 PPID LENGTH
        // variables for data items and parsing
        string PPID;  	// A:80 (varies)  process program ID
        uint LENGTH;  	// U4:1 (always)  program length in bytes
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length != 3 || list0[0] != "L:2") { ok=false; break; }
        string [] list1;
        list1 = SecsPort.ListSplit(list0[1]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { PPID = list1[1];} else { PPID = ""; }
        list1 = SecsPort.ListSplit(list0[2]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1[0] != "U4:1") { ok = false; break; }
        LENGTH = uint.Parse(list1[1]);
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(7, 2, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S7F1R
```
