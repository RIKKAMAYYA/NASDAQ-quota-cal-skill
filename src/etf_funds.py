import json
import re
import requests
from typing import List
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

def fetch_etf_data() -> List[ETFFund]:
    secids = ",".join(get_secid(f.code) for f in ETF_FUNDS)
    url = (
        f"https://push2.eastmoney.com/api/qt/ulist.np/get"
        f"?fields=f2,f3,f12,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f37,f38,f45,f46,f60,f62,f64,f65,f69,f70,f71,f72,f73,f74,f75,f78,f84,f87,f92,f97,f98,f100,f105,f111,f115,f116,f117,f120,f121,f122,f133,f136,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200,f201,f202,f203,f204,f205,f206,f207,f208,f209,f210,f211,f212"
        f"&secids={secids}"
        f"&ut=fa5fd1943c7b386f172d6893dbfd32bb"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        results = []
        if data.get("data") and data["data"].get("diff"):
            for item in data["data"]["diff"]:
                code = str(item.get("f12", ""))
                name = item.get("f14", "")
                price = item.get("f2", "-")
                change_pct = item.get("f3", "-")
                premium_rate = item.get("f23", "-")
                volume = item.get("f37", "-")

                if price != "-":
                    price = f"{price:.4f}" if price < 10 else f"{price:.3f}"
                if change_pct != "-":
                    change_pct = f"{change_pct:.2f}%"
                if premium_rate != "-":
                    premium_rate = f"{premium_rate:.2f}%"

                fund = ETFFund(
                    name=name or "未知",
                    code=code,
                    premium_rate=premium_rate,
                    price=price if price != "-" else "待查",
                    change_pct=change_pct,
                    volume=volume if volume != "-" else "待查",
                )
                results.append(fund)
        return results
    except Exception as e:
        print(f"  获取ETF数据失败: {e}")
        return ETF_FUNDS