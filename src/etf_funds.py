import json
import re
import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
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

def is_market_open() -> bool:
    now = datetime.now()
    wd = now.weekday()
    if wd >= 5:
        return False
    hour = now.hour
    minute = now.minute
    time_num = hour * 100 + minute
    return (930 <= time_num <= 1130) or (1300 <= time_num <= 1500)

def fetch_single_etf(code: str) -> Optional[Dict[str, Any]]:
    secid = get_secid(code)
    url = (
        f"http://push2.eastmoney.com/api/qt/stock/get"
        f"?secid={secid}"
        f"&fields=f43,f44,f45,f46,f47,f48,f57,f58,f170,f171"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        data = resp.json()
        if data.get("data"):
            return data["data"]
    except Exception:
        return None

def sanity_check_price(val: float) -> bool:
    return 0.5 <= val <= 200

def sanity_check_change(val: float) -> bool:
    return -20 <= val <= 20

def format_price(val) -> Tuple[str, Optional[float]]:
    if val is None or val == "-":
        return "待查", None
    try:
        v = float(val)
        if v == 0:
            return "休市", 0.0
        if v > 100:
            v = v / 1000
        if not sanity_check_price(v):
            return "数据异常", None
        if v >= 10:
            return f"{v:.3f}", v
        return f"{v:.4f}", v
    except (ValueError, TypeError):
        return "待查", None

def format_change(val) -> Tuple[str, Optional[float]]:
    if val is None or val == "-":
        return "待查", None
    try:
        v = float(val)
        if not sanity_check_change(v):
            return "数据异常", None
        return f"{v:.2f}%", v
    except (ValueError, TypeError):
        return "待查", None

def format_volume(val) -> Tuple[str, Optional[float]]:
    if val is None or val == "-":
        return "待查", None
    try:
        v = float(val)
        if v == 0:
            return "0", 0.0
        if v >= 1_0000_0000:
            return f"{v / 1_0000_0000:.2f}亿", v
        if v >= 1_0000:
            return f"{v / 1_0000:.2f}万", v
        return f"{v:.0f}", v
    except (ValueError, TypeError):
        return "待查", None

def format_premium(premium_val, price_val, iopv_val=None) -> Tuple[str, Optional[float]]:
    if premium_val is not None:
        try:
            p = float(premium_val)
            if p == 0:
                return "0.00%", 0.0
            if -20 <= p <= 20:
                return f"{p:.2f}%", p
        except (ValueError, TypeError):
            pass

    if price_val and iopv_val and iopv_val > 0:
        pct = (price_val - iopv_val) / iopv_val * 100
        return f"{pct:.2f}%", pct
    return "待查", None

def cross_validate_price(price_val: Optional[float], code: str) -> Optional[float]:
    if price_val is not None and price_val > 0:
        return price_val
    detail = fetch_single_etf(code)
    if detail:
        raw_f43 = detail.get("f43")
        if raw_f43:
            try:
                cv = float(raw_f43)
                if cv > 100:
                    cv = cv / 1000
                if sanity_check_price(cv):
                    return cv
            except (ValueError, TypeError):
                pass
    return None

def fetch_etf_data(retries: int = 2) -> List[ETFFund]:
    market_open = is_market_open()
    secids = ",".join(get_secid(f.code) for f in ETF_FUNDS)
    url = (
        f"http://push2.eastmoney.com/api/qt/ulist.np/get"
        f"?fields=f2,f3,f12,f14,f23,f37,f170,f171"
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
                    raw_iopv = item.get("f170")

                    price_str, price_num = format_price(raw_price)
                    change_str, change_num = format_change(raw_change)
                    volume_str, volume_num = format_volume(raw_volume)

                    iopv_num = None
                    if raw_iopv:
                        try:
                            iopv_num = float(raw_iopv)
                            if iopv_num > 100:
                                iopv_num = iopv_num / 1000
                        except (ValueError, TypeError):
                            pass
                    premium_str, premium_num = format_premium(raw_premium, price_num, iopv_num)

                    if not market_open and (price_num == 0.0 or price_str == "休市"):
                        price_str = "休市中"
                        change_str = "休市中"
                        premium_str = "休市中"
                        volume_str = "休市中"
                    elif market_open and price_num == 0.0:
                        price_str = "待查"
                        change_str = "待查"
                        premium_str = "待查"
                        volume_str = "待查"
                    elif price_str == "数据异常" or change_str == "数据异常":
                        fallback_price = cross_validate_price(price_num, code)
                        if fallback_price:
                            price_str = f"{fallback_price:.4f}"
                            price_num = fallback_price
                            change_str = "待查"

                    fund = ETFFund(
                        name=name or "未知",
                        code=code,
                        premium_rate=premium_str,
                        price=price_str,
                        change_pct=change_str,
                        volume=volume_str,
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