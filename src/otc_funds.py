import requests, re, json, time
from typing import List, Optional, Tuple
from src.config import OTCFund, OTC_FUNDS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def fetch_fund_info(code: str) -> dict:
    info = {
        "status": "待查",
        "limit_text": "待查",
        "limit_amount": None,
        "management_fee": "待查",
        "custodian_fee": "待查",
        "sales_service_fee": "0.00%",
        "purchase_fee_original": "待查",
        "purchase_fee_current": "待查",
        "tracking_error": "待查",
        "tracking_error_avg": "待查",
        "return_1y": "待查",
        "return_3y": "待查",
        "fund_size": "待查",
    }

    url = f'https://fundf10.eastmoney.com/jjfl_{code}.html'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = 'utf-8'
        text = resp.text

        clean = re.sub(r'<[^>]+>', ' | ', text)
        clean = re.sub(r'\s+', ' ', clean)

        mgmt = re.search(r'管理费率\s*\|\s*\|?\s*([\d.]+)%', clean)
        cust = re.search(r'托管费率\s*\|\s*\|?\s*([\d.]+)%', clean)
        ssf = re.search(r'销售服务费率\s*\|\s*\|?\s*([\d.]+|---)%', clean)
        if mgmt:
            info["management_fee"] = f"{mgmt.group(1)}%"
        if cust:
            info["custodian_fee"] = f"{cust.group(1)}%"
        if ssf:
            info["sales_service_fee"] = f"{ssf.group(1)}%" if ssf.group(1) != "---" else "0.00%"

        if '暂停申购' in clean:
            info["status"] = "暂停申购"
        elif '限大额' in clean:
            info["status"] = "限大额"
        else:
            info["status"] = "正常申购"

        upper_m = re.search(r'单日累计购买上限\s*([\d,.]+)\s*(万?元)?', clean)
        if upper_m:
            upper_val = upper_m.group(1)
            upper_unit = upper_m.group(2) or "元"
            info["limit_text"] = f"上限{upper_val}{upper_unit}"
            try:
                amount = float(upper_val.replace(',', ''))
                if '万' in upper_unit:
                    amount *= 10000
                info["limit_amount"] = amount
            except ValueError:
                pass

        limit_m = re.search(r'日累计申购限额\s*\|\s*\|?\s*(无限额|[\d,.]+)\s*(万?元)?', clean)
        if limit_m:
            if limit_m.group(1) == '无限额':
                info["limit_text"] = "无限额"
                info["limit_amount"] = float("inf")
            else:
                limit_val = limit_m.group(1)
                limit_unit = limit_m.group(2) or "元"
                if not upper_m:
                    info["limit_text"] = f"限额{limit_val}{limit_unit}"
                    try:
                        amount = float(limit_val.replace(',', ''))
                        if '万' in limit_unit:
                            amount *= 10000
                        info["limit_amount"] = amount
                    except ValueError:
                        pass
    except Exception as e:
        print(f"    [ERROR] fundf10 {code}: {e}")

    url_ts = f'https://fundf10.eastmoney.com/tsdata_{code}.html'
    try:
        resp_ts = requests.get(url_ts, headers=HEADERS, timeout=10)
        resp_ts.encoding = 'utf-8'
        text_ts = resp_ts.text
        clean_ts = re.sub(r'<[^>]+>', ' | ', text_ts)
        clean_ts = re.sub(r'\s+', ' ', clean_ts)

        te_match = re.search(r'纳斯达克100指数\s*\|\s*\|?\s*([\d.]+)%\s*\|\s*\|?\s*([\d.]+)%', clean_ts)
        if te_match:
            info["tracking_error"] = f"{te_match.group(1)}%"
            info["tracking_error_avg"] = f"{te_match.group(2)}%"
        else:
            te_single = re.search(r'年化跟踪误差[^%]*?([\d.]+)%', clean_ts)
            if te_single:
                info["tracking_error"] = f"{te_single.group(1)}%"
    except Exception as e:
        print(f"    [ERROR] tsdata {code}: {e}")

    url2 = f'https://fund.eastmoney.com/pingzhongdata/{code}.js'
    try:
        resp2 = requests.get(url2, headers=HEADERS, timeout=8)
        text2 = resp2.text

        source_rate = re.search(r'fund_sourceRate="([^"]+)"', text2)
        now_rate = re.search(r'fund_Rate="([^"]+)"', text2)
        if source_rate and source_rate.group(1):
            info["purchase_fee_original"] = f"{source_rate.group(1)}%"
        if now_rate and now_rate.group(1):
            info["purchase_fee_current"] = f"{now_rate.group(1)}%"

        syl_1y = re.search(r'syl_1y\s*=\s*"?([^";\n]+)', text2)
        syl_3y = re.search(r'syl_3y\s*=\s*"?([^";\n]+)', text2)
        if syl_1y and syl_1y.group(1):
            try:
                info["return_1y"] = f"{float(syl_1y.group(1)):.2f}%"
            except ValueError:
                pass
        if syl_3y and syl_3y.group(1):
            try:
                info["return_3y"] = f"{float(syl_3y.group(1)):.2f}%"
            except ValueError:
                pass

        size_match = re.search(r'Data_fluctuationScale\s*=\s*\{[^}]*"series":\[\{"name":"[^"]*","data":\[([^\]]+)\]', text2)
        if size_match:
            nums = size_match.group(1).split(',')
            if nums:
                last = float(nums[-1].strip())
                if last >= 1:
                    info["fund_size"] = f"{last:.2f}亿"
                else:
                    info["fund_size"] = f"{last*10000:.0f}万"
    except Exception as e:
        print(f"    [ERROR] pingzhongdata {code}: {e}")

    return info

def collect_otc_data() -> List[OTCFund]:
    results = []
    for fund in OTC_FUNDS:
        print(f"  正在查询: {fund.name} ({fund.code})")
        info = fetch_fund_info(fund.code)

        fund.management_fee = info["management_fee"]
        fund.custodian_fee = info["custodian_fee"]
        fund.sales_service_fee = info["sales_service_fee"]
        fund.purchase_fee = info["purchase_fee_current"]

        mgmt_val = float(info["management_fee"].replace('%', '')) if info["management_fee"] != "待查" else 0
        cust_val = float(info["custodian_fee"].replace('%', '')) if info["custodian_fee"] != "待查" else 0
        ssf_val = float(info["sales_service_fee"].replace('%', '')) if info["sales_service_fee"] not in ("待查", "0.00%", "---") else 0
        fund.total_fee_pct = mgmt_val + cust_val + ssf_val

        if info["status"] == "暂停申购":
            fund.daily_limit = f"暂停申购({info['limit_text']})" if info['limit_text'] != '待查' else "暂停申购"
            fund.limit_amount = info.get("limit_amount", 0.0)
        elif info["status"] == "限大额":
            fund.daily_limit = f"限大额({info['limit_text']})" if info['limit_text'] != '待查' else "限大额"
            fund.limit_amount = info.get("limit_amount")
        else:
            fund.daily_limit = info['limit_text'] if info['limit_text'] != '待查' else "无限额"
            fund.limit_amount = info.get("limit_amount", float("inf"))

        fund.return_1y = info["return_1y"]
        fund.return_3y = info["return_3y"]
        fund.fund_size = info["fund_size"]
        fund.tracking_error = info["tracking_error"]
        fund.tracking_error_avg = info["tracking_error_avg"]

        print(f"    → 状态: {info['status']} | 限额: {fund.daily_limit}")
        print(f"    → 管理费: {fund.management_fee} | 托管费: {fund.custodian_fee} | 销售服务费: {fund.sales_service_fee} | 总费率: {fund.total_fee_pct:.2f}%")
        print(f"    → 跟踪误差: {fund.tracking_error}(同类{fund.tracking_error_avg}) | 申购费: {info['purchase_fee_original']}→{info['purchase_fee_current']} | 近1年: {fund.return_1y} | 近3年: {fund.return_3y}")

        time.sleep(0.3)
        results.append(fund)
    return results