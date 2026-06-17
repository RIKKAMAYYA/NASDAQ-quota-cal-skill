import re
import requests
import time
from typing import List, Optional, Tuple
from src.config import OTCFund, OTC_FUNDS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

LIMIT_KEYWORDS = [
    "单日累计申购限额", "日累计申购限额", "申购限额",
    "单日累计购买上限", "限购",
    "大额申购限额", "每日申购限额",
]

def parse_limit_amount(text: str) -> Tuple[str, Optional[float]]:
    unit_map = {"元": 1, "万": 10000, "万元": 10000, "亿": 100000000, "亿元": 100000000}
    amount_patterns = [
        r"(?:限额|上限|限购)[：:]\s*([\d,]+\.?\d*)\s*(元|万|万元|亿|亿元)?",
        r"([\d,]+\.?\d*)\s*(元|万|万元|亿|亿元)",
    ]
    for ap in amount_patterns:
        match = re.search(ap, text)
        if match:
            num_str = match.group(1).replace(",", "")
            unit = (match.group(2) or "元").strip()
            try:
                num = float(num_str)
                multiplier = unit_map.get(unit, 1)
                amount = num * multiplier
                return text.strip(), amount
            except ValueError:
                pass
    return text.strip(), None

def fetch_fund_limit_page(code: str) -> Tuple[str, Optional[float]]:
    url = f"http://fund.eastmoney.com/{code}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        text = resp.text

        for keyword in LIMIT_KEYWORDS:
            pattern = rf"{re.escape(keyword)}[：:]\s*([^<，。]+)"
            match = re.search(pattern, text)
            if match:
                raw = match.group(1).strip()
                label, amount = parse_limit_amount(f"{keyword}：{raw}")
                if amount is not None:
                    return raw, amount
                if "无限" in raw or "不限" in raw:
                    return "无限额", float("inf")
                return raw, amount

        general_patterns = [
            r"暂停申购",
            r"暂停大额申购",
            r"暂停交易",
        ]
        for gp in general_patterns:
            if re.search(gp, text):
                return re.search(gp, text).group(), 0.0
        return "无限额", float("inf")
    except Exception:
        return "查询失败", None

def fetch_fund_performance(code: str) -> Tuple[str, str, str]:
    url = f"http://fund.eastmoney.com/{code}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        text = resp.text

        size_match = re.search(r"(?:基金规模|资产规模)[：:]\s*([^<]+)", text)
        size = size_match.group(1).strip() if size_match else "待查"

        y1_match = re.search(r"近1年[：:]\s*<span[^>]*>([^<]+)", text)
        y1 = y1_match.group(1).strip() if y1_match else "待查"

        y3_match = re.search(r"近3年[：:]\s*<span[^>]*>([^<]+)", text)
        y3 = y3_match.group(1).strip() if y3_match else "待查"

        return y1, y3, size
    except Exception:
        return "待查", "待查", "待查"

def collect_otc_data() -> List[OTCFund]:
    results = []
    for fund in OTC_FUNDS:
        print(f"  正在查询: {fund.name} ({fund.code})")
        limit_text, limit_amount = fetch_fund_limit_page(fund.code)
        fund.daily_limit = limit_text
        fund.limit_amount = limit_amount
        print(f"    → 限额: {limit_text}")

        y1, y3, size = fetch_fund_performance(fund.code)
        fund.return_1y = y1
        fund.return_3y = y3
        fund.fund_size = size

        time.sleep(0.5)
        results.append(fund)
    return results