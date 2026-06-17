import json
import re
import requests
import time
from typing import List, Dict, Any
from src.config import ETFFund, ETF_FUNDS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def get_secid(code: str) -> str:
    if code.startswith("51") or code.startswith("56"):
        return f"1.{code}"
    return f"0.{code}"

def fetch_etf_data(retries: int = 3) -> List[ETFFund]:
    secids = ",".join(get_secid(f.code) for f in ETF_FUNDS)
    url = (
        f"http://push2.eastmoney.com/api/qt/ulist.np/get"
        f"?fields=f2,f3,f12,f14,f23,f37"
        f"&secids={secids}"
        f"&ut=fa5fd1943c7b386f172d6893dbfd32bb"
    )
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            data = resp.json()
            results = []
            if data.get("data") and data["data"].get("diff"):
                for item in data["data"]["diff"]:
                    code = str(item.get("f12", ""))
                    name = item.get("f14", "")
                    raw_price = item.get("f2")
                    raw_change = item.get("f3")
                    raw_premium = item.get("f23")
                    raw_volume = item.get("f37")

                    price = format_price(raw_price)
                    change_pct = format_pct(raw_change)
                    premium_rate = format_pct(raw_premium)
                    volume = format_volume(raw_volume)

                    fund = ETFFund(
                        name=name or "未知",
                        code=code,
                        premium_rate=premium_rate,
                        price=price,
                        change_pct=change_pct,
                        volume=volume,
                    )
                    results.append(fund)
            if results:
                return results
            if attempt < retries - 1:
                time.sleep(1)
        except Exception as e:
            if attempt < retries - 1:
                print(f"  第{attempt+1}次获取ETF数据失败，重试中... ({e})")
                time.sleep(1)
            else:
                print(f"  获取ETF数据失败: {e}")
    return ETF_FUNDS

def format_price(val) -> str:
    if val is None or val == "-":
        return "待查"
    try:
        val = float(val)
        if val > 100:
            val = val / 1000
        if val >= 10:
            return f"{val:.3f}"
        return f"{val:.4f}"
    except (ValueError, TypeError):
        return "待查"

def format_pct(val) -> str:
    if val is None or val == "-":
        return "待查"
    try:
        return f"{float(val):.2f}%"
    except (ValueError, TypeError):
        return "待查"

def format_volume(val) -> str:
    if val is None or val == "-":
        return "待查"
    try:
        val = float(val)
        if val >= 1_0000_0000:
            return f"{val / 1_0000_0000:.2f}亿"
        if val >= 1_0000:
            return f"{val / 1_0000:.2f}万"
        return f"{val:.0f}"
    except (ValueError, TypeError):
        return "待查"