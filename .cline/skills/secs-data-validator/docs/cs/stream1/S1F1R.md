# S1F1R - Are You Online?

**Direction:** Sent by Host and Equipment

---

| **S1F1R** | Are You Online? | Sent by Host and Equipment |

### Format

`_header only_` — 這是一個**純標頭訊息**，不帶任何 data item。在 SECS-II/HSMS 協議中，訊息由「訊息標頭（message header）」和「訊息資料（data item）」兩部分組成。header-only 表示所有資訊都編碼在 10 個位元組的標頭裡（Stream=1, Function=1, W-bit 等），不需要解析任何 TSN 資料。

### C# Code Template（secs4net）

```csharp
    // S1F1R C# Receive message - add next line to setup
    //sp is a SecsPort or SecsHost object reference
    sp.MessageTypeAdd( 1, 1, new SecsMsgReceiveDelegate(recv_S1F1R));

// receive method
void recv_S1F1R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    //SecsPort sp = (SecsPort)sender;
    //SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // no data expected
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(1, 2, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S1F1R
```

**程式碼說明：**

1. **`sp.MessageTypeAdd(1, 1, ...)`** — 向連接物件（`SecsPort` 或 `SecsHost`）註冊 S1F1 的接收處理函式。收到 Stream=1, Function=1 的訊息時，會呼叫 `recv_S1F1R`。

2. **Handler 參數：**
   - `sender`：發送者物件（`SecsPort` 或 `SecsHost`），用來回覆訊息。
   - `stream`, `function`：訊息的 SxFy 識別。
   - `send_reply`：布林值，若為 `true` 表示對方期待回覆。
   - `transID`：交易 ID，回覆時必須帶上同一個 ID。
   - `TSN_data`：訊息的 data item（S1F1R 為 header-only，此欄位為空）。
   - `header`：原始標頭字串。

3. **`sp.SendReply(1, 2, transID, reply)`** — 回覆 S1F2（Online Data）。function 改為 `2`（偶數 = reply），`transID` 必須與收到的請求一致。

|     |     |     |
| --- | --- | --- |
