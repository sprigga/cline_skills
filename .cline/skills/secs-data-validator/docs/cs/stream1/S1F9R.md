# S1F9R - Material Transfer Status Request

**Direction:** Sent by Host Only

---

| **S1F9R** | Material Transfer Status Request | Sent by Host Only |

Format:

_header only_ — the message has no data body; it consists only of the SECS-II message header (stream, function, w-bit, and system bytes). Contrast with other messages that list specific data items (e.g., `L<n> [items...]`).

```
    // S1F9R C# Receive message - add next line to setup
    //SecsPort sp=your_SecsPort;
    sp.MessageTypeAdd( 1, 9, new SecsMsgReceiveDelegate(recv_S1F9R));

// receive method
void recv_S1F9R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsPort sp = (SecsPort)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // no data expected
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(1, 10, transID, reply);
            }
        return;
        } // end while(ok)
    // bad data
    sp.SendS9(7, header);
    } // end recv_S1F9R
```

|     |     |     |
| --- | --- | --- |
