# S5F1R - Alarm Report Send

**Direction:** Sent by Equipment Only

---

| **S5F1R** | Alarm Report Send | Sent by Equipment Only |

## 用意與目的

S5F1R 是 SECS-II/GEM 協定中設備主動向 Host 回報警報狀態的核心訊息。每當設備上的警報條件**被觸發（SET）或被解除（CLEAR）**時，設備必須主動發送此訊息通知 Host。

### 在 GEM 標準中的角色

```
Equipment                          Host
   │                                 │
   │  S5F1R (Alarm Report Send)  ──▶ │  ← 設備主動推送（push），無需 Host 先詢問
   │                                 │    Host 必須在 T3 timeout 前回覆
   │  S5F2  (Alarm Report Ack)   ◀── │  ← Host 確認收到（ACKC5=0）
   │                                 │
```

S5F1R 的 reply bit（R）表示設備期待回應。Host **必須**在 T3 時間內回覆 S5F2，否則設備端會記錄通訊失敗。

### 與 S6F11（Event Report）的關係

在實際設備（如 Schmoll 鑽孔機）中，警報通常同時透過兩個管道上報：

- **S5F1R** — 警報的「原始通知」，直接攜帶 ALID 和 ALTX
- **S6F11** — Collection Event 觸發的「事件報告」，可能附帶更多 VID 資料

Host 端應同時處理兩者，不可依賴其中一個作為唯一來源。

---

## Format (TSN)

```
{L:3
[ALCD](http://hume.com/secs/items.html#ALCD)
[ALID](http://hume.com/secs/items.html#ALID)
[ALTX](http://hume.com/secs/items.html#ALTX)}
```

### Format Explanation

- **`L:3`** — 固定長度的 list，包含 3 個元素：`ALCD`、`ALID`、`ALTX`。
- **`[ALCD]`** — Alarm Code，`B:1` 格式（1 byte binary）。值 ≥ 128 表示 alarm 被設定（set），< 128 表示被清除（clear）。bit field 使用方式已被棄用（deprecated），現在只看是否 ≥ 128。
- **`[ALID]`** — Alarm ID，`U4:1` 格式（4-byte unsigned integer），用來識別是哪一個 alarm（例如溫度過高、壓力異常等）。長度可變（varies）。
- **`[ALTX]`** — Alarm Text，`A:120` 格式（ASCII 字串，最大 120 字元）。用來描述 alarm 的具體內容。長度上限最近從 40 提高到 120。

### ALCD 數值對照表

| 值（十進位） | 值（十六進位） | 意義 |
|------------|--------------|------|
| 0 | `0x00` | Alarm CLEAR（無警報） |
| 1–127 | `0x01–0x7F` | Alarm CLEAR（舊式：低位 bit 代表類別，已廢棄） |
| 128 | `0x80` | Alarm SET（無類別） |
| 129–255 | `0x81–0xFF` | Alarm SET（舊式：低位 bit 代表類別，已廢棄） |

**常見實測值：**

| ALCD 值 | 意義 |
|---------|------|
| `0` (`0x00`) | 警報解除 |
| `2` (`0x02`) | 解除（舊式 Category 0） |
| `128` (`0x80`) | 警報設定（標準） |
| `130` (`0x82`) | 警報設定（舊式 Category 2，Schmoll 設備常用） |

> **歷史說明：** 早期 SECS-II 規範中，ALCD 低 7 bits 用來表示警報類別（bit0=Personal Safety、bit1=Equipment Safety 等），bit7 表示 SET/CLEAR。GEM 標準廢棄了 bit field 拆解，只保留 bit7（≥128=SET，<128=CLEAR）。但舊設備（如 Schmoll S80）仍會送出如 `0x82` 的值，Host 應以 ≥128 判斷，不應嘗試解析低 7 bits。

### ALID 格式說明

ALID 在協定上標記為「varies（長度可變）」，實際上各廠商實作不同：

| 廠商/設備 | ALID 範圍 | 說明 |
|----------|----------|------|
| GEM 標準 | 任意 U4 | 設備自定義 |
| Schmoll S80/S50 | 1000000–9999999 | 7 位數編碼，前 1-3 位為類別 |
| 通用代理 ALID | 5003 | Schmoll 用於「代理」整體警報，ALTX 傳遞識別碼 |

### 範例

| 傳送內容 | 意義 |
|---------|------|
| `L:3 {B:1 128} {U4:1 1001} {A:20 Temperature High}` | ALCD=128（alarm set），ALID=1001，ALTX="Temperature High" |
| `L:3 {B:1 0} {U4:1 1001} {A:20 Temperature Normal}` | ALCD=0（alarm clear），ALID=1001，ALTX="Temperature Normal" |
| `L:3 {B:1 130} {U4:1 3000227} {A:40 (C227) Not enough tools. Insert more tools}` | ALCD=0x82（set），ALID=3000227，完整警報描述 |

---

## C# 接收處理程式（secs4net v2）

以下是符合本專案架構（`IMessageHandler` + `secs4net` v2.4.4）的 **Host 端** S5F1R 處理器實作：

### 處理流程

1. **取得 SecsItem** — 從 `wrapper.PrimaryMessage.SecsItem` 取得根節點，驗證為 `L:3` 結構。
2. **解析 ALCD** — `root[0].FirstValue<byte>()` 取得 1 byte binary，判斷是否 ≥ 128（SET/CLEAR）。
3. **解析 ALID** — `root[1].FirstValue<uint>()` 取得警報 ID（U4）。
4. **解析 ALTX** — `root[2].GetString()` 取得警報文字（ASCII）。
5. **回覆 S5F2** — 建構 `SecsMessage(5, 2)` 並設定 `SecsItem = B(0x00)`（ACKC5=0），呼叫 `wrapper.TryReplyAsync()`。

```csharp
// SecsApp/Handlers/S5F1Handler.cs
using Secs4Net;
using static Secs4Net.Item;

namespace SecsApp.Handlers;

public sealed class S5F1Handler : IMessageHandler
{
    public int Stream   => 5;
    public int Function => 1;

    public async Task HandleAsync(PrimaryMessageWrapper wrapper, CancellationToken ct)
    {
        var msg  = wrapper.PrimaryMessage;
        var root = msg.SecsItem;

        // S5F1 format: L:3 { ALCD, ALID, ALTX }
        if (root is null || root.Format != SecsFormat.List || root.Count < 3)
        {
            Console.WriteLine("[WARN] S5F1: unexpected structure — sending ACK anyway");
            await ReplyAckAsync(wrapper, ct);
            return;
        }

        // ALCD: B:1 — bit7 set (≥128) means alarm SET, <128 means CLEAR
        byte alcd   = root[0].FirstValue<byte>();
        bool isSet  = alcd >= 128;

        // ALID: U4:1 — alarm identifier
        uint alid   = root[1].FirstValue<uint>();

        // ALTX: A:n — alarm description text (max 120 chars)
        string altx = root[2].Count > 0 ? root[2].GetString() : string.Empty;

        string state = isSet ? "SET" : "CLEAR";
        Console.WriteLine($"[RX] S5F1 Alarm {state}: ALID={alid} ALCD=0x{alcd:X2} ALTX=\"{altx}\"");

        await ReplyAckAsync(wrapper, ct);
    }

    private static async Task ReplyAckAsync(PrimaryMessageWrapper wrapper, CancellationToken ct)
    {
        using var s5f2 = new SecsMessage(5, 2)
        {
            Name     = "AlarmReportAck",
            SecsItem = B(0x00), // ACKC5 = 0 (accepted)
        };
        bool sent = await wrapper.TryReplyAsync(s5f2, ct);
        Console.WriteLine($"[TX] S5F2 ACK → {(sent ? "OK" : "Already replied")}");
    }
}
```

### 在 Program.cs 中註冊

```csharp
factory.Register(new S5F1Handler());
```

### secs4net v2 Item API 說明

| 操作 | API | 說明 |
|------|-----|------|
| 讀取 byte | `item.FirstValue<byte>()` | 取得第一個元素值（B:1 格式） |
| 讀取 uint | `item.FirstValue<uint>()` | 取得第一個元素值（U4:1 格式） |
| 讀取字串 | `item.GetString()` | 取得 ASCII 字串（A:n 格式） |
| 建構 binary | `B(0x00)` | 建立 `B:1` Item（`Item.B` factory） |
| 建構 uint | `U4(1001u)` | 建立 `U4:1` Item（`Item.U4` factory） |
| 建構字串 | `A("text")` | 建立 `A:4` Item（`Item.A` factory） |
| 建構 list | `L(item1, item2, item3)` | 建立 `L:3` Item（`Item.L` factory） |

> **注意：** 舊版 secs4net（SecsPort 時代）使用 `SecsPort.ListSplit()` + `sp.BinToInt()` 等字串解析方式。v2 改用型別化的 `Item` 物件樹，不應混用。

### 進階：區分 SET / CLEAR 並追蹤活動警報

實際 Host 應用通常需要維護一個「活動警報表」（Active Alarm Table），用於 S5F5R（Alarm List Request）查詢回應：

```csharp
private readonly Dictionary<uint, (byte Alcd, string Altx)> _activeAlarms = new();

public async Task HandleAsync(PrimaryMessageWrapper wrapper, CancellationToken ct)
{
    // ... 解析同上 ...

    if (isSet)
        _activeAlarms[alid] = (alcd, altx);
    else
        _activeAlarms.Remove(alid);

    Console.WriteLine($"[RX] S5F1 {state}: ALID={alid} ALTX=\"{altx}\" (active={_activeAlarms.Count})");
    await ReplyAckAsync(wrapper, ct);
}
```

---

## 舊版 API 程式碼（secs4net v1 / SecsPort）

以下 C# 程式碼使用舊版 `secs4net`（`SecsPort` 時代）API，僅供對照參考，**不適用於本專案**：

### 處理流程

1. **註冊 handler** — 在初始化時用 `sp.MessageTypeAdd(5, 1, recv_S5F1)` 將回呼函式綁定到 Stream 5, Function 1。
2. **解析 TSN 資料** — 用 `SecsPort.ListSplit()` 將 `L:3` list 拆解，依序取出 `ALCD`（binary → 用 `sp.BinToInt()` 轉整數）、`ALID`（U4 字串）、`ALTX`（ASCII 字串）。
3. **回覆 S5F2** — 解析成功後以 `sp.SendReply(5, 2, transID, reply)` 回覆 S5F2（Alarm Report Ack），`reply` 需建構 ACKC5 資料。
4. **錯誤處理** — 若 TSN 資料格式錯誤（list 結構不合法或 type tag 不符），不送 S9F7（原始碼中無 `SendS9` 呼叫），直接 return。

```csharp
    // S5F1 C# Receive message - add next line to setup
    //SecsHost sp=your_SecsHost;
    sp.MessageTypeAdd( 5, 1, new SecsMsgReceiveDelegate(recv_S5F1));

// receive method
void recv_S5F1(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // expect L:3 ALCD ALID ALTX
        // variables for data items and parsing
        int ALCD;  	// B:1 (always)  alarm code byte, >= 128 alarm is set, bit field use is deprecated
        string ALID;  	// U4:1 (varies)  Alarm type ID
        string ALTX;  	// A:120 (always)  alarm text, the length limit was recently raised from 40
        string [] list0;
        list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length != 4 || list0[0] != "L:3") { ok=false; break; }
        string [] list1;
        list1 = SecsPort.ListSplit(list0[1]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1[0] != "B:1") { ok = false; break; }
        ALCD = sp.BinToInt(list1[1]);
        list1 = SecsPort.ListSplit(list0[2]);
        if (list1.Length < 1) { ok = false; break; }
        if (list1.Length == 2) { ALID = list1[1];} else { ALID = ""; }
        list1 = SecsPort.ListSplit(list0[3]);
        if (list1.Length < 1) { ok = false; break; }
        if (!list1[0].StartsWith("A:")) { ok = false; break; }
        if (list1.Length == 2) { ALTX = list1[1];} else { ALTX = ""; }
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(5, 2, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S5F1
```

---

## 實測 Log 案例（KA01 Schmoll 鑽孔機，2026-04-14）

### 場景：MachineMessages 警報觸發序列（含重連後持續警報）

此日誌展示設備在通訊重建後，陸續上報多個 S5F1R 警報的完整流程。

#### 警報預通知（通用 ALID:5003，ALCD=0x02）

```xml
<SECSMessage s="5" f="1" direction="E to H" replyBit="true"
             txid="186" time="2026-04-14T13:01:10.325Z" deviceID="0">
    <SECSData>
        <LST>
            <BIN>2</BIN>      <!-- ALCD=0x02 = OFF/Category 0, alarm cleared -->
            <UI4>5003</UI4>   <!-- ALID=5003 通用 MachineMessages 警報 -->
            <ASC>2</ASC>      <!-- ALTX="2"（通用代碼，非描述性文字） -->
        </LST>
    </SECSData>
</SECSMessage>
<SECSMessage s="5" f="2" direction="H to E" replyBit="false"
             txid="186" time="2026-04-14T13:01:10.341Z" deviceID="0">
    <SECSData><BIN>0</BIN></SECSData>  <!-- ACKC5=0 -->
</SECSMessage>
```

#### 通訊重建後多重警報上報（ALCD=0x82，各別 ALID）

```xml
<!-- txid=189: 通用 ALID 5003 再次 SET（ALCD=0x82 = ON, Cat.2） -->
<SECSMessage s="5" f="1" direction="E to H" replyBit="true"
             txid="189" time="2026-04-14T13:02:02.514Z" deviceID="0">
    <SECSData>
        <LST>
            <BIN>130</BIN>         <!-- ALCD=0x82 = ON, Category 2 -->
            <UI4>5003</UI4>        <!-- ALID=5003 -->
            <ASC>X30_G2_n</ASC>   <!-- ALTX = 機器元件識別碼 -->
        </LST>
    </SECSData>
</SECSMessage>

<!-- txid=10: 工具不足 -->
<SECSMessage s="5" f="1" direction="E to H" replyBit="true"
             txid="10" time="2026-04-14T13:04:33.532Z" deviceID="0">
    <SECSData>
        <LST>
            <BIN>130</BIN>
            <UI4>3000227</UI4>
            <ASC>(C227) Not enough tools. Insert more tools</ASC>
        </LST>
    </SECSData>
</SECSMessage>

<!-- txid=11: 外部 Feed Hold -->
<SECSMessage s="5" f="1" direction="E to H" replyBit="true"
             txid="11" time="2026-04-14T13:04:33.545Z" deviceID="0">
    <SECSData>
        <LST>
            <BIN>130</BIN>
            <UI4>1000199</UI4>
            <ASC>(199) External feed hold active. (press 'RESET button')</ASC>
        </LST>
    </SECSData>
</SECSMessage>

<!-- txid=12: 緊急停止 -->
<SECSMessage s="5" f="1" direction="E to H" replyBit="true"
             txid="12" time="2026-04-14T13:04:33.558Z" deviceID="0">
    <SECSData>
        <LST>
            <BIN>130</BIN>
            <UI4>1000002</UI4>
            <ASC>(002) Feed hold! Emergency stop left active</ASC>
        </LST>
    </SECSData>
</SECSMessage>
```

**分析：**

| txid | ALCD（十六進位） | ALID | ALTX | 意義 |
|------|----------------|------|------|------|
| 186 | `0x02` (OFF, Cat.0) | 5003 | `"2"` | 通用 MachineMessages 警報清除預通知 |
| 189 | `0x82` (ON, Cat.2) | 5003 | `"X30_G2_n"` | 通用警報 SET，ALTX 為元件識別碼（Schmoll 特殊機制） |
| 10 | `0x82` (ON, Cat.2) | 3000227 | `(C227) Not enough tools...` | 實際警報：工具不足 |
| 11 | `0x82` (ON, Cat.2) | 1000199 | `(199) External feed hold active...` | 實際警報：外部 Feed Hold |
| 12 | `0x82` (ON, Cat.2) | 1000002 | `(002) Feed hold! Emergency stop left active` | 實際警報：緊急停止 |

> **Schmoll 雙層警報機制：** 設備使用 ALID:5003 作為通用「代理」警報，ALTX 傳遞識別碼（如 `X30_G2_n`）。實際觸發的各別警報 (ALID:3000227、1000199、1000002) 緊接著以獨立 S5F1R 上報。Host 端需同時處理兩層：通用層（觸發事件關聯）與個別層（顯示具體警報文字）。

|     |     |     |
| --- | --- | --- |
