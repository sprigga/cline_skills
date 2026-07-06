# S5F5R - List Alarms Request

**Direction:** Sent by Host Only

**Reply:** [S5F6](S5F6.md) — List Alarm Data

---

| **S5F5R** | List Alarms Request | Sent by Host Only |

## 目的與用意

S5F5R 是 SECS-II Stream 5（Exception Handling / 警報管理）中的 **主動查詢訊息**。Host 用它向 Equipment 查詢警報（Alarm）的定義與目前狀態。

### 核心語義

S5F5R 傳遞的是 **「我想查哪些 alarm」**，Equipment 以 [S5F6](S5F6.md) 回覆 **「這些 alarm 的定義與狀態」**。

- 傳送 `U4:0`（空 list）→ 查詢設備上**全部** alarm
- 傳送 `U4:n ALID₁ ALID₂ …` → 只查詢指定 ALID 的 alarm

### 使用情境

| 情境 | 說明 |
|------|------|
| **設備連線初始化** | Host 連線後，以 `U4:0` 查詢全部 alarm，建立本地 alarm 資料庫（ALID → ALTX 的對照表）。 |
| **特定 alarm 細節查詢** | 收到 S5F1R（Alarm Report Send）後，Host 想確認該 ALID 的完整文字說明，用 S5F5R 指定 ALID 查詢。 |
| **UI 畫面刷新** | 操作員在 Host 端警報管理畫面按「重新整理」，Host 發送 S5F5R 取得最新警報狀態。 |
| **批次狀態確認** | Host 需要核查多個已知 ALID 的目前 ALCD 狀態（Set 或 Clear），傳入 ALID 清單查詢。 |

### 與其他 Stream 5 訊息的關係

```
Host                                          Equipment
 │                                               │
 │──── S5F5R (List Alarms Request) ────────────→│  Host 查詢 alarm（全部或指定 ALID）
 │←─── S5F6  (List Alarm Data) ────────────────│  Equipment 回覆 alarm 定義與狀態
 │                                               │
 │──── S5F7R (List Enabled Alarm Request) ─────→│  Host 查詢「已啟用」的 alarm
 │←─── S5F8  (List Enabled Alarm Data) ─────── │  只回傳 enabled 的 alarm
 │                                               │
 │←─── S5F1R (Alarm Report Send) ──────────────│  Equipment 主動上報 alarm 事件
 │──── S5F2  (Alarm Report Ack) ───────────────→│  Host 確認收到
 │                                               │
 │──── S5F3R (Enable/Disable Alarm) ───────────→│  Host 啟用或停用指定 alarm
 │←─── S5F4  (Enable/Disable Alarm Ack) ────── │  Equipment 回覆 ACKC5
```

> **S5F5R vs S5F7R 的差異：**
> - S5F5R → S5F6：查詢**所有**符合條件的 alarm（不論是否 enabled）
> - S5F7R → S5F8：只回傳**目前已啟用（enabled）** 的 alarm
>
> 兩者回覆格式完全相同（`L:n {L:3 ALCD ALID ALTX}`），但 S5F6 包含已停用的警報，S5F8 不包含。

---

## Format (TSN)

```
[ALIDVECTOR]
```

### 資料格式詳解

#### ALIDVECTOR — Alarm ID Vector（`U4:n`）

`U4:n` 是 SECS-II 的 Unsigned 4-byte Integer 陣列格式，每個元素佔 4 bytes，`n` 為元素個數。

| TSN 表示 | 意義 |
|---------|------|
| `U4:0` | 零長度（empty）→ 請求回傳**所有** alarms |
| `U4:1 1001` | 只查詢 ALID = 1001 的 alarm |
| `U4:2 1001 1005` | 查詢 ALID=1001 和 ALID=1005 的 alarm |
| `U4:4 1000004 1000010 1000199 3000227` | 查詢 4 個指定 ALID 的 alarm |

> **關鍵語義：** `U4:0` 表示 0 個元素的空陣列，而**不是**值為 0 的 ALID。在 SECS-II 中，`U4:0` 是表示「空 vector」最常見的慣例，代表「無限制，全部回傳」。

#### SECS-II 資料型態對照

| SECS-II 型態 | TSN 格式 | 二進位大小 | 值域 | 說明 |
|-------------|---------|----------|------|------|
| `U4:n` | `U4:{count} val₁ val₂ …` | 4n bytes | 0 ~ 4,294,967,295 | Unsigned 4-byte int 陣列 |
| `U4:0` | `U4:0` | 0 bytes | — | 空陣列，語義「全部查詢」 |

### 格式層級圖

```
S5F5R data
 └── U4:n                       ← ALIDVECTOR（alarm ID 陣列）
      ├── [0] (empty)           ← n=0，查詢全部 alarm
      ├── <ALID₁>              ← n=1，查詢 ALID₁
      ├── <ALID₂>              ← n=2，查詢 ALID₁ 和 ALID₂
      └── ...                   ← 可攜帶任意多個 ALID
```

### 傳送範例

| 場景 | TSN 傳送內容 | 說明 |
|------|------------|------|
| 查詢全部 alarm | `U4:0` | 空陣列，設備回傳所有 alarm 定義與狀態 |
| 查詢單一 alarm | `U4:1 1001` | 只查 ALID=1001 |
| 查詢兩個 alarm | `U4:2 1001 1005` | 查 ALID=1001 和 ALID=1005 |
| 查詢四個 alarm | `U4:4 1000004 1000010 1000199 3000227` | 批次查詢 |

---

## 實機案例（Schmoll KA01 S80 鑽孔機）

### 案例 1：查詢單一 ALID

```xml
<!-- Host → Equipment：查詢 ALID=1000004 -->
<SECSMessage s="5" f="5" direction="H to E" replyBit="true" txid="5001001"
    time="2026-03-19T10:00:00.000Z" deviceID="0">
    <SECSData><UI4>1000004</UI4></SECSData>
</SECSMessage>

<!-- Equipment → Host：回覆 S5F6 -->
<SECSMessage s="5" f="6" direction="E to H" replyBit="false" txid="5001001"
    time="2026-03-19T10:00:00.020Z" deviceID="0">
    <SECSData>
        <LST>
            <LST><BIN>2</BIN><UI4>1000004</UI4><ASC>(004) Loader: Emergency stop right active</ASC></LST>
        </LST>
    </SECSData>
</SECSMessage>
```

**XML 欄位解析：**

| XML 元素 | SECS-II 型態 | 值 | 說明 |
|----------|-------------|-----|------|
| `<UI4>1000004</UI4>` | `U4:1` | 1000004 | S5F5R 傳送的 ALIDVECTOR（1 個 ID） |
| `<BIN>2</BIN>` | `B:1` | 2 | ALCD = 2（Cleared, 分類 2）|
| `<UI4>1000004</UI4>` | `U4:1` | 1000004 | ALID = 1000004 |
| `<ASC>...</ASC>` | `A:39` | `(004) Loader: Emergency stop right active` | ALTX 警報描述 |

**分析：**
- Host 傳送 `U4:1 1000004`，查詢 ALID=`1000004`（Loader 緊急停止右側）
- Equipment 回覆 ALCD=`2`（< 128 → 警報**已清除**）
- ALTX 含 `(004)` 前綴，對應 ALID 末 3 碼（Schmoll S80 命名慣例）
- 回應時間 20 ms

### 案例 2：查詢全部 alarm（U4:0）

```xml
<!-- Host → Equipment：查詢全部 alarm（空 vector = U4:0）-->
<SECSMessage s="5" f="5" direction="H to E" replyBit="true" txid="5001002"
    time="2026-03-19T10:01:00.000Z" deviceID="0">
    <SECSData><UI4 /></SECSData>
</SECSMessage>
```

> `<UI4 />` 是 XML 中表示零長度 U4 陣列（`U4:0`）的方式，等同 TSN 的 `U4:0`。

---

## C# 實作（secs4net v2.4.4 — Host 端）

以下程式碼是 **Host 端** 使用 secs4net v2 強型別 `Item` API 發送 S5F5R、並解析 S5F6 回覆的完整邏輯。

### 發送查詢

```csharp
using Secs4Net;
using Secs4Net.Sml;

// 情境 1：查詢全部 alarm（空 ALIDVECTOR = U4:0）
var s5f5_all = new SecsMessage(5, 5, replyExpected: true)
{
    SecsItem = Item.U4()  // U4:0，零長度陣列
};

// 情境 2：查詢指定 ALID
var s5f5_specific = new SecsMessage(5, 5, replyExpected: true)
{
    SecsItem = Item.U4(1001u, 1005u)  // U4:2，查詢 ALID=1001 和 ALID=1005
};

// 發送並等待 S5F6 回覆
SecsMessage s5f6Reply = await secsGem.SendAsync(s5f5_specific);
```

### 解析 S5F6 回覆

```csharp
// S5F6 格式：L:n { L:3 B:1(ALCD) U4:1(ALID) A(ALTX) }
var alarms = new List<(int alcd, uint alid, string altx)>();

Item outerList = s5f6Reply.SecsItem;  // L:n
foreach (Item alarmItem in outerList)  // 迭代每筆 L:3
{
    // alarmItem[0] = ALCD (B:1)
    // alarmItem[1] = ALID (U4:1)
    // alarmItem[2] = ALTX (A:n)
    int  alcd = alarmItem[0].GetValue<byte>();
    uint alid = alarmItem[1].GetValue<uint>();
    string altx = alarmItem[2].GetValue<string>();

    bool isSet = (alcd & 0x80) != 0;  // bit 7 = 1 → alarm SET
    alarms.Add((alcd, alid, altx));
    Console.WriteLine($"ALID={alid:D7}  {'(SET)' if isSet else '(CLR)'}  {altx}");
}
```

### ALCD 狀態判斷

```csharp
static bool IsAlarmSet(int alcd) => (alcd & 0x80) != 0;
// alcd >= 128 → SET（警報觸發中）
// alcd <  128 → CLEAR（警報已清除）
```

| ALCD 值 | `IsAlarmSet()` | 實際意義 |
|---------|---------------|---------|
| `0` | `false` | Cleared, 無分類 |
| `2` | `false` | Cleared, 分類 2（Schmoll S80 常見值） |
| `128` | `true` | **SET**，無分類 |
| `130` | `true` | **SET**，分類 2 |

### 舊式 TSN 字串 API（secs4net v1 / SecsPort 參考）

> 以下為舊版 `SecsPort` 字串 API 的 Equipment 端接收範例，僅供參考對照。

```csharp
// 向 SecsPort 註冊 handler（初始化時呼叫）
sp.MessageTypeAdd(5, 5, new SecsMsgReceiveDelegate(recv_S5F5R));

void recv_S5F5R(object sender, int stream, int function, bool send_reply,
    int transID, string TSN_data, string header)
{
    SecsPort sp = (SecsPort)sender;
    bool ok = true;
    while (ok)
    {
        // ALIDVECTOR: U4:n
        string[] list0 = SecsPort.ListSplit(TSN_data);
        if (list0.Length < 1) { ok = false; break; }

        // list0[0] = "U4:n"（型態標記）
        // list0[1..] = 各 ALID 字串值
        uint[] ALIDVECTOR = new uint[list0.Length - 1];
        for (int i = 0; i < ALIDVECTOR.Length; i++)
        {
            ALIDVECTOR[i] = uint.Parse(list0[1 + i]);
        }

        // ALIDVECTOR.Length == 0 → 查全部
        // ALIDVECTOR.Length >  0 → 查指定 ALID

        if (send_reply)
        {
            string reply = BuildS5F6Reply(ALIDVECTOR); // 自行實作查詢邏輯
            sp.SendReply(5, 6, transID, reply);
        }
        return;
    }
    // 資料格式錯誤 → 回覆 S9F7（Illegal Data）
    sp.SendS9(7, header);
}
```

### 處理流程說明

1. **解析 ALIDVECTOR** — `SecsPort.ListSplit(TSN_data)` 將 `U4:n val₁ val₂ …` 拆解為陣列；`list0[0]` 是型態標記（`"U4:n"`），`list0[1+i]` 是各 ALID 的字串值。
2. **判斷查詢範圍** — `ALIDVECTOR.Length == 0` 表示 `U4:0`（查全部），`> 0` 表示只查指定 ALID。
3. **建構 S5F6 回覆** — 根據 ALID 清單查詢設備內部 alarm 資料庫，建構對應的 `L:n {L:3 ...}` 結構。
4. **錯誤處理** — TSN 資料格式錯誤時，以 `sp.SendS9(7, header)` 通知 Host（S9F7 = Illegal Data）。

---

## 相關訊息

| 訊息 | 方向 | 說明 |
|------|------|------|
| [S5F6](S5F6.md) | Equipment → Host | S5F5R 的直接回覆，攜帶 alarm 定義與狀態 |
| [S5F7R](S5F7R.md) | Host → Equipment | 查詢「已啟用」alarm（S5F5R 的子集版本） |
| [S5F1R](S5F1R.md) | Equipment → Host | 設備主動上報 alarm 事件（即時通知，非查詢） |
| [S5F3R](S5F3R.md) | Host → Equipment | 啟用或停用指定 alarm |
