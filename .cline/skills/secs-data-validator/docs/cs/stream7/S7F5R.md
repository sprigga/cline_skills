# S7F5R - Process Program Request

**Source:** [SECS-II Automated Code Generation Tool](http://hume.com/secs/msgsCS.html)

**Sent by:** Host and Equipment

## Format

[PPID](http://hume.com/secs/items.html#PPID)

## Details

Request a process program by its ID.

## C# Code

```csharp
    // S7F5R C# Receive message - add next line to setup
    //sp is a SecsPort or SecsHost object reference
    sp.MessageTypeAdd( 7, 5, new SecsMsgReceiveDelegate(recv_S7F5R));

// receive method
void recv_S7F5R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    //SecsPort sp = (SecsPort)sender;
    //SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect PPID
        // variables for data items and parsing
        string PPID;  	// A:80 (varies)  process program ID
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length < 1) { ok = false; break; }
        if (list0.Length == 2) { PPID = list0[1];} else { PPID = ""; }
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(7, 6, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S7F5R
```
