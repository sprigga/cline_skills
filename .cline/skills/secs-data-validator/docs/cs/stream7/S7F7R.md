# S7F7R - Process Program ID Request

**Direction:** Sent by Equipment Only

---

| **S7F7R** | Process Program ID Request | Sent by Equipment Only |

### 用意與目的

S7F7R（**Process Program ID Request**）是 SECS-II Stream 7（製程程式管理）中**唯一由設備主動發起**的查詢訊息。設備送出一個 MID（Material ID，物料 ID），向 Host 詢問：「這個物料應該使用哪個製程程式（PPID）？」Host 以 S7F8 回覆，包含對應的 PPID 和 MID。

#### 在 GEM 工作流程中的定位

```
Host                                Equipment
  │                                     │
  │        (物料進入設備 Port)           │
  │                                     │
  │◀─── S7F7R (MID="LOT-A001-001") ────│  ← 本訊息：設備查詢物料對應配方
  │─── S7F8 (L:2 { PPID, MID }) ──────▶│  Host 回覆對應的製程程式 ID
  │                                     │
  │        (設備載入對應配方並開始製程)   │
```

S7F7R 是 **SEMI E40（Object Services）** 規範中「Material-to-Process-Program 映射」的核心訊息。典型使用情境：

- **自動配方選擇：** 物料（晶圓批次/卡匣）進入設備時，設備掃描條碼或 RFID 取得 MID，再向 Host 查詢應套用哪個配方。
- **MES 整合：** Host（MES/WCS）維護 MID→PPID 的映射表，設備不需要本地儲存此對應關係。
- **製程防呆：** 確保同一設備對不同批次使用正確配方，防止人工選擇錯誤。
- **追蹤與稽核：** Host 可記錄哪個批次使用了哪個配方，實現完整的製程追蹤。

#### 訊息名稱解析

| 部分 | 含義 |
|------|------|
| `S7` | Stream 7 — 製程程式管理 |
| `F7` | Function 7 — 第 7 號功能（Request） |
| `R` | Reply requested（需要回覆）— 設備期待收到 S7F8 作為配方 ID 回應 |

> **為何由設備主動發起（Equipment Only）？** Stream 7 的大多數訊息（S7F1R、S7F5R、S7F19R、S7F25R）是 Host 向設備查詢或傳送配方。S7F7R 反轉方向：設備在製程開始前，**必須**先向 Host 確認物料應使用的配方，這體現了 Host 是製程決策權威（Process Program Authority）的設計原則。

#### 與相關訊息的關係

| 訊息 | 方向 | 用途 |
|------|------|------|
| **S7F7R** | Equipment → Host | 送出 MID，請求對應的 PPID（本文件） |
| S7F8 | Host → Equipment | 回覆 L:2 { PPID, MID }，提供對應的製程程式 ID |
| S7F3R | Host/Equipment → 對方 | 傳送完整非格式化製程程式（PPID + PPBODY） |
| S7F5R | Host/Equipment → 對方 | 請求取回非格式化製程程式（以 PPID 為鍵） |
| S7F25R | Host/Equipment → 對方 | 請求取回格式化製程程式（以 PPID 為鍵） |
| S7F19R | Host → Equipment | 查詢設備上已存在的配方清單 |
| S7F23R | Host → Equipment | 上傳格式化製程程式至設備 |

---

### Format (TSN)

```
[MID]
```

**Format Explanation:**

這是一個**單項目訊息**，只有一個資料項目：

- **`[MID]`** — Material ID（物料 ID），型別 `A:16`（ASCII 字串，最大 16 字元）。SEMI E40 進一步規定 MID 型別必須為 `A:n`（可變長度 ASCII）。用來識別進入設備的物料（批次、卡匣、晶圓等）。

> **注意：** 雖然 MID 型別規格為 `A:16`，但 SEMI E40 允許更長的 MID（視廠商定義而定）。若 Host 收到的 MID 無對應記錄，應回覆 S7F8 包含空 PPID（`A:0`），表示查無對應配方。

---

### 資料型別說明與範例

S7F7R 只有一個資料項目 MID，型別固定為 `A`（ASCII 字串）。

#### 型別速查表

| 欄位 | SECS 型別 | 長度限制 | 說明 |
|------|-----------|----------|------|
| MID | `A` (ASCII) | 最大 16 字元（E40 允許更長） | 物料 ID，唯一識別進入設備的批次或晶圓 |

#### MID 型別：`A` (ASCII 字串)

MID 是**唯一**的資料項目，型別固定為 ASCII。MID 的命名格式由工廠、MES 系統或 SEMI E40 規範定義。

**secs4net 建立 S7F7R（設備端發送）：**

```csharp
// 設備掃描到物料 LOT-A001-001，向 Host 查詢對應配方
var msg = new SecsMessage(7, 7, replyExpected: true,
    Item.A("LOT-A001-001"));
```

**SML 表示法：**

```
S7F7R
'LOT-A001-001' A
.
```

**常見 MID 命名範例：**

| 場景 | MID 值 | 說明 |
|------|--------|------|
| 批次 ID | `"LOT-A001-001"` | 標準晶圓批次識別碼 |
| 卡匣條碼 | `"FOUP-2024-0042"` | FOUP 卡匣條碼掃描結果 |
| 晶圓序號 | `"WFR-300-0815"` | 單片晶圓序號 |
| 短代碼 | `"M0042"` | 簡短格式，MES 系統生成 |
| 空字串 | `""` | 部分設備在無法讀取 MID 時送出（視廠商實作） |

**secs4net 讀取收到的 S7F7R（Host 端 handler）：**

```csharp
public async Task HandleAsync(PrimaryMessageWrapper wrapper)
{
    var msg = wrapper.PrimaryMessage;
    // S7F7R 的 body 就是 MID 字串（Item.A 型別）
    string mid = msg.SecsItem?.GetValue<string>() ?? string.Empty;

    // 查詢 MES/Host 的 MID→PPID 映射表
    string? ppid = _materialRegistry.LookupPpid(mid);

    await wrapper.TryReplyAsync(BuildS7F8(mid, ppid ?? string.Empty));
}

private static SecsMessage BuildS7F8(string mid, string ppid) =>
    new SecsMessage(7, 8,
        Item.L(
            Item.A(ppid),   // PPID（空字串表示查無對應配方）
            Item.A(mid)     // 回傳原始 MID，供設備確認
        ));
```

#### 完整互動範例：設備查詢並解析回覆

```csharp
// 設備端：發送 S7F7R 並等待 S7F8
public async Task<string?> RequestPpidForMaterialAsync(
    ISecsGem secsGem, string mid, CancellationToken ct = default)
{
    var request = new SecsMessage(7, 7, replyExpected: true,
        Item.A(mid));

    SecsMessage reply = await secsGem.SendAsync(request, ct);

    // S7F8 結構：L:2 { PPID, MID }
    var body = reply.SecsItem;
    if (body is null || body.Count < 2) return null;

    string replyPpid = body[0].GetValue<string>();
    string replyMid  = body[1].GetValue<string>();

    // 空 PPID 表示 Host 查無此物料對應的配方
    if (string.IsNullOrEmpty(replyPpid))
    {
        Console.WriteLine($"[WARN] No PPID found for MID={mid}");
        return null;
    }

    // 驗證回覆的 MID 與請求一致（防止競態條件）
    if (replyMid != mid)
        Console.WriteLine($"[WARN] MID mismatch: sent={mid}, got={replyMid}");

    return replyPpid;
}
```

---

### 通訊流程

```
Host                                Equipment
  │                                     │
  │                                (物料進入 Load Port)
  │                                     │
  │◀─── S7F7R ──────────────────────────│
  │     Item.A("LOT-A001-001")          │  設備查詢 MID 對應配方
  │                                     │
  │─── S7F8 ───────────────────────────▶│
  │    L:2 {                            │
  │      A "ETCH_RECIPE_5NM"            │  ← PPID（配方名稱）
  │      A "LOT-A001-001"               │  ← MID 回傳確認
  │    }                                │
  │                                     │
  │                                (設備載入 ETCH_RECIPE_5NM 並開始製程)
```

> 若 MID 不存在對應記錄，Host 回覆 `L:2 { A"" A"LOT-A001-001" }` — PPID 為空字串，設備應停止進行製程並報警。

---

### C# secs4net 實作

#### Host 端：接收 S7F7R 並回覆 S7F8

```csharp
// Handlers/S7F7Handler.cs
using Secs4Net;

public sealed class S7F7Handler : IMessageHandler
{
    public int Stream   => 7;
    public int Function => 7;

    private readonly IMaterialRegistry _materialRegistry;

    public S7F7Handler(IMaterialRegistry materialRegistry)
        => _materialRegistry = materialRegistry;

    public async Task HandleAsync(PrimaryMessageWrapper wrapper)
    {
        var msg = wrapper.PrimaryMessage;
        string mid = msg.SecsItem?.GetValue<string>() ?? string.Empty;

        string? ppid = _materialRegistry.LookupPpid(mid);
        var reply = BuildS7F8(mid, ppid ?? string.Empty);

        await wrapper.TryReplyAsync(reply);
    }

    private static SecsMessage BuildS7F8(string mid, string ppid) =>
        new SecsMessage(7, 8,
            Item.L(
                Item.A(ppid),   // 空字串表示查無對應配方
                Item.A(mid)
            ));
}
```

#### 在 Program.cs 中註冊

```csharp
factory.Register(new S7F7Handler(materialRegistry));
```

---

### 單元測試

```csharp
public sealed class S7F7HandlerTests
{
    [Fact]
    public async Task ReturnsS7F8WithPpid_WhenMidIsKnown()
    {
        var registry = new FakeMaterialRegistry();
        registry.Register("LOT-A001-001", "ETCH_RECIPE_5NM");
        var handler = new S7F7Handler(registry);
        var request = new SecsMessage(7, 7, replyExpected: true,
            Item.A("LOT-A001-001"));

        var (replied, replyMsg) = await SimulateHandleAsync(handler, request);

        Assert.True(replied);
        Assert.Equal(7, replyMsg!.S);
        Assert.Equal(8, replyMsg.F);
        Assert.Equal("ETCH_RECIPE_5NM", replyMsg.SecsItem![0].GetValue<string>());
        Assert.Equal("LOT-A001-001",    replyMsg.SecsItem[1].GetValue<string>());
    }

    [Fact]
    public async Task ReturnsEmptyPpid_WhenMidNotFound()
    {
        var handler = new S7F7Handler(new FakeMaterialRegistry());
        var request = new SecsMessage(7, 7, replyExpected: true,
            Item.A("UNKNOWN-MID"));

        var (replied, replyMsg) = await SimulateHandleAsync(handler, request);

        Assert.True(replied);
        Assert.Equal("", replyMsg!.SecsItem![0].GetValue<string>()); // 空 PPID
        Assert.Equal("UNKNOWN-MID", replyMsg.SecsItem[1].GetValue<string>()); // MID 回傳
    }

    [Fact]
    public async Task HandlesEmptyMid()
    {
        var handler = new S7F7Handler(new FakeMaterialRegistry());
        var request = new SecsMessage(7, 7, replyExpected: true,
            Item.A(""));

        var (replied, _) = await SimulateHandleAsync(handler, request);
        Assert.True(replied);
    }
}
```

---

### S7F7R 與其他「以 ID 查詢」訊息的比較

| 特性 | S7F7R / S7F8 | S7F25R / S7F26 | S7F5R / S7F6 |
|------|--------------|----------------|--------------|
| 查詢鍵 | **MID**（物料 ID） | **PPID**（配方 ID） | **PPID**（配方 ID） |
| 查詢方向 | Equipment → Host | Host/Equip → 對方 | Host/Equip → 對方 |
| 回傳內容 | PPID（一個 ID 字串） | 完整格式化配方（L:4 巢狀） | 完整非格式化配方（ASCII body） |
| 使用時機 | 物料進站，查詢應使用的配方 | 拉取完整格式化配方內容 | 拉取完整非格式化配方內容 |
| 相關標準 | SEMI E40（物料服務） | SEMI E30 GEM #7（必要） | 選用，視設備規格 |
