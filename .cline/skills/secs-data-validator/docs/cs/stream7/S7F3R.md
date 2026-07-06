# S7F3R - Process Program Send

**Direction:** Sent by Host and Equipment

---

| **S7F3R** | Process Program Send | Sent by Host and Equipment |
| --- | --- | --- |

## 協定意義

**Process Program（製程程式）** 是控制設備如何處理晶圓的指令集（例如溫度、氣體流量、步驟時序等）。

S7F3R 的作用是：
> **Host 或 Equipment 任一方主動傳送一個完整的製程程式給對方，並要求回應（R = Reply required）。**

常見場景：
- Host 將新的製程程式下傳到設備（Download）
- 設備將目前執行中的程式上傳回 Host（Upload）

### 與 Stream 7 其他訊息的關係

```
S7F1R  →  詢問設備已有的 PPID 清單
S7F2   ←  回覆 PPID 清單

S7F3R  →  傳送完整 Process Program（PPID + PPBODY）  ← 本訊息
S7F4   ←  回應是否接受（PPGNT: 0=OK, 1=已存在, 2=空間不足...）

S7F5R  →  要求取回 Process Program（接收方主動請求）
S7F6   ←  回覆 Process Program 內容（也是 PPID + PPBODY）
```

S7F3R 是「推送」方向（傳送方主動），S7F5R 是「拉取」方向（接收方主動請求）。

---

## 訊息格式

### TSN 表示法

```
{L:2
  [PPID]
  [PPBODY]
}
```

### 欄位說明

| 欄位 | SECS 型別 | C# 型別 | 說明 |
|------|-----------|---------|------|
| `PPID` | `A:80` | `string` | Process Program ID，ASCII 字串，最大 80 字元，用來識別製程程式名稱 |
| `PPBODY` | `B:n` | `byte[]` | Process Program 實際內容，Binary，長度可變，可為任意非 list 型別 |

### 訊息結構圖

```
S7F3R (SecsFormat.List, Count=2)
├── [0] PPID    → SecsFormat.ASCII   (A:80, 最長 80 字元)
│              例: "ETCH_RECIPE_001"
└── [1] PPBODY → SecsFormat.Binary   (B:n, 可變長度)
               例: 0x01 0x2C 0x01 0x32 0x78 ...
```

---

## S7F4 回應格式（Process Program Send Acknowledge）

接收方收到 S7F3R 後，**必須**回覆 S7F4：

```
S7F4
└── PPGNT → B:1  (Grant Code)
```

| PPGNT 值 | 常數名稱 | 意義 |
|----------|----------|------|
| `0x00` | `PpgntOk` | 接受 |
| `0x01` | `PpgntAlreadyExists` | PPID 已存在（重複） |
| `0x02` | `PpgntInsufficientSpace` | 設備空間不足 |
| `0x03` | `PpgntInvalidPpid` | PPID 無效或格式錯誤 |
| `0x04` | `PpgntBusy` | 設備忙碌，暫時無法接受 |
| `0x05` | `PpgntWillNotAccept` | 拒絕接受 |

---

## secs4net v2 實作範例

### 建立並傳送 S7F3R（Host 下傳製程程式）

```csharp
using Secs4Net;
using static Secs4Net.Item;

// 製程程式內容（模擬：溫度=300°C, 壓力=50 mTorr, 時間=120 秒）
byte[] recipeData = new byte[]
{
    0x01,       // Header byte: recipe version 1
    0x2C, 0x01, // 溫度: 300°C (0x012C, big-endian)
    0x32,       // 壓力: 50 mTorr
    0x78        // 時間: 120 秒
};

using var s7f3 = new SecsMessage(7, 3)
{
    Name     = "ProcessProgramSend",
    SecsItem = L(                         // L:2
        A("ETCH_RECIPE_001"),             // PPID  → A:16 (ASCII)
        B(recipeData)                     // PPBODY → B:5 (Binary)
    ),
};

// 傳送並等待 S7F4 回應
SecsMessage reply = await secsGem.SendAsync(s7f3, ct);
byte ppgnt = reply.SecsItem.FirstValue<byte>();
Console.WriteLine($"[RX] S7F4 PPGNT=0x{ppgnt:X2}");
```

### 接收並解析 S7F3R（Equipment 端 Handler）

依照本 repo 的 `IMessageHandler` 架構（參見 `SecsApp/Handlers/`）：

```csharp
// SecsApp/Handlers/S7F3Handler.cs
using Secs4Net;
using static Secs4Net.Item;

public sealed class S7F3Handler : IMessageHandler
{
    public int Stream   => 7;
    public int Function => 3;

    private const byte PpgntOk                = 0x00;
    private const byte PpgntAlreadyExists      = 0x01;
    private const byte PpgntInsufficientSpace  = 0x02;
    private const byte PpgntInvalidPpid        = 0x03;

    public async Task HandleAsync(PrimaryMessageWrapper wrapper, CancellationToken ct)
    {
        byte ppgnt = Parse(wrapper.PrimaryMessage.SecsItem);

        using var s7f4 = new SecsMessage(7, 4)
        {
            Name     = "ProcessProgramSendAck",
            SecsItem = B(ppgnt),
        };
        await wrapper.TryReplyAsync(s7f4, ct);
        Console.WriteLine($"[TX] S7F4 PPGNT=0x{ppgnt:X2}");
    }

    internal static byte Parse(Item? root)
    {
        // 驗證外層 L:2 結構
        if (root is null || root.Format != SecsFormat.List || root.Count != 2)
        {
            Console.WriteLine("[WARN] S7F3: root must be L:2");
            return PpgntInvalidPpid;
        }

        // 解析 PPID (A:80)
        var ppidItem = root[0];
        if (ppidItem.Format != SecsFormat.ASCII)
        {
            Console.WriteLine("[WARN] S7F3: PPID is not ASCII");
            return PpgntInvalidPpid;
        }
        string ppid = ppidItem.Count > 0 ? ppidItem.GetString() : string.Empty;

        // 解析 PPBODY (B:n)
        var ppbodyItem = root[1];
        if (ppbodyItem.Format != SecsFormat.Binary)
        {
            Console.WriteLine($"[WARN] S7F3: PPBODY format={ppbodyItem.Format}, expected Binary");
            return PpgntInvalidPpid;
        }
        byte[] ppbody = ppbodyItem.GetValues<byte>().ToArray();

        Console.WriteLine($"[RX] S7F3 PPID=\"{ppid}\" PPBODY={ppbody.Length} bytes");
        // 儲存製程程式到設備記憶體...

        return PpgntOk;
    }
}
```

在 `Program.cs` 中註冊：

```csharp
factory.Register(new S7F3Handler());
```

---

## 新舊 API 對照

| 動作 | 舊版 SecsPort（文件參考） | secs4net v2（本 repo） |
|------|--------------------------|------------------------|
| 驗證 List 結構 | `list0.Length != 3 \|\| list0[0] != "L:2"` | `root.Format != SecsFormat.List \|\| root.Count != 2` |
| 取出 PPID | `list1 = ListSplit(list0[1]); PPID = list1[1]` | `root[0].GetString()` |
| 取出 PPBODY bytes | `sp.BinToInt(list1[1+i])` 逐一轉換 | `root[1].GetValues<byte>().ToArray()` |
| 回覆訊息 | `sp.SendReply(7, 4, transID, reply)` | `wrapper.TryReplyAsync(s7f4, ct)` |
| 註冊 handler | `sp.MessageTypeAdd(7, 3, recv_S7F3R)` | `factory.Register(new S7F3Handler())` |

---

## 舊版 SecsPort 接收範例（歷史參考）

> 以下程式碼使用舊版 SecsPort TSN 字串 API，**不適用於本 repo**，僅供對照理解。

### 處理流程

1. **註冊 handler** — 在初始化時用 `sp.MessageTypeAdd(7, 3, recv_S7F3R)` 將回呼函式綁定到 Stream 7, Function 3。
2. **解析 TSN 資料** — 用 `SecsPort.ListSplit()` 將 TSN 字串拆解為 list 結構，驗證外層 list 為 `L:2`，再分別取出 PPID 和 PPBODY。
3. **PPID 解析** — `list0[1]` 是 PPID 項目，透過 `ListSplit()` 取得實際字串值。
4. **PPBODY 解析** — `list0[2]` 是 PPBODY 項目（Binary 型別），透過 `sp.BinToInt()` 將二進位資料轉換為整數陣列。
5. **回覆 S7F4** — 解析成功後以 `sp.SendReply(7, 4, transID, reply)` 回覆 S7F4（Process Program Send Acknowledge）。

```csharp
    // S7F3R C# Receive message - add next line to setup
    //sp is a SecsPort or SecsHost object reference
    sp.MessageTypeAdd( 7, 3, new SecsMsgReceiveDelegate(recv_S7F3R));

// receive method
void recv_S7F3R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    //SecsPort sp = (SecsPort)sender;
    //SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect L:2 PPID PPBODY
        // variables for data items and parsing
        string PPID;  	// A:80 (varies)  process program ID
        int [] PPBODY;  	// B:n (varies)  process program data, any non-list type
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length != 3 || list0[0] != "L:2") { ok=false; break; }
        string [] list1;
        list1 = SecsPort.ListSplit(list0[1]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { PPID = list1[1];} else { PPID = ""; }
        list1 = SecsPort.ListSplit(list0[2]);
        if (list1.Length < 1) { ok = false; break; }
        PPBODY = new int[list1.Length-1];
        for(int i=0; i < PPBODY.Length; i++) {
            PPBODY[i] = sp.BinToInt(list1[1+i]);
            }
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(7, 4, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S7F3R
```
