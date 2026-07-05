# Cline Skills 結構與實作指南

## 什麼是 Skills？

Skills 是**模組化指令集**，讓 Cline 能按需載入特定任務的操作指南。

與 Rules（永遠啟用、永遠佔用 context）不同，Skills 採用**三層漸進載入**：

| 層級 | 何時載入 | Token 成本 | 內容 |
|------|---------|------------|------|
| Metadata | 啟動時（永遠） | ~100 tokens/skill | `name` 和 `description` |
| Instructions | 觸發時 | < 5k tokens | SKILL.md 本文 |
| Resources | 按需 | 無上限 | 附屬檔案（docs/、scripts/） |

---

## 目錄結構

```
my-skill/
├── SKILL.md              # 必須：主要指令 + YAML frontmatter
├── docs/                 # 可選：詳細參考文件（按需載入）
│   └── advanced.md
├── templates/            # 可選：樣板檔案
│   └── config.yaml
└── scripts/              # 可選：工具腳本（只有輸出進 context）
    └── helper.py
```

---

## SKILL.md 格式

```markdown
---
name: my-skill          # 必須與目錄名稱完全一致（kebab-case）
description: 說明這個 skill 做什麼，以及何時使用（最多 1024 字元）
---

# My Skill

詳細的操作指令...

## 步驟
1. 第一步...
2. 第二步...
3. 進階用法請見 [advanced.md](docs/advanced.md)
```

**必填欄位：**
- `name`：必須與目錄名稱完全相同，使用 kebab-case
- `description`：Cline 靠這個決定何時啟動此 skill，**寫得好壞直接影響觸發準確度**

---

## 觸發方式

1. **自動匹配**：Cline 比對使用者請求與 skill description，自動用 `use_skill` 工具啟動
2. **Slash 指令**：在聊天輸入 `/skill-name`（如 `/secs-data-validator`）強制觸發

---

## Skills 存放位置

**專案級（建議版控共享）：**
```
.cline/skills/
.clinerules/skills/
.claude/skills/
```

**全域級（個人通用）：**
```
~/.cline/skills/           # macOS/Linux
C:\Users\USERNAME\.cline\skills\  # Windows
```

> 同名時，**全域 skill 優先於專案 skill**。

---

## 撰寫有效 Description

**好的範例：**
```
description: Validate SECS-II SML message format. Use when checking SML syntax,
verifying item data types, or analyzing .sml files for format errors.
```

**差的範例：**
```
description: Helps with SECS stuff.
```

要訣：
- 以**動詞開頭**（Validate、Deploy、Generate、Analyze）
- 包含使用者可能說的**觸發短語**
- 提及**具體工具、檔案類型或領域**

---

## 附屬資源使用時機

| 使用 Scripts | 使用 Instructions（SKILL.md） |
|-------------|------------------------------|
| 確定性操作（語法驗證、格式化） | 彈性指引（依情境調整） |
| 複雜計算 | 決策過程 |
| 需要可靠性的操作 | 可能因情境變化的步驟 |
| 避免消耗 tokens 解釋邏輯 | 最佳實踐與模式 |

Scripts 特別高效：一個 500 行的驗證腳本只把**輸出結果**送進 context，腳本本身不佔 tokens。

---

## 命名規範

**好的命名：**
- `aws-cdk-deploy`
- `secs-data-validator`
- `pr-review-checklist`
- `database-migration`

**避免：**
- `aws`（太模糊）
- `my_skill`（底線，不描述性）
- `DeployToAWS`（應用 kebab-case）
- `misc-helpers`（太泛用）

---

## 本專案 Skills 清單

| Skill 目錄 | 用途 | 附屬資源 |
|-----------|------|---------|
| `secs-data-validator/` | 驗證 SECS-II SML 訊息格式 | C#/Python 各 Stream 訊息實作文件、SML 語法參考、範例 SML 檔 |

---

## 參考資料

- [Cline Skills 官方文件](https://docs.cline.bot/customization/skills)
- [Cline Rules 文件](https://docs.cline.bot/customization/cline-rules)
- [Storage Locations](https://docs.cline.bot/getting-started/config#storage-locations)
