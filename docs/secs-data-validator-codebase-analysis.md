# validate_sml.py Codebase 分析

## 專案概述

這是一個 **SECS-II SML 格式驗證器**，用於驗證半導體設備通訊協議 SECS-II (SECS Message Language) 的訊息格式正確性。

## 核心架構

### 1. 程式結構

```
secs-data-validator/
├── scripts/
│   └── validate_sml.py          # 主驗證腳本
├── templates/
│   ├── example.sml              # 基本 SML 範例
│   ├── init-sequence.log        # 設備初始化序列日誌
│   ├── s2f23-trace.log          # 追蹤初始化日誌
│   └── s5f3-alarm.log           # 警報啟用/停用日誌
├── docs/
│   ├── cs/                      # C# 實作文檔 (secs4net)
│   └── python/                  # Python 實作文檔
└── SKILL.md                     # 技能描述文件
```

### 2. 核心類別

#### ValidationResult
**用途**: 驗證結果數據結構

**欄位**:
- `valid`: 布林值，表示格式是否正確
- `errors`: 錯誤列表 (`list[ValidationError]`)
- `warnings`: 警告列表 (`list[ValidationError]`)
- `message_count`: 訊息數量 (int)

**代碼**:
```python
@dataclass
class ValidationResult:
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    message_count: int = 0
```

#### ValidationError
**用途**: 單一錯誤/警告記錄

**欄位**:
- `line`: 行號 (int)
- `message`: 錯誤訊息 (str)

**代碼**:
```python
@dataclass
class ValidationError:
    line: int
    message: str

    def __str__(self):
        return f"  Line {self.line}: {self.message}"
```

#### SMLValidator
**用途**: 核心驗證邏輯引擎

**初始化參數**:
- `text`: 要驗證的 SML 文本

**主要方法**:

| 方法 | 用途 | 說明 |
|------|------|------|
| `validate()` | 主驗證方法 | 返回 ValidationResult |
| `_split_messages()` | 訊息分割 | 將文本分割為獨立訊息 |
| `_validate_message()` | 單一訊息驗證 | 驗證訊息頭和內容 |
| `_validate_header()` | 訊息頭驗證 | 檢查 SxFy 格式 |
| `_validate_item_structure()` | 項目結構驗證 | 驗證嵌套結構 |
| `_parse_item()` | 項目解析 | 遞迴解析項目 |
| `_validate_numeric()` | 數值範圍驗證 | 檢查數值是否在有效範圍 |

## 支援的 SECS-II 數據類型

### 基本類型
```python
VALID_ITEM_TYPES = {
    "L",        # List (列表)
    "A",        # ASCII (字符串)
    "J",        # JIS-8 字符串
    "B",        # Binary (二進制)
    "BOOLEAN",  # Boolean (布爾值)
    "U1", "U2", "U4", "U8",  # Unsigned integers (無符號整數)
    "I1", "I2", "I4", "I8",  # Signed integers (有符號整數)
    "F4", "F8",              # Floating point (浮點數)
}
```

### 數值範圍驗證
- **U1**: 0-255
- **U2**: 0-65,535
- **U4**: 0-4,294,967,295
- **U8**: 0-18,446,744,073,709,551,615
- **I1**: -128 到 127
- **I2**: -32,768 到 32,767
- **I4**: -2,147,483,648 到 2,147,483,647
- **I8**: -9,223,372,036,854,775,808 到 9,223,372,036,854,775,807

## 驗證流程

### 1. 訊息分割 (`_split_messages`)
- 以 `.` 作為訊息結束符
- 自動過濾日誌噪音：
  - 時間戳記行 (`2026-06-04 11:12:10...`)
  - 十六進制字節傾印 (`00 01 82 17...`)
  - 方向/元數據行 (`S2F23 H2E Wbit...`)
  - 空白主體標記 (`< >`)

### 2. 訊息頭驗證 (`_validate_header`)
- **格式**: `S{stream}F{function} W` (可選 W bit)
- **Stream 範圍**: 1-127
- **Function 範圍**: 0-255
- **規則**: 偶數 function 不應有 W bit (回覆訊息)

**驗證邏輯**:
```python
pattern = r"^S(\d+)F(\d+)(\s+W)?\s*$"
m = re.match(pattern, header, re.IGNORECASE)

if stream == 0:
    self.error(line_num, f"Stream 0 is reserved")
elif stream > 127:
    self.error(line_num, f"Stream {stream} out of range (1–127)")

if func > 255:
    self.error(line_num, f"Function {func} out of range (0–255)")

if func % 2 == 0 and m.group(3):
    self.warn(line_num, f"even function (reply) should not have W bit")
```

### 3. 項目結構驗證 (`_validate_item_structure`)
- **標記化** (`_tokenize`): 將輸入分割為標記
- **遞迴解析** (`_parse_item`): 解析嵌套結構
- **類型檢查**: 驗證每個項目的類型和值

**標記化模式**:
```python
token_pattern = r"'[^']*'|\"[^\"]*\"|0x[0-9A-Fa-f]+|<|>|\[|\]|[^\s<>\[\]]+"
```

### 4. 數值驗證 (`_validate_numeric`)
- 檢查數值是否在允許範圍內
- 驗證浮點數和整數格式
- 對超出範圍的值報告具體錯誤

## 日誌文件支援

### 智能過濾
驗證器會自動忽略日誌文件中的非 SML 內容：

| 過濾類型 | 示例 | 正則表達式 |
|---------|------|-----------|
| 時間戳記 | `2026-06-04 11:12:10.4189[TRACE]...` | `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}` |
| 十六進制傾印 | `00 01 82 17 00 00...` | `^([0-9A-Fa-f]{2} )+[0-9A-Fa-f]{2}$` |
| 元數據 | `S2F23 H2E Wbit(True)...` | `^S\d+F\d+\s+(H2E\|E2H)\s+Wbit` |
| 空主體 | `< >` | `^<\s*>$` |

### 格式正規化
- **引號標題**: `'S2F23'W` → `S2F23 W`
- **標題僅訊息**: 無 `.` 終止符的自動處理
- **布爾值**: 接受 `True`/`False` 和 `T`/`F`

## 使用範例

### 1. 基本 SML 驗證
```bash
python validate_sml.py file.sml
```

**輸入文件 (example.sml)**:
```
# S1F1 - Are You There (無 body)
S1F1 W
.

# S1F2 - On Line Data
S1F2
<L
  <A 'MDLN-001'>
  <A '1.0.0'>
>.
```

### 2. 日誌文件驗證
```bash
python validate_sml.py equipment.log
```

### 3. 標準輸入驗證
```bash
echo "S1F1 W\n." | python validate_sml.py
```

### 4. 批次驗證
```bash
for f in path/to/*.sml; do
  echo "=== $f ==="
  python validate_sml.py "$f"
  echo
done
```

## 技術特點

### 1. 零依賴設計
- **僅使用 Python 標準庫**: `re`, `sys`, `dataclasses`, `typing`
- **無需安裝第三方套件**
- **易於部署和移植**

### 2. 強大的錯誤報告
- **精確的行號定位**
- **清晰的錯誤訊息**
- **建議修正方法**

**錯誤報告格式**:
```
Source: file.sml
Messages found: 2

✗ INVALID — 2 error(s) found:
  Line 15: Invalid message header: 'S1F99' (expected SxFy or SxFy W)
  Line 25: Value 300 out of range for U1 (0–255)
```

### 3. 靈活的輸入支援
- **文件輸入**: 指定文件路徑
- **標準輸入**: 從管道讀取
- **混合日誌格式**: 自動過濾日誌噪音

### 4. 完整的 SECS-II 支援
- ✅ 所有標準數據類型
- ✅ 嵌套列表結構
- ✅ 數值範圍檢查
- ✅ 訊息頭驗證
- ✅ 日誌格式兼容

## 退出代碼

| 代碼 | 含義 |
|------|------|
| 0 | 驗證通過 (VALID) |
| 1 | 驗證失敗 (INVALID) |
| 2 | 文件錯誤 (File Not Found 或讀取錯誤) |

## 常見錯誤和修正

| 錯誤類型 | 示例 | 修正方法 |
|---------|------|---------|
| 無效訊息頭 | `S128F1` | Stream 範圍 1-127 |
| 未知類型 | `<X 123>` | 使用有效的類型如 `<U1 123>` |
| 數值超出範圍 | `<U1 300>` | 使用 `<U2 300>` 或調整數值 |
| 缺少終止符 | `S1F1 W` | 添加 `.` 在下一行 |
| 未引用字符串 | `<A text>` | 改為 `<A 'text'>` |
| 缺少閉合符號 | `<L <A 'x'` | 添加 `>.` 結尾 |

## 系統要求

- **Python 版本**: 3.7+ (推薦 3.10+)
- **依賴套件**: 無 (零依賴)
- **操作系統**: Windows, Linux, macOS

## 應用領域

這個驗證器主要用於：

1. **半導體設備通訊**
   - SECS/GEM 協議開發和測試
   - 設備通訊驗證

2. **設備集成**
   - EAP (Equipment Automation Program) 開發
   - MES 系統集成

3. **日誌分析**
   - SECS 通訊日誌的格式驗證
   - 問題診斷和調試

4. **協議調試**
   - 訊息格式問題診斷
   - 合規性檢查

## 設計優勢

### 1. 輕量級
- 單文件腳本 (~12KB)
- 無外部依賴
- 易於嵌入其他項目

### 2. 高效
- 快速驗證大型日誌文件
- 低記憶體占用
- 線性處複雜度

### 3. 準確
- 嚴格遵循 SECS-II 標準
- 完整的數據類型支援
- 精確的錯誤定位

### 4. 易用
- 清晰的錯誤報告
- 靈活的輸入方式
- 豐富的使用範例

## 相關文檔

- **SKILL.md**: 技能使用說明和觸發條件
- **docs/cs/**: C# 實作文檔 (secs4net 庫)
- **docs/python/**: Python 實作文檔
- **templates/**: 各種格式的範例文件

## 總結

這個 codebase 是一個專業領域工具，展現了針對特定工業標準的精簡而完整的實現。它通過嚴格的格式驗證、清晰的錯誤報告和靈活的輸入支援，為半導體設備通訊開發者提供了強大的調試和驗證工具。其零依賴設計使其易於在任何環境中部署和使用。