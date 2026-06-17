import re
import requests
from typing import List
from src.config import OTCFund, OTC_FUNDS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def fetch_fund_detail(code: str) -> dict:
    url = f"http://fundgz.1234567.com.cn/js/{code}.js"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        match = re.search(r"jsonpgz\((.+?)\);", resp.text)
        if match:
            return match.group(1)
    except Exception:
        return None

def fetch_fund_limit_page(code: str) -> str:
    url = f"http://fund.eastmoney.com/{code}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        text = resp.text
        limit_patterns = [
            r"单日累计申购限额[：:]\s*([^<]+)",
            r"申购限额[：:]\s*([^<]+)",
            r"限购[：:]\s*([^<]+)",
            r"单日累计购买上限[：:]\s*([^<]+)",
        ]
        for pattern in limit_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        if "暂停申购" in text or "暂停交易" in text:
            return "暂停申购"
        if "暂停大额申购" in text:
            return "暂停大额申购"
        return "未限购"
    except Exception:
        return "查询失败"

def fetch_fee_info(code: str) -> dict:
    url = f"http://fund.eastmoney.com/pingzhongdata/{code}.js"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        text = resp.text
        mgmt_fee = re.search(r"管理费率[：:]\s*([\d.]+%)", text)
        cust_fee = re.search(r"托管费率[：:]\s*([\d.]+%)", text)
        return {
            "management_fee": mgmt_fee.group(1) if mgmt_fee else "待查",
            "custodian_fee": cust_fee.group(1) if cust_fee else "待查",
        }
    except Exception:
        return {"management_fee": "待查", "custodian_fee": "待查"}

def collect_otc_data() -> List[OTCFund]:
    results = []
    for fund in OTC_FUNDS:
        print(f"  正在查询: {fund.name} ({fund.code})")
        limit = fetch_fund_limit_page(fund.code)
        fee = fetch_fee_info(fund.code)
        fund.daily_limit = limit
        fund.management_fee = fee["management_fee"]
        fund.custodian_fee = fee["custodian_fee"]
        results.append(fund)
    return results