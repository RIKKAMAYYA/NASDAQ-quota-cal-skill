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
    time_num = now.hour * 100 + now.minute
    return (930 <= time_num <= 1130) or (1300 <= time_num <= 1500)

def fetch_etf_detail(code: str) -> Optional[Dict[str, Any]]:
    secid = get_secid(code)
    url = (
        f"http://push2.eastmoney.com/api/qt/stock/get"
        f"?secid={secid}"
        f"&fields=f43,f44,f45,f46,f47,f48,f57,f58,f169"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        data = resp.json()
        if data.get("data"):
            return data["data"]
    except Exception:
        return None

def fetch_etf_nav(code: str) -> Tuple[Optional[float], Optional[float], str]:
    url = f"http://fundgz.1234567.com.cn/js/{code}.js"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        match = re.search(r'jsonpgz\((.+?)\);', resp.text)
        if match:
            info = json.loads(match.group(1))
            dwjz = float(info.get('dwjz', 0))
            gsz = float(info.get('gsz', 0))
            gszzl = info.get('gszzl', '?')
            gztime = info.get('gztime', '')
            return dwjz, gsz, gszzl, gztime
    except Exception:
        pass
    return None, None, '?', ''

def calc_premium(price: float, nav: float) -> Optional[float]:
    if price > 0 and nav > 0:
        return (price - nav) / nav * 100
    return None

def parse_etf_detail(detail: Dict[str, Any], code: str) -> ETFFund:
    raw_price = detail.get("f43", 0)
    raw_volume_amount = detail.get("f48", 0.0)
    raw_change_pct = detail.get("f169", 0)
    name = detail.get("f58", "未知")

    price = raw_price / 1000 if raw_price else 0
    price_str = f"{price:.3f}" if price >= 10 else f"{price:.4f}" if price > 0 else "待查"

    change_pct = raw_change_pct / 10 if raw_change_pct else 0
    change_str = f"{change_pct:.2f}%" if raw_change_pct != 0 else "0.00%"

    volume_amount = raw_volume_amount
    if volume_amount >= 1_0000_0000:
        volume_str = f"{volume_amount / 1_0000_0000:.2f}亿"
    elif volume_amount >= 1_0000:
        volume_str = f"{volume_amount / 1_0000:.2f}万"
    elif volume_amount > 0:
        volume_str = f"{volume_amount:.0f}"
    else:
        volume_str = "0"

    premium_str = "待查"
    if price > 0:
        dwjz, gsz, gszzl, gztime = fetch_etf_nav(code)
        if gsz and gsz > 0:
            premium = calc_premium(price, gsz)
            if premium is not None:
                premium_str = f"{premium:.2f}%"
        elif dwjz and dwjz > 0:
            premium = calc_premium(price, dwjz)
            if premium is not None:
                premium_str = f"{premium:.2f}%"

    if price == 0:
        price_str = "待查"
        change_str = "待查"
        premium_str = "待查"
        volume_str = "0"

    return ETFFund(
        name=name,
        code=code,
        premium_rate=premium_str,
        price=price_str,
        change_pct=change_str,
        volume=volume_str,
    )

def fetch_etf_data() -> List[ETFFund]:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    results = []

    def process_etf(fund: ETFFund) -> ETFFund:
        detail = fetch_etf_detail(fund.code)
        if detail:
            etf = parse_etf_detail(detail, fund.code)
            print(f"  ✅ {etf.name} ({etf.code}) | 价格:{etf.price} | 涨跌:{etf.change_pct} | 溢价率:{etf.premium_rate} | 成交额:{etf.volume}")
            return etf
        else:
            print(f"  ❌ {fund.name} ({fund.code}) 获取失败")
            return fund

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_fund = {executor.submit(process_etf, fund): fund for fund in ETF_FUNDS}
        for future in as_completed(future_to_fund):
            try:
                results.append(future.result())
            except Exception as e:
                fund = future_to_fund[future]
                print(f"  ❌ {fund.name} ({fund.code}) 异常: {e}")
                results.append(fund)

    results.sort(key=lambda x: x.code)
    return results