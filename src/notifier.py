import requests
from typing import List
from src.config import SERVERCHAN_KEY, OTCFund, ETFFund

def build_message(otc_data: List[OTCFund], etf_data: List[ETFFund]) -> str:
    title = "📊 纳斯达克100指数基金日报"

    lines = ["## 📈 场外基金限额/费率\n"]
    lines.append("| 基金名称 | 代码 | 每日限额 | 管理费 | 托管费 |")
    lines.append("|---------|------|---------|-------|-------|")
    for f in otc_data:
        lines.append(f"| {f.name} | {f.code} | {f.daily_limit} | {f.management_fee} | {f.custodian_fee} |")

    lines.append("\n## 📉 场内ETF溢价率\n")
    lines.append("| ETF名称 | 代码 | 最新价 | 涨跌幅 | 溢价率 | 成交额 |")
    lines.append("|--------|------|-------|-------|-------|-------|")
    for f in etf_data:
        lines.append(f"| {f.name} | {f.code} | {f.price} | {f.change_pct} | {f.premium_rate} | {f.volume} |")

    warnings = []
    for f in etf_data:
        try:
            rate_str = f.premium_rate.replace("%", "")
            rate = float(rate_str)
            if rate > 5:
                warnings.append(f"⚠️ **{f.name}**({f.code}) 溢价率高达 {f.premium_rate}，注意风险！")
            elif rate > 3:
                warnings.append(f"⚡ {f.name}({f.code}) 溢价率 {f.premium_rate}，偏高需谨慎。")
        except (ValueError, AttributeError):
            pass

    if warnings:
        lines.append("\n## 🚨 溢价预警\n")
        lines.extend(warnings)

    return title, "\n".join(lines)

def send_serverchan(title: str, content: str) -> bool:
    if not SERVERCHAN_KEY:
        print("错误: 未设置 SERVERCHAN_KEY 环境变量")
        return False

    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    try:
        resp = requests.post(url, data={"title": title, "desp": content}, timeout=15)
        result = resp.json()
        if result.get("code") == 0:
            print("Server酱推送成功!")
            return True
        else:
            print(f"Server酱推送失败: {result}")
            return False
    except Exception as e:
        print(f"Server酱推送异常: {e}")
        return False

def notify(otc_data: List[OTCFund], etf_data: List[ETFFund]) -> bool:
    title, content = build_message(otc_data, etf_data)
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(content)
    print("=" * 60)
    return send_serverchan(title, content)