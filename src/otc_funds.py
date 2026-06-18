import requests, re, json, time
from typing import List, Optional, Tuple
from src.config import OTCFund, OTC_FUNDS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def fetch_limit_from_fundf10(code: str) -> Tuple[str, Optional[float]]:
    url = f"https://fundf10.eastmoney.com/jjfl_{code}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = 'utf-8'
        text = resp.text

        upper_match = re.search(r'单日累计购买上限\s*([\d,.]+)\s*(万?元)?', text)
        status_match = re.search(r'交易状态[：:]\s*([^<]{2,30})', text)
        limit_match = re.search(r'日累计申购限额(?:</td><td[^>]*>)?\s*(无限额|[\d,.]+)\s*(万?元)?', text)

        upper_amount = None
        upper_display = ""
        if upper_match:
            upper_display = upper_match.group(1)
            unit = upper_match.group(2) or "元"
            upper_amount = parse_amount(upper_match.group(1))
            if '万' in unit and upper_amount:
                upper_amount *= 10000

        limit_amount = None
        limit_display = ""
        if limit_match:
            limit_display = limit_match.group(1)
            unit2 = limit_match.group(2) or "元"
            limit_amount = parse_amount(limit_match.group(1))
            if '万' in unit2 and limit_amount:
                limit_amount *= 10000

        if '无限额' in text and '日累计申购限额无限额' in text:
            return "无限额", float("inf")

        status = status_match.group(1).strip() if status_match else ""

        if '暂停申购' in status:
            if upper_amount is not None:
                return f"暂停申购(上限{upper_display}元)", upper_amount
            return "暂停申购", 0.0

        if '限大额' in status:
            if upper_amount is not None:
                return f"限大额(上限{upper_display}元)", upper_amount
            if limit_amount is not None:
                return f"限大额(上限{limit_display}元)", limit_amount
            return "限大额", 0.0

        if limit_amount is not None:
            return f"限额{limit_display}元", limit_amount

        if '暂停申购' in text:
            return "暂停申购", 0.0
        if '限大额' in text:
            return "限大额", 0.0
    except Exception as e:
        print(f"    [DEBUG] 费率页失败: {e}")
    return "待查", None

def parse_amount(text: str) -> Optional[float]:
    text = text.strip()
    if '无限额' in text:
        return float("inf")
    match = re.search(r'([\d,.]+)\s*(万?亿?元?)?', text)
    if match:
        num_str = match.group(1).replace(',', '')
        unit = (match.group(2) or '元').strip()
        try:
            num = float(num_str)
            if '亿' in unit:
                return num * 100000000
            if '万' in unit:
                return num * 10000
            return num
        except ValueError:
            pass
    return None

def fetch_fund_performance(code: str) -> Tuple[str, str, str]:
    url = f"https://fund.eastmoney.com/pingzhongdata/{code}.js"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        text = resp.text

        syl_1y = re.search(r'syl_1y\s*=\s*"?([^";\n]+)', text)
        syl_3y = re.search(r'syl_3y\s*=\s*"?([^";\n]+)', text)
        syl_1n = re.search(r'syl_1n\s*=\s*"?([^";\n]+)', text)

        y1 = f"{float(syl_1y.group(1)):.2f}%" if syl_1y else "待查"
        y3 = f"{float(syl_3y.group(1)):.2f}%" if syl_3y else "待查"

        size = "待查"
        size_match = re.search(r'Data_fluctuationScale\s*=\s*\{[^}]*"series":\[\{"name":"[^"]*","data":\[([^\]]+)\]', text)
        if size_match:
            nums = size_match.group(1).split(',')
            if nums:
                last = float(nums[-1].strip())
                if last >= 1:
                    size = f"{last:.2f}亿"
                else:
                    size = f"{last*10000:.0f}万"

        return y1, y3, size
    except Exception:
        return "待查", "待查", "待查"

def collect_otc_data() -> List[OTCFund]:
    results = []
    for fund in OTC_FUNDS:
        print(f"  正在查询: {fund.name} ({fund.code})")

        limit_text, limit_amount = fetch_limit_from_fundf10(fund.code)
        fund.daily_limit = limit_text
        fund.limit_amount = limit_amount
        print(f"    → 限额: {limit_text} (数值: {limit_amount})")

        y1, y3, size = fetch_fund_performance(fund.code)
        fund.return_1y = y1
        fund.return_3y = y3
        fund.fund_size = size
        print(f"    → 近1年: {y1}, 近3年: {y3}, 规模: {size}")

        time.sleep(0.3)
        results.append(fund)
    return results