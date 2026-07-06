# S5F7R - List Enabled Alarm Request

**Direction:** Sent by Host Only

---

| **S5F7R** | List Enabled Alarm Request | Sent by Host Only |

## Format (TSN)

`_header only_` — 這是一個**純標頭訊息**，不帶任何 data item。在 SECS-II/HSMS 協議中，訊息由「訊息標頭（message header）」和「訊息資料（data item）」兩部分組成。header-only 表示所有資訊都編碼在 10 個位元組的標頭裡（Stream=5, Function=7, W-bit 等），不需要解析任何 TSN 資料。

### 用途

Host 發送 S5F7R 向 Equipment 請求**目前已啟用（enabled）的 alarm 清單**。與 S5F5R（List Alarms Request）不同，S5F7R 不需要指定任何 ALID，Equipment 會回傳所有被啟用的 alarm。

## C# 接收處理程式

以下 C# 程式碼是 **Equipment 端** 接收 S5F7R 後的處理邏輯，使用 `secs4net` 函式庫：

### 處理流程

1. **註冊 handler** — 在初始化時用 `sp.MessageTypeAdd(5, 7, recv_S5F7R)` 將回呼函式綁定到 Stream 5, Function 7。
2. **不需解析 TSN** — S5F7R 為 header-only，直接跳過資料解析。
3. **回覆 S5F8** — 以 `sp.SendReply(5, 8, transID, reply)` 回覆 S5F8（List Enabled Alarm Data），`reply` 需建構所有已啟用 alarm 的資料 list。
4. **錯誤處理** — 因為沒有資料需要解析，若收到非空資料（非預期），送出 `sp.SendS9(7, header)`（S9F7 = illegal data）。

```csharp
    // S5F7R C# Receive message - add next line to setup
    //SecsPort sp=your_SecsPort;
    sp.MessageTypeAdd( 5, 7, new SecsMsgReceiveDelegate(recv_S5F7R));

// receive method
void recv_S5F7R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsPort sp = (SecsPort)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // no data expected
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(5, 8, transID, reply);
            }
        return;
        } // end while(ok)
    // bad data
    sp.SendS9(7, header);
    } // end recv_S5F7R
```

|     |     |     |
| --- | --- | --- |
