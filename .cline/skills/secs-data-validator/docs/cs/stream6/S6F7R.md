# S6F7R - Data Transfer Request

**Direction:** Sent by Host Only

---

Format:

[DATAID](http://hume.com/secs/items.html#DATAID)

```
    // S6F7R C# Receive message - add next line to setup
    //SecsPort sp=your_SecsPort;
    sp.MessageTypeAdd( 6, 7, new SecsMsgReceiveDelegate(recv_S6F7R));

// receive method
void recv_S6F7R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsPort sp = (SecsPort)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect DATAID
        // variables for data items and parsing
        string DATAID;  	// U4:1 (varies)  an identifier to correlate related messages
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length < 1) { ok = false; break; }
        if (list0.Length == 2) { DATAID = list0[1];} else { DATAID = ""; }
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(6, 8, transID, reply);
            }
        return;
        } // end while(ok)
    // bad data
    sp.SendS9(7, header);
    } // end recv_S6F7R
```
