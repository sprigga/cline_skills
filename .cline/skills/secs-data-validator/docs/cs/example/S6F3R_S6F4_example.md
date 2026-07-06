# S6F3R / S6F4 實務應用範例

**相關訊息：** [S6F3R](../stream6/S6F3R.md) · [S6F4](../stream6/S6F4.md)

---

## 背景：S6F3 vs S6F11 的差異

S6F3（Discrete Variable Data Send）和 S6F11（Event Report Send）都屬於 Stream 6，但設計哲學不同：

| 特性 | S6F3 (Discrete Variable Data) | S6F11 (Event Report Send) |
|------|-------------------------------|---------------------------|
| 觸發方式 | 事件發生時，設備直接帶資料送出 | 透過 S2F33/S2F35/S2F37 預先設定 report |
| 資料結構 | `DSID + {DVNAME/DVVAL}` | `RPTID + {VID}` |
| 設定需求 | S2F15 設定 EC 即可 | 需要先定義 Report、Link Event、Enable Event |
| GEM 符合性 | 舊式、較少用於現代 GEM | GEM 標準推薦方式 |

本專案（Schmoll S80）實際使用 **S6F11**，S6F3 較常見於舊式設備或不支援完整 GEM report 設定流程的設備。

---

## 情境一：鑽孔完成後回報孔徑量測值

假設鑽孔機在 `ProcessingCompleted` 事件後，主動送出 S6F3R，附帶量測結果：

```
S6F3R  (Equipment → Host)
{L:3
  U4:1  [DATAID = 42]              ← 關聯同批多訊息
  U4:1  [CEID = 9]                 ← ProcessingCompleted
  {L:1
    {L:2
      A:n  [DSID = "DRILL_RESULTS"]
      {L:3
        {L:2  U4:1 [DVNAME=2001]  A:n [DVVAL="EQ-S80-01"]}   ← MachineInformation
        {L:2  U4:1 [DVNAME=2003]  A:n [DVVAL="PCB-PANEL-99"]} ← ProductionData
        {L:2  U4:1 [DVNAME=2005]  A:n [DVVAL="BREAK"]}        ← ToolBreak
      }
    }
  }
}

S6F4  (Host → Equipment)
B:1  [ACKC6 = 0x00]   ← 接受，繼續加工
```

---

## 情境二：前置作業（S2F15）

S6F3R 規格明確說明需透過 **S2F15** 設定設備常數，告訴設備哪些事件要觸發 S6F3 送出：

```
Host                              Equipment
  │                                   │
  │──S2F15R──────────────────────────►│  設定 EC，告知要回傳哪些離散變數
  │◄──S2F16 EAC=0x00─────────────────│  設備接受
  │                                   │
  │           [事件發生，例如分析完成]  │
  │◄──S6F3R──────────────────────────│  設備主動送 Discrete Variable Data
  │──S6F4 ACKC6=0x00────────────────►│  Host 確認接收
```

S6F3 的前置比 S6F11 輕量：S6F11 需要 S2F33 / S2F35 / S2F37 三步；S6F3 只需 S2F15 設一個 EC。

---

## 情境三：secs4net C# Handler 實作

對照本專案 `S6F11Handler.cs` 的結構，S6F3 handler 如下：

```csharp
// SecsApp/Handlers/S6F3Handler.cs
using Secs4Net;
using SecsApp.Protocol;
using static Secs4Net.Item;

namespace SecsApp.Handlers;

public sealed class S6F3Handler : IMessageHandler
{
    public int Stream   => 6;
    public int Function => 3;

    public async Task HandleAsync(PrimaryMessageWrapper wrapper, CancellationToken ct)
    {
        var root = wrapper.PrimaryMessage.SecsItem;

        // S6F3: L:3 { DATAID, CEID, L:n { L:2 DSID { L:m { L:2 DVNAME DVVAL } } } }
        if (root is null || root.Format != SecsFormat.List || root.Count < 3)
        {
            await ReplyAckAsync(wrapper, 0x01, ct);
            return;
        }

        ulong dataid = root[0].FirstValue<uint>();
        ulong ceid   = root[1].FirstValue<uint>();
        Console.WriteLine($"[RX] S6F3 DATAID={dataid} CEID={ceid} ({CollectionEventId.GetName(ceid)})");

        var dataSetList = root[2];                    // {L:n ...}
        for (int n = 0; n < dataSetList.Count; n++)
        {
            var ds   = dataSetList[n];                // {L:2 DSID {L:m ...}}
            var dsid = ds[0].GetString();
            var vars = ds[1];                         // {L:m {L:2 DVNAME DVVAL}}

            for (int m = 0; m < vars.Count; m++)
            {
                var pair   = vars[m];
                ulong  dvname = pair[0].FirstValue<uint>();
                string dvval  = pair[1].GetString();
                Console.WriteLine($"  DSID={dsid} DVNAME={dvname} DVVAL={dvval}");
            }
        }

        await ReplyAckAsync(wrapper, 0x00, ct);
    }

    private static async Task ReplyAckAsync(PrimaryMessageWrapper wrapper, byte ackc6, CancellationToken ct)
    {
        using var s6f4 = new SecsMessage(6, 4)
        {
            Name     = "DiscreteVarDataSendAck",
            SecsItem = B(ackc6),
        };
        await wrapper.TryReplyAsync(s6f4, ct);
        Console.WriteLine($"[TX] S6F4 ACKC6=0x{ackc6:X2}");
    }
}
```

啟用方式（`Program.cs`）：

```csharp
factory.Register(new S6F3Handler());
```

---

## S6F4 ACKC6 常用值

| ACKC6 | 意義 | 設備後續行為 |
|-------|------|-------------|
| `0x00` | OK — 接受 | 繼續加工 |
| `0x01` | BUSY — Host 忙碌 | 設備可能排隊或觸發警告 |
| `0x02` | DENIED — 拒絕 | 設備記錄錯誤 |

---

## 重要設計注意事項

**DATAID 跨訊息關聯：** 同一批加工可能拆成多個 S6F3 訊息送出，DATAID 相同代表屬於同一次事件，Host 可用它合併入同一筆資料庫記錄。

**DSID 是字串分類標籤：** 和 S6F11 的 `RPTID`（數字）不同，DSID 是 ASCII 字串（如 `"DRILL_RESULTS"`），讓 Host 在 parse 前就能分流處理邏輯。

**S6F4 的 ACKC6 不是裝飾：** 設備可根據 Host 回的 ACKC6 決定後續行為，非零值應觸發告警處理。
