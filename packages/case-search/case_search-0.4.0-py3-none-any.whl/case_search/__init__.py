import os
from pathlib import Path
from typing import Literal
import httpx
import pandas as pd
from mcp.server.fastmcp import FastMCP


# 取得資料檔案路徑（從套件目錄讀取）
DATA_FILE = Path(__file__).parent / "case_data.csv"
TAX_RULES_FILE = Path(__file__).parent / "tax_rules.csv"

# Serper API 設定
SERPER_API_URL = "https://google.serper.dev/search"

# 建立 FastMCP server
mcp = FastMCP("case-search")


def load_case_data():
    """載入案件資料 CSV 檔案"""
    try:
        df = pd.read_csv(DATA_FILE)
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到資料檔案: {DATA_FILE}")
    except Exception as e:
        raise Exception(f"讀取資料檔案時發生錯誤: {e}")


def load_tax_rules():
    """載入稅務規則 CSV 檔案"""
    try:
        df = pd.read_csv(TAX_RULES_FILE)
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到稅務規則檔案: {TAX_RULES_FILE}")
    except Exception as e:
        raise Exception(f"讀取稅務規則檔案時發生錯誤: {e}")


def get_rules_by_tax_type(tax_type: str):
    """根據稅務類型篩選規則"""
    df = load_tax_rules()

    # 過濾符合稅務類型的規則
    filtered_rules = df[df['tax_type'] == tax_type]

    if filtered_rules.empty:
        return None

    # 轉換為字典列表
    rules_list = filtered_rules.to_dict('records')

    # 處理 NaN 值
    for rule in rules_list:
        for key, value in rule.items():
            if pd.isna(value):
                rule[key] = None

    return rules_list


def search_case_by_ban(ban: str):
    """根據統一編號(ban)查詢營業人稅務資訊（不區分大小寫）"""
    df = load_case_data()

    # 搜尋符合的營業人（不區分大小寫）
    result = df[df['ban'].str.upper() == ban.upper()]

    if result.empty:
        return None

    # 將結果轉換為字典並處理 NaN 值
    case_info = result.iloc[0].to_dict()

    # 將 NaN 轉換為 None（JSON null）
    for key, value in case_info.items():
        if pd.isna(value):
            case_info[key] = None

    return case_info


@mcp.tool()
def search_case(ban: str) -> dict:
    """
    根據統一編號(ban)查詢營業人稅務資訊（不區分大小寫）。
    輸入統一編號，回傳該營業人的完整稅務資訊，包括：
    - 基本資料：統一編號(ban)、營業人名稱(company_name)、行業別(industry_type)、課稅方式(tax_method)
    - 111年度：銷項金額(yr111_sales)、進項金額(yr111_purchases)、期末存貨(yr111_inventory)、
               存貨/銷項比(yr111_inv_sales_ratio)、存貨/進項比(yr111_inv_purch_ratio)、
               加值率(yr111_vat_rate)、實繳稅額(yr111_tax_paid)
    - 112年度：銷項金額(yr112_sales)、進項金額(yr112_purchases)、期末存貨(yr112_inventory)、
               存貨/銷項比(yr112_inv_sales_ratio)、存貨/進項比(yr112_inv_purch_ratio)、
               加值率(yr112_vat_rate)、實繳稅額(yr112_tax_paid)

    Args:
        ban: 統一編號（不區分大小寫），例如：BAN1111, ban1112, Ban1113
    """
    if not ban:
        raise ValueError("請提供統一編號(ban)")

    case_info = search_case_by_ban(ban)

    if case_info is None:
        raise ValueError(f"找不到統一編號 {ban} 的資料")

    return case_info


@mcp.tool()
def get_risk_rules(tax_type: Literal["營業稅", "貨物稅", "所得稅"]) -> dict:
    """
    取得指定稅務類型的風險稽核規則。
    輸入稅務類型（營業稅、貨物稅、所得稅），回傳該類型的所有風險規則資訊。

    每條規則包含：
    - rule_id: 規則編號
    - tax_type: 稅務類型
    - rule_name: 規則名稱
    - description: 規則描述
    - risk_category: 風險等級 (High/Medium/Low)
    - logic_condition: 邏輯判斷條件
    - suggested_action: 建議稽核行動

    Args:
        tax_type: 稅務類型，可選擇「營業稅」、「貨物稅」或「所得稅」

    Returns:
        包含規則列表的字典，若規則尚未建立則回傳提示訊息
    """
    if not tax_type:
        raise ValueError("請選擇稅務類型")

    rules = get_rules_by_tax_type(tax_type)

    if rules is None:
        return {
            "status": "not_available",
            "message": f"{tax_type}規則內容尚未建立，請先建立相關規則",
            "tax_type": tax_type,
            "rules": []
        }

    return {
        "status": "success",
        "tax_type": tax_type,
        "rule_count": len(rules),
        "rules": rules
    }


@mcp.tool()
async def web_search(query: str, num_results: int = 10) -> dict:
    """
    使用 Serper API 進行 Google 網路搜尋。
    需要在環境變數中設定 SERPER_API_KEY。

    Args:
        query: 搜尋關鍵字
        num_results: 返回結果數量，預設為 10，最大為 100

    Returns:
        搜尋結果，包含網頁標題、連結、摘要等資訊
    """
    if not query:
        raise ValueError("請提供搜尋關鍵字")

    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        raise ValueError(
            "請在環境變數中設定 SERPER_API_KEY。"
            "可在 https://serper.dev 取得 API Key"
        )

    # 限制結果數量
    num_results = min(max(1, num_results), 100)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SERPER_API_URL,
                headers={
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": query,
                    "num": num_results
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise ValueError("搜尋請求逾時，請稍後再試")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise ValueError("SERPER_API_KEY 無效，請確認 API Key 是否正確")
        elif e.response.status_code == 429:
            raise ValueError("API 請求次數超過限制，請稍後再試")
        else:
            raise ValueError(f"搜尋請求失敗: HTTP {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"搜尋時發生錯誤: {str(e)}")


def main() -> None:
    """主程式進入點"""
    mcp.run()
