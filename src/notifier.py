import requests
from typing import List
from src.config import SERVERCHAN_KEY, OTCFund, ETFFund
from src.recommender import get_buy_plan

def pad_cjk(text: str, width: int) -> str:
    cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    ascii_count = len(text) - cjk_count
    visual_width = cjk_count * 2 + ascii_count
    padding = max(0, width - visual_width)
    return text + " " * padding

def fmt_otc_table(data: List[OTCFund]) -> str:
    lines = []
    lines.append("```")
    h1 = pad_cjk("基金名称", 20)
    h2 = pad_cjk("代码", 8)
    h3 = pad_cjk("状态/限额", 18)
    h4 = pad_cjk("管理费", 7)
    h5 = pad_cjk("托管费", 7)
    h6 = pad_cjk("服务费", 7)
    h7 = pad_cjk("总费率", 7)
    h8 = pad_cjk("申购费", 7)
    h9 = pad_cjk("近1年", 8)
    h10 = pad_cjk("近3年", 8)
    lines.append(f"{h1} {h2} {h3} {h4} {h5} {h6} {h7} {h8} {h9} {h10}")
    lines.append("-" * 97)
    for f in data:
        d1 = pad_cjk(f.name, 20)
        d2 = pad_cjk(f.code, 8)
        d3 = pad_cjk(f.daily_limit, 18)
        d4 = pad_cjk(f.management_fee, 7)
        d5 = pad_cjk(f.custodian_fee, 7)
        d6 = pad_cjk(f.sales_service_fee, 7)
        d7 = pad_cjk(f"{f.total_fee_pct:.2f}%", 7)
        d8 = pad_cjk(f.purchase_fee, 7)
        d9 = pad_cjk(f.return_1y, 8)
        d10 = pad_cjk(f.return_3y, 8)
        lines.append(f"{d1} {d2} {d3} {d4} {d5} {d6} {d7} {d8} {d9} {d10}")
    lines.append("```")
    return "\n".join(lines)

def fmt_etf_table(data: List[ETFFund]) -> str:
    lines = []
    lines.append("```")
    h1 = pad_cjk("ETF名称", 18)
    h2 = pad_cjk("代码", 8)
    h3 = pad_cjk("最新价", 10)
    h4 = pad_cjk("涨跌幅", 10)
    h5 = pad_cjk("溢价率", 10)
    h6 = pad_cjk("成交额", 10)
    lines.append(f"{h1} {h2} {h3} {h4} {h5} {h6}")
    lines.append("-" * 66)
    for f in data:
        d1 = pad_cjk(f.name, 18)
        d2 = pad_cjk(f.code, 8)
        d3 = pad_cjk(f.price, 10)
        d4 = pad_cjk(f.change_pct, 10)
        d5 = pad_cjk(f.premium_rate, 10)
        d6 = pad_cjk(f.volume, 10)
        lines.append(f"{d1} {d2} {d3} {d4} {d5} {d6}")
    lines.append("```")
    return "\n".join(lines)

def fmt_premium_warnings(data: List[ETFFund]) -> str:
    warnings = []
    for f in data:
        if f.premium_rate in ("休市", "待查"):
            continue
        try:
            rate_str = f.premium_rate.replace("%", "")
            rate = float(rate_str)
            if rate > 5:
                warnings.append(f"🔴 **{f.name}**({f.code}) 溢价率 {f.premium_rate}，严重偏高！")
            elif rate > 3:
                warnings.append(f"🟡 {f.name}({f.code}) 溢价率 {f.premium_rate}，偏高需谨慎。")
        except (ValueError, AttributeError):
            pass
    if warnings:
        return "### 🚨 溢价预警\n\n" + "\n".join(warnings) + "\n"
    return ""

def build_message(otc_data: List[OTCFund], etf_data: List[ETFFund]) -> str:
    title = "📊 纳斯达克100基金日报"

    from datetime import datetime
    now = datetime.now()
    wd = now.weekday()
    hour = now.hour
    minute = now.minute
    time_num = hour * 100 + minute
    is_weekend = wd >= 5
    is_trading = (not is_weekend) and ((930 <= time_num <= 1130) or (1300 <= time_num <= 1500))

    status_emoji = "🟢" if is_trading else ("🔴" if is_weekend else "🟡")
    status_text = "交易中" if is_trading else ("周末休市" if is_weekend else "非交易时段")

    sections = []

    sections.append(f"> {status_emoji} 市场状态：{status_text}（{now.strftime('%Y-%m-%d %H:%M')}）")
    sections.append("")
    sections.append("> 💡 你有京东Plus会员，A类申购费已免除，实际只付管理费+托管费+销售服务费")
    sections.append("")

    sections.append("## 📈 场外基金（A类/I类）")
    sections.append("")
    sections.append(fmt_otc_table(otc_data))

    sections.append("")
    sections.append("## 📉 场内ETF溢价率")
    sections.append("")
    sections.append(fmt_etf_table(etf_data))

    sections.append("")
    premium_warn = fmt_premium_warnings(etf_data)
    if premium_warn:
        sections.append(premium_warn)

    sections.append("---")
    sections.append("")
    sections.append("## 🏆 每日购买方案推荐")
    sections.append("")
    sections.append(get_buy_plan(otc_data))

    return title, "\n".join(sections)

def send_serverchan(title: str, content: str) -> bool:
    if not SERVERCHAN_KEY:
        print("⚠️ 未设置 SERVERCHAN_KEY 环境变量，跳过推送")
        return False

    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    try:
        resp = requests.post(url, data={"title": title, "desp": content}, timeout=15)
        result = resp.json()
        if result.get("code") == 0:
            print("✅ Server酱推送成功!")
            return True
        else:
            print(f"❌ Server酱推送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ Server酱推送异常: {e}")
        return False

def notify(otc_data: List[OTCFund], etf_data: List[ETFFund]) -> bool:
    title, content = build_message(otc_data, etf_data)
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(content)
    print("=" * 60)
    return send_serverchan(title, content)