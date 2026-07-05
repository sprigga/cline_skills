# S2F15R / S2F16 實務應用範例

**相關訊息：** [S2F15R](../stream2/S2F15R.md) · [S2F16](../stream2/S2F16.md) · [S2F13R](../stream2/S2F13R.md) · [S2F29R](../stream2/S2F29R.md)

---

## 核心概念：Equipment Constant 是什麼？

**EC（Equipment Constant）** 是設備上可由 Host 調整的運行參數。名稱雖叫「Constant」，但實際上是可在線設定的值：

| ECID | 名稱 | 典型用途 |
|------|------|----------|
| 1001 | T3Timeout | 回覆逾時秒數 |
| 2001 | DrillSpeed | 鑽孔轉速 (RPM) |
| 2002 | FeedRate | 進給速率 (mm/min) |
| 3001 | ReportingInterval | 狀態回報間隔 (秒) |

---

## 情境一：連線後調整設備工藝參數

Host 在連線建立後，先查詢現有 EC 值，再將製程配方參數推送給設備：

```
Host                                  Equipment (Schmoll S80)
  │                                         │
  │ ──S1F1R / S1F2──────────────────────── │  連線 handshake
  │                                         │
  │ ──S2F13R (L:0)─────────────────────── ▶│  查詢現有 EC 值
  │ ◀─S2F14 {L:3                           │
  │      {L:2 ECID=2001 ECV=3000}          │  鑽速目前: 3000 RPM
  │      {L:2 ECID=2002 ECV=800}           │  進給目前: 800 mm/min
  │      {L:2 ECID=3001 ECV=5}} ──────── │  回報間隔: 5 秒
  │                                         │
  │ ──S2F15R {L:2                           │  Host 推送新參數
  │      {L:2 ECID=2001 ECV=3500}          │  鑽速改為: 3500 RPM
  │      {L:2 ECID=2002 ECV=1000}} ──────►│  進給改為: 1000 mm/min
  │ ◀─S2F16 B:1 EAC=0x00 ────────────── │  設備接受（全部成功）
```

---

## 情境二：secs4net C# 實作

S2F15R 屬於 Host 主動送出，加在 `OutboundCommands.cs` 中，與現有的 `SendS2F41AndWaitS2F42Async` 同級：

```csharp
// OutboundCommands.cs 新增方法
internal static async Task<bool> SendS2F15AndWaitS2F16Async(
    ISecsGem secsGem,
    IEnumerable<(uint ecid, string ecv)> constants,
    CancellationToken ct)
{
    var items = constants
        .Select(c => L(U4(c.ecid), A(c.ecv)))
        .ToArray();

    using var s2f15 = new SecsMessage(2, 15)
    {
        Name     = "NewEquipmentConstantSend",
        SecsItem = L(items),          // L:n { L:2 ECID ECV }
    };

    Console.WriteLine($"[TX] S2F15R ({items.Length} constants)");
    using var s2f16 = await secsGem.SendAsync(s2f15, ct);

    var root = s2f16.SecsItem;
    if (root is null || root.Format != SecsFormat.Binary || root.Count < 1)
    {
        Console.WriteLine("[ERROR] S2F16: expected EAC (B:1)");
        return false;
    }

    int eac = root.FirstValue<byte>();
    Console.WriteLine($"[RX] S2F16 EAC={eac} ({EacDescription(eac)})");
    return eac == 0;
}

private static string EacDescription(int eac) => eac switch
{
    0 => "OK — all constants set",
    1 => "At least one ECID does not exist",
    2 => "At least one ECV out of range",
    3 => "At least one ECV wrong type",
    _ => $"Unknown ({eac})",
};
```

呼叫方式（`Program.cs` 啟動序列，S1F15 之前）：

```csharp
await OutboundCommands.SendS2F15AndWaitS2F16Async(secsGem, new[]
{
    (2001u, "3500"),   // DrillSpeed = 3500 RPM
    (2002u, "1000"),   // FeedRate = 1000 mm/min
}, ct);
```

---

## EAC 錯誤處理策略

S2F16 的 EAC 只告訴你「有沒有錯」，**不告訴你哪個 ECID 出錯**。這是 SECS 協議的設計限制，實務上的對應策略如下：

| EAC | 意義 | 處理方式 |
|-----|------|----------|
| `0` | 全部成功 | 繼續啟動流程 |
| `1` | 至少一個 ECID 不存在 | 先送 S2F29R (L:0) 查詢設備支援的 EC 清單，比對找出問題 |
| `2` | 至少一個 ECV 超出範圍 | 先送 S2F13R (L:0) 查詢當前值與合法範圍，調整後重送 |
| `3` | 至少一個 ECV 型別錯誤 | 檢查是否送了 `A:` 但設備期待 `U4:` |

> **重要：** EAC 採「全部或全不」原則（類似 SQL transaction）— 任一 ECID/ECV 有問題，所有常數均不被設定。因此不要把無關的 ECID 混在同一個 S2F15 請求中。

---

## 整體 EC 管理工作流

```
連線建立後
    │
    ▼
S2F29R (L:0)  →  查詢所有 ECID + 名稱 + 合法範圍
    │
    ▼
S2F13R (L:0)  →  查詢所有 ECID 的當前值
    │
    ▼
[比對製程配方，找出需要調整的 ECID]
    │
    ▼
S2F15R        →  只送需要修改的 ECID（差異部分）
    │
    ▼
S2F16 EAC=0?  →  是 → 繼續啟動流程
               →  否 → 記錄錯誤，依 EAC 碼診斷問題
```

---

## S2F15 vs S2F41 的角色區別

| 訊息 | 用途 | 效果 |
|------|------|------|
| S2F15R | 設定 Equipment Constant | 持久設定，設備重啟後通常保留 |
| S2F41R | 執行 Host Command (RCMD) | 一次性操作，如 START / STOP / ABORT |
