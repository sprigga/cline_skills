# S5F3R - Enable/Disable Alarm Send

**Direction:** Sent by Host Only

---

| **S5F3R** | Enable/Disable Alarm Send | Sent by Host Only |

## 用意與目的

S5F3R 是 Host 主動向設備發出的「警報管理」指令，用來啟用（Enable）或停用（Disable）設備上的指定警報。設備收到後以 S5F4 回覆確認。

### 在 GEM 標準中的角色

```
Host                               Equipment
  │                                    │
  │  S5F3R (Enable/Disable Alarm)  ──▶ │  ← Host 主動發送（outbound command）
  │                                    │    設備必須在 T3 timeout 前回覆
  │  S5F4  (Enable/Disable Alarm Ack) ◀│  ← 設備確認（ACKC5=0）
  │                                    │
```

與 S5F1R（設備推送警報）相反，S5F3R 是**Host 主動下達的設定指令**。這是 GEM 中 Host 對設備進行「警報管理」的標準手段。

### 典型使用場景

- **上線初始化** — Host 連線後送出 `S5F3R (ALED=128, ALID=空)` 啟用設備上全部警報
- **選擇性停用** — 對特定維護期間的非關鍵警報暫時停用
- **恢復啟用** — 維護結束後重新啟用

### 與 S5F5R / S5F6 的關係

GEM 警報管理的完整流程：

| 訊息 | 方向 | 用途 |
|------|------|------|
| S5F3R | H→E | 啟用/停用指定警報 |
| S5F4 | E→H | 確認 Enable/Disable |
| S5F5R | H→E | 查詢已啟用警報清單 |
| S5F6 | E→H | 回傳已啟用警報清單 |

---

## Format (TSN)

```
{L:2
[ALED](http://hume.com/secs/items.html#ALED)
[ALID](http://hume.com/secs/items.html#ALID)}
```

### Format Explanation

- **`L:2`** — 固定長度的 list，包含 2 個元素：`ALED` 和 `ALID`。
- **`[ALED]`** — Alarm Enable/Disable，`B:1` 格式（1 byte binary）。
  - `128` (`0x80`) = Enable（啟用該 alarm）
  - `0` (`0x00`) = Disable（停用該 alarm）
- **`[ALID]`** — Alarm ID，`U4:1` 格式（4-byte unsigned integer），指定要啟用/停用的 alarm。長度可變（varies）。

### ALED 數值對照表

| 值（十進位） | 值（十六進位） | 意義 |
|------------|--------------|------|
| 0 | `0x00` | Disable — 停用指定警報 |
| 128 | `0x80` | Enable — 啟用指定警報 |

> **注意：** ALED 的語意與 ALCD（S5F1R）相同：bit7 表示 ON/OFF，其餘 bits 忽略。實作時只需判斷 `>= 128` 或 `== 0`。

### ALID 廣播語意

| ALID 值 | 意義 |
|---------|------|
| 指定 U4 值（如 `1001`） | 僅對該 ALID 套用操作 |
| 空值（`U4:0`，無內容） | **廣播**：對設備上全部已定義警報套用操作 |

> **廣播慣例：** ALID 為空是 SECS-II 中「全部」的表示方式，同樣的慣例也出現在 S6F23（CEID 空值=全部 Collection Event）。C# 解析時 `item.Count == 0` 即為廣播。

### 範例

| 傳送內容 | 意義 |
|---------|------|
| `L:2 {B:1 128} {U4:1 1001}` | 啟用（enable）ALID=1001 的 alarm |
| `L:2 {B:1 0} {U4:1 1001}` | 停用（disable）ALID=1001 的 alarm |
| `L:2 {B:1 128} {U4:0}` | 啟用（enable）**全部** alarm（ALID 為空，廣播語意） |

---

## C# 發送程式碼（secs4net v2）

本專案為 **Host 端**，S5F3R 是**主動發出**的 outbound command，對應 `OutboundCommands.cs` 的設計模式。

### 建構與發送流程

1. **建構 `SecsMessage(5, 3)`** — 指定 Stream=5、Function=3，reply bit 由 secs4net 自動設定（函式名稱帶 R）。
2. **設定 `SecsItem = L(...)`** — 以 `Item.L` 包裝 `ALED`（`B:1`）和 `ALID`（`U4:1`）。
3. **呼叫 `secsGem.SendAsync()`** — 等待設備回覆 S5F4。
4. **解析 S5F4 的 ACKC5** — `reply.SecsItem.FirstValue<byte>()` 取得結果，驗證為 `0`。

```csharp
// OutboundCommands.cs — 啟用全部警報（ALID 空值 = 廣播）
public static async Task SendS5F3EnableAllAlarmsAsync(ISecsGem secsGem, CancellationToken ct)
{
    using var s5f3 = new SecsMessage(5, 3)
    {
        Name     = "EnableDisableAlarm",
        SecsItem = L(
            B(0x80),   // ALED = 128 = Enable
            U4()       // ALID 空值 = 廣播，套用至全部警報
        ),
    };

    SecsMessage? reply = await secsGem.SendAsync(s5f3, ct);

    if (reply?.SecsItem is null)
    {
        Console.WriteLine("[WARN] S5F3R: no reply (T3 timeout or null body)");
        return;
    }

    // S5F4: B:1 ACKC5
    byte ackc5 = reply.SecsItem.FirstValue<byte>();
    Console.WriteLine($"[RX] S5F4 ACKC5={ackc5} ({(ackc5 == 0 ? "OK" : "Error")})");
}

// 啟用/停用單一 ALID
public static async Task SendS5F3SetAlarmAsync(
    ISecsGem secsGem, uint alid, bool enable, CancellationToken ct)
{
    byte aled = enable ? (byte)0x80 : (byte)0x00;

    using var s5f3 = new SecsMessage(5, 3)
    {
        Name     = "EnableDisableAlarm",
        SecsItem = L(
            B(aled),    // ALED
            U4(alid)    // ALID
        ),
    };

    SecsMessage? reply = await secsGem.SendAsync(s5f3, ct);
    byte ackc5 = reply?.SecsItem?.FirstValue<byte>() ?? 0xFF;
    Console.WriteLine($"[RX] S5F4 ACKC5={ackc5} ALID={alid} {(enable ? "enabled" : "disabled")}");
}
```

### secs4net v2 Item 建構說明

| 操作 | API | 說明 |
|------|-----|------|
| 建構空 U4 | `U4()` | 建立 `U4:0`（無值），ALID 廣播語意 |
| 建構有值 U4 | `U4(1001u)` | 建立 `U4:1` 指定 ALID |
| 建構 binary | `B(0x80)` | 建立 `B:1` ALED=Enable |
| 建構 list | `L(item1, item2)` | 建立 `L:2` 包裝 ALED + ALID |

> **`Item.U4()` 無參數呼叫：** 建立長度為 0 的 U4 Item（`U4:0`），對應 SECS-II 廣播語意「全部」。

---

## 舊版 API 程式碼（secs4net v1 / SecsPort）

以下 C# 程式碼使用舊版 `secs4net`（`SecsPort` 時代）API，展示 **Equipment 端** 接收 S5F3R 的處理邏輯。**不適用於本專案**，僅供對照參考。

### 處理流程

1. **註冊 handler** — 在初始化時用 `sp.MessageTypeAdd(5, 3, recv_S5F3)` 將回呼函式綁定到 Stream 5, Function 3。
2. **解析 TSN 資料** — 用 `SecsPort.ListSplit()` 將 `L:2` list 拆解，取出 `ALED`（binary → 用 `sp.BinToInt()` 轉整數）和 `ALID`（U4 字串）。
3. **回覆 S5F4** — 解析成功後以 `sp.SendReply(5, 4, transID, reply)` 回覆 S5F4（Enable/Disable Alarm Ack），`reply` 需建構 ACKC5 資料。
4. **錯誤處理** — 若 TSN 資料格式錯誤，送出 `sp.SendS9(7, header)`（S9F7 = illegal data）通知 host。

```csharp
    // S5F3 C# Receive message - add next line to setup
    //SecsPort sp=your_SecsPort;
    sp.MessageTypeAdd( 5, 3, new SecsMsgReceiveDelegate(recv_S5F3));

// receive method
void recv_S5F3(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsPort sp = (SecsPort)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect L:2 ALED ALID
        // variables for data items and parsing
        int ALED;  	// B:1 (always)  enable/disable alarm, 128 means enable, 0 disable
        string ALID;  	// U4:1 (varies)  Alarm type ID
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length != 3 || list0[0] != "L:2") { ok=false; break; }
        string [] list1;
        list1 = SecsPort.ListSplit(list0[1]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1[0] != "B:1") { ok = false; break; }
        ALED = sp.BinToInt(list1[1]);
        list1 = SecsPort.ListSplit(list0[2]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { ALID = list1[1];} else { ALID = ""; }
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(5, 4, transID, reply);
            }
        return;
        } // end while(ok)
    // bad data
    sp.SendS9(7, header);
    } // end recv_S5F3
```

---

## 實測 Log 案例（KA01 Schmoll 鑽孔機，2026-03-18）

### 場景：Host 上線後啟用全部警報

此日誌展示 Host 在建立連線後發送 S5F3R 啟用全部警報，設備即時確認的完整流程。

**S5F3R（H→E）— 啟用全部警報**

```xml
<SECSMessage s="5" f="3" direction="H to E" replyBit="true"
             txid="2000035" time="2026-03-18T06:09:00.493Z" deviceID="0">
    <SECSData>
        <LST>
            <BIN>128</BIN>  <!-- ALED=0x80 = Enable -->
            <UI4 />         <!-- ALID 空值 = 套用至全部 alarm（廣播） -->
        </LST>
    </SECSData>
</SECSMessage>
```

**S5F4（E→H）— 確認（ACKC5=0）**

```xml
<SECSMessage s="5" f="4" direction="E to H" replyBit="false"
             txid="2000035" time="2026-03-18T06:09:00.495Z" deviceID="0">
    <SECSData>
        <BIN>0</BIN>  <!-- ACKC5=0 = OK -->
    </SECSData>
</SECSMessage>
```

**分析：**

| 欄位 | 值 | 說明 |
|------|-----|------|
| ALED | `128`（`0x80`）| Enable 旗標 |
| ALID | 空 `U4:0` | 廣播：啟用**全部**警報 |
| ACKC5 | `0` | Equipment 確認成功 |
| 來回時間 | 2 ms（493Z → 495Z）| 設備回覆迅速 |

> **注意：** ALID 為空（`<UI4 />`）是 SECS-II 中的廣播語意，代表對所有已定義的警報套用此 Enable/Disable 操作。C# 解析時 `item.Count == 0` 即為廣播（secs4net v2），對應舊版程式碼中 `list1.Length == 1`（無值）的 `ALID = ""` 分支。

|     |     |     |
| --- | --- | --- |
