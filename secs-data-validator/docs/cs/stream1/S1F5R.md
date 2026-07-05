# S1F5R - Formatted Status Request

**Direction:** Sent by Host Only

---

| **S1F5R** | Formatted Status Request | Sent by Host Only |

Format: **SECS-II data payload structure** — 列出此消息的 data 區段包含哪些 SEMI 標準資料項目（data items）及其型態。

[SFCD](http://hume.com/secs/items.html#SFCD) — Status Form Code, `B:1` (1 byte binary, 整數值), 用來指定 Host 想查詢的狀態報告格式

```
    // S1F5R C# Receive message - add next line to setup
    //SecsPort sp=your_SecsPort;
    sp.MessageTypeAdd( 1, 5, new SecsMsgReceiveDelegate(recv_S1F5R));

// receive method
void recv_S1F5R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsPort sp = (SecsPort)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect SFCD
        // variables for data items and parsing
        int SFCD;  	// B:1 (always)  status form code
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length < 1) { ok = false; break; }
        if (list0[0] != "B:1") { ok = false; break; }
        SFCD = sp.BinToInt(list0[1]);
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(1, 6, transID, reply);
            }
        return;
        } // end while(ok)
    // bad data
    sp.SendS9(7, header);
    } // end recv_S1F5R
```

|     |     |     |
| --- | --- | --- |
