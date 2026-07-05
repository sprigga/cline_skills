# secs-data-validator Skill 規範符合性分析

> 分析依據:[../cline-skills-guide.md](../cline-skills-guide.md)
> 分析對象:`.cline/skills/secs-data-validator/`
> 分析日期:2026-07-05

---

## 一、分析背景與評估標準

本文件評估 `.cline/skills/secs-data-validator` skill 是否符合《Cline Skills 結構與實作指南》之規範。

評估涵蓋下列面向:

| 面向 | 對應指南章節 |
|------|------------|
| 目錄結構 | 目錄結構 |
| SKILL.md 格式(含 frontmatter) | SKILL.md 格式 |
| `name` 欄位一致性 | SKILL.md 格式 / 命名規範 |
| `description` 撰寫品質 | 撰寫有效 Description |
| 附屬資源分層(scripts vs docs) | 附屬資源使用時機 |
| 三層漸進載入設計 | 什麼是 Skills? |

---

## 二、Skill 實際結構

```
.cline/skills/secs-data-validator/
├── SKILL.md
├── docs/
│   ├── sml-syntax.md
│   ├── cs/
│   │   ├── FORMAT_GUIDE.md
│   │   ├── STREAM2_UPDATES_VISUAL.md
│   │   ├── example/
│   │   ├── stream1/  ...  stream10/
│   └── python/
│       └── (per-stream handler guides)
├── scripts/
│   └── validate_sml.py
└── templates/
    ├── example.sml
    ├── init-sequence.log
    ├── s2f23-trace.log
    └── s5f3-alarm.log
```

---

## 三、逐項符合性檢查

### ✅ 符合的項目

| 規範要求 | 實際狀況 | 評語 |
|---------|---------|------|
| **`name` 與目錄一致(kebab-case)** | 目錄 `secs-data-validator` = `name: secs-data-validator` | ✓ 完全符合 |
| **目錄結構** | `SKILL.md` + `docs/` + `scripts/` + `templates/` | ✓ 與指南範本一致 |
| **`description` 品質** | 以動詞 `Validate` 開頭、列舉資料型別 `L/A/B/U1/U2/I4/F4`、含觸發短語、中英夾雜貼近使用者實際說法 | ✓ **典範等級**,符合「動詞開頭 + 觸發短語 + 具體領域」三要訣 |
| **description 長度 < 1024 字元** | 約 400 字元 | ✓ |
| **附屬資源分層** | 確定性驗證邏輯放 `scripts/validate_sml.py`(只有輸出進 context);彈性指引放 `docs/` | ✓ 完美示範「Scripts vs Instructions」分工哲學 |
| **漸進載入** | SKILL.md 本文精簡,把 SML 語法、各 Stream 實作都推到 `docs/` | ✓ SKILL.md 控制在 < 5k tokens 內 |

### ⚠️ 可改善項目(非違規,屬品質加分項)

#### 1. SKILL.md 末尾的「Example files」清單可精簡

- **位置**:`SKILL.md` 第 103–107 行
- **現況**:列出 4 個 template 檔的詳細說明
- **問題**:指南強調 Instructions 層應 < 5k tokens。此資訊可移至 `templates/README.md`,讓 SKILL.md 更輕量。
- **影響層級**:優化性質,目前並未超載。

#### 2. `STREAM2_UPDATES_VISUAL.md` 檔案位置不一致

- **位置**:`docs/cs/STREAM2_UPDATES_VISUAL.md`
- **現況**:其他 Stream 文件皆置於 `streamN/` 子目錄,此檔案單獨放在 `docs/cs/` 根目錄。
- **問題**:命名與組織方式與其他 Stream 不一致。
- **影響層級**:內容組織小瑕疵,不影響載入與觸發。

---

## 四、設計亮點(符合指南精神的典範做法)

### 1. `description` 撰寫品質優異

指南要求 description 應:
- 以**動詞開頭**
- 包含使用者可能說的**觸發短語**
- 提及**具體工具、檔案類型或領域**

本 skill 的 description:

```
Validate SECS-II SML message format. Use when checking SML syntax,
verifying item data types (L/A/B/U1/U2/I4/F4 etc.), validating SxFy
message headers, analyzing .sml files, or validating SECS log files
containing embedded SML. Triggers on phrases like "check SECS format",
"validate SML", "SECS-II message correct?", "檢查 SECS log", or
"幫我檢查 SML 格式".
```

— 三項要訣全部具備,可作為撰寫範例。

### 2. Scripts / Docs 分層符合「附屬資源使用時機」原則

指南指出:scripts 適合「確定性操作、需要可靠性、避免消耗 tokens 解釋邏輯」。

本 skill 將:
- **驗證邏輯**(判斷 U1 範圍、解析 SxFy、過濾 log 額外資訊)→ 放入 `scripts/validate_sml.py`
- **彈性指引**(各 Stream 訊息格式、SML 語法參考)→ 放入 `docs/`

腳本本體**不進 context、只有 stdout 進 context**,完美實踐指南原則。

---

## 五、總結

| 結論 | 說明 |
|------|------|
| **是否符合規範** | ✓ 符合 |
| **整體品質** | 良好,部分項目達典範等級 |
| **是否阻塞使用** | 否,可正常觸發與載入 |
| **建議整理項目** | (1) template 說明外移;(2) `STREAM2_UPDATES_VISUAL.md` 重新歸置 |

這份 skill 在 `description` 撰寫與 scripts/docs 分層兩點上,本身就是指南範例的優秀體現,可作為日後新增 skill 的參考標竿。
