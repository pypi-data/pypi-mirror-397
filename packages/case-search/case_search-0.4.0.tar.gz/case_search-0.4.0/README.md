# Case Search MCP Server

這是一個基於 **FastMCP** 框架開發的 Model Context Protocol (MCP) server，提供案件查詢和網路搜尋功能。

## ✨ 功能

- 📋 **營業人稅務資訊查詢**：根據統一編號 (ban) 查詢 CSV 檔案中的營業人稅務資訊
- ⚠️ **風險規則查詢**：根據稅務類型（營業稅、貨物稅、所得稅）取得對應的風險稽核規則
- 🔍 **網路搜尋**：透過 Serper API 進行 Google 網路搜尋
- 📊 以 JSON 格式回傳完整的資料
- 🔌 支援透過 stdio 與 MCP 客戶端通訊

## 安裝

### 從 PyPI 安裝（推薦）

```bash
# 使用 uvx 直接執行（不需要安裝）
uvx case-search

# 或安裝到本地環境
pip install case-search
```

### 從原始碼安裝

```bash
# 複製專案
git clone https://github.com/plion818/case-search.git
cd case-search

# 使用 uv 安裝相依套件
uv pip install -e .
```

## 使用方式

### 方式一：透過 uvx 執行（推薦）

最簡單的方式，不需要事先安裝：

```bash
uvx case-search
```

### 方式二：本地安裝後執行

```bash
# 安裝後執行
pip install case-search
case-search
```

### 方式三：在 Claude Desktop 中使用

編輯 Claude Desktop 設定檔，加入以下內容：

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**使用已發佈的套件（推薦）：**

```json
{
  "mcpServers": {
    "case-search": {
      "command": "uvx",
      "args": ["case-search"],
      "env": {
        "SERPER_API_KEY": "your-serper-api-key-here"
      }
    }
  }
}
```

**使用本地開發版本：**

```json
{
  "mcpServers": {
    "case-search": {
      "command": "uvx",
      "args": [
        "--from",
        "c:\\Users\\plion818\\2. Learn\\MCP\\case_search",
        "case-search"
      ],
      "env": {
        "SERPER_API_KEY": "your-serper-api-key-here"
      }
    }
  }
}
```

或使用絕對路徑指定 Python 執行檔：

```json
{
  "mcpServers": {
    "case-search": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\Users\\plion818\\2. Learn\\MCP\\case_search",
        "run",
        "case-search"
      ],
      "env": {
        "SERPER_API_KEY": "your-serper-api-key-here"
      }
    }
  }
}
```

> **📌 注意**：
> - 網路搜尋功能需要設定 `SERPER_API_KEY` 環境變數
> - 可在 [https://serper.dev](https://serper.dev) 免費註冊並取得 API Key
> - 免費方案提供每月 2,500 次搜尋額度

## 工具說明

### search_case

根據統一編號查詢營業人稅務資訊（不區分大小寫）。

**輸入參數：**
- `ban` (string, 必填): 統一編號（不區分大小寫），例如 "BAN1111", "ban1112", "Ban1113"

**輸出欄位說明：**
| 欄位名稱 | 說明 |
|---------|------|
| ban | 統一編號 (Key) |
| company_name | 營業人名稱 |
| industry_type | 行業別 |
| yr111_sales | 111年銷項金額 |
| yr111_purchases | 111年進項金額 |
| yr111_inventory | 111年期末存貨 |
| yr111_inv_sales_ratio | 111年存貨/銷項比 |
| yr111_inv_purch_ratio | 111年存貨/進項比 |
| yr111_vat_rate | 111年加值率 |
| yr111_tax_paid | 111年實繳稅額 |
| yr112_sales | 112年銷項金額 |
| yr112_purchases | 112年進項金額 |
| yr112_inventory | 112年期末存貨 |
| yr112_inv_sales_ratio | 112年存貨/銷項比 |
| yr112_inv_purch_ratio | 112年存貨/進項比 |
| yr112_vat_rate | 112年加值率 |
| yr112_tax_paid | 112年實繳稅額 |
| tax_method | 課稅方式 |

**輸出範例：**

```json
{
  "ban": "BAN1111",
  "company_name": "甲骨文五金批發有限公司",
  "industry_type": "批發業",
  "yr111_sales": 20000000,
  "yr111_purchases": 18000000,
  "yr111_inventory": 45000000,
  "yr111_inv_sales_ratio": 2.25,
  "yr111_inv_purch_ratio": 2.50,
  "yr111_vat_rate": 0.10,
  "yr111_tax_paid": 100000,
  "yr112_sales": 10000000,
  "yr112_purchases": 500000,
  "yr112_inventory": 60000000,
  "yr112_inv_sales_ratio": 6.00,
  "yr112_inv_purch_ratio": 120.00,
  "yr112_vat_rate": 0.95,
  "yr112_tax_paid": 475000,
  "tax_method": "1(一般課稅)"
}
```

如果找不到營業人，會回傳錯誤訊息：

```json
{
  "error": "找不到統一編號 BAN9999 的資料"
}
```

### get_risk_rules

取得指定稅務類型的風險稽核規則。

**輸入參數：**
- `tax_type` (下拉選單, 必填): 稅務類型
  - 營業稅
  - 貨物稅
  - 所得稅

**規則欄位說明：**
| 欄位名稱 | 說明 |
|---------|------|
| rule_id | 規則編號 |
| tax_type | 稅務類型 |
| rule_name | 規則名稱 |
| description | 規則描述 |
| risk_category | 風險等級 (High/Medium/Low) |
| logic_condition | 邏輯判斷條件 |
| suggested_action | 建議稽核行動 |

**輸出範例（規則已建立）：**

```json
{
  "status": "success",
  "tax_type": "營業稅",
  "rule_count": 7,
  "rules": [
    {
      "rule_id": "R001",
      "tax_type": "營業稅",
      "rule_name": "存貨積壓異常 (Phantom Inventory)",
      "description": "連續兩年存貨對銷項比率大於200%...",
      "risk_category": "High",
      "logic_condition": "(yr111_inv_sales_ratio > 2.0 AND yr112_inv_sales_ratio > 2.0) AND (yr112_inv_purch_ratio > 0.7)",
      "suggested_action": "實地盤點存貨、調閱進銷存明細帳、查核倉儲空間是否足夠"
    }
  ]
}
```

**輸出範例（規則尚未建立）：**

```json
{
  "status": "not_available",
  "message": "貨物稅規則內容尚未建立，請先建立相關規則",
  "tax_type": "貨物稅",
  "rules": []
}
```

### web_search

使用 Serper API 進行 Google 網路搜尋。

**輸入參數：**
- `query` (string, 必填): 搜尋關鍵字
- `num_results` (integer, 可選): 返回結果數量，預設為 10，最大為 100

**輸出範例：**

```json
{
  "searchParameters": {
    "q": "FastMCP Python",
    "type": "search",
    "engine": "google"
  },
  "organic": [
    {
      "title": "FastMCP - GitHub",
      "link": "https://github.com/jlowin/fastmcp",
      "snippet": "FastMCP is a high-level framework for building MCP servers...",
      "position": 1
    },
    {
      "title": "Model Context Protocol Documentation",
      "link": "https://modelcontextprotocol.io",
      "snippet": "The Model Context Protocol (MCP) is an open protocol...",
      "position": 2
    }
  ],
  "knowledgeGraph": {
    "title": "Python",
    "type": "Programming language",
    "description": "Python is a high-level programming language..."
  }
}
```

**錯誤處理：**

如果未設定 API Key：
```json
{
  "error": "請在環境變數中設定 SERPER_API_KEY。可在 https://serper.dev 取得 API Key"
}
```

如果 API Key 無效：
```json
{
  "error": "SERPER_API_KEY 無效，請確認 API Key 是否正確"
}
```

如果超過 API 請求限制：
```json
{
  "error": "API 請求次數超過限制，請稍後再試"
}
```

## 資料檔案

營業人稅務資料儲存在 `src/case_search/case_data.csv` 檔案中，包含以下欄位：

| 欄位名稱 | 說明 |
|---------|------|
| ban | 統一編號 (Key) |
| company_name | 營業人名稱 |
| industry_type | 行業別 |
| yr111_sales | 111年銷項金額 |
| yr111_purchases | 111年進項金額 |
| yr111_inventory | 111年期末存貨 |
| yr111_inv_sales_ratio | 111年存貨/銷項比 |
| yr111_inv_purch_ratio | 111年存貨/進項比 |
| yr111_vat_rate | 111年加值率 |
| yr111_tax_paid | 111年實繳稅額 |
| yr112_sales | 112年銷項金額 |
| yr112_purchases | 112年進項金額 |
| yr112_inventory | 112年期末存貨 |
| yr112_inv_sales_ratio | 112年存貨/銷項比 |
| yr112_inv_purch_ratio | 112年存貨/進項比 |
| yr112_vat_rate | 112年加值率 |
| yr112_tax_paid | 112年實繳稅額 |
| tax_method | 課稅方式 |

### tax_rules.csv

稅務風險規則儲存在 `src/case_search/tax_rules.csv` 檔案中，包含以下欄位：

| 欄位名稱 | 說明 |
|---------|------|
| rule_id | 規則編號 |
| tax_type | 稅務類型（營業稅/貨物稅/所得稅）|
| rule_name | 規則名稱 |
| description | 規則描述 |
| risk_category | 風險等級 (High/Medium/Low) |
| logic_condition | 邏輯判斷條件 |
| suggested_action | 建議稽核行動 |

**目前狀態：**
- ✅ 營業稅：7 條規則已建立
- ⏳ 貨物稅：規則尚未建立
- ⏳ 所得稅：規則尚未建立

## 開發

### 技術棧

本專案使用 Python 3.10+ 和以下主要技術：

- **FastMCP 框架**：基於官方 MCP SDK 的高層抽象，簡化 MCP server 開發
- **mcp[cli]** >= 1.24.0：Model Context Protocol 核心套件（已包含 httpx）
- **pandas** >= 2.0.0：資料處理
- **httpx**：HTTP 客戶端（透過 mcp[cli] 間接依賴）

### 專案結構

```
case_search/
├── src/
│   └── case_search/
│       ├── __init__.py      # FastMCP server 主程式
│       ├── case_data.csv    # 營業人稅務資料檔案
│       └── tax_rules.csv    # 稅務風險規則檔案
├── pyproject.toml           # 專案設定和依賴管理
├── uv.lock                  # 依賴鎖定檔案（確保可重現建置）
├── MANIFEST.in              # 打包時包含的額外檔案
└── README.md

```

### 關鍵概念

#### pyproject.toml 中的 keywords
- **目的**：幫助使用者在 PyPI 搜尋時找到您的套件
- **影響**：提升套件在 PyPI 的搜尋排名和可見度
- **管理**：手動編輯，精心挑選相關關鍵字

#### uv.lock 的作用
- **目的**：鎖定所有依賴的精確版本（包含間接依賴）
- **優勢**：
  - ✅ 確保團隊成員使用相同版本
  - ✅ 提供可重現的建置環境
  - ✅ 避免意外升級導致的問題
- **管理**：由 `uv` 自動生成，不要手動編輯

### 常用指令

```bash
# 安裝依賴
uv sync

# 執行 server
uv run case-search

# 使用 MCP Inspector 測試
npx @modelcontextprotocol/inspector uv run case-search

# 打包
uv build

# 發布到 PyPI
uv publish
```

## 授權

此專案由 plion818 開發維護。
