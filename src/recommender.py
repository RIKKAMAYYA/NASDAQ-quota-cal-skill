from typing import List, Dict
from src.config import OTCFund, ETFFund

RECOMMENDATION_NOTES = {
    "270042": "广发纳指A，老牌QDII，规模大",
    "160213": "国泰纳指，LOF可场内交易",
    "000834": "大成纳指A，费率1.00%",
    "040046": "华安纳指A，管理费0.60%较低",
    "161130": "易方达纳指A，总费率0.60%最低",
    "018043": "天弘纳指A，总费率0.60%最低",
    "021000": "南方纳指I，I类份额，限大额1000元",
    "019547": "招商纳指A，总费率0.65%较低",
    "019005": "万家纳指A，总费率1.60%最高，不推荐",
}

def compute_score(fund: OTCFund) -> float:
    fee_score = max(0, 100 - (fund.total_fee_pct - 0.60) * 200)

    if fund.limit_amount is None:
        limit_score = 50
    elif fund.limit_amount == float("inf"):
        limit_score = 100
    elif fund.limit_amount == 0:
        limit_score = 0
    else:
        log_val = min(100, max(0, (fund.limit_amount ** 0.3) / 50))
        limit_score = log_val * 100

    te_score = 100
    try:
        te_val = float(fund.tracking_error.replace('%', ''))
        te_score = max(0, 100 - te_val * 30)
    except (ValueError, AttributeError):
        pass

    return fee_score * 0.4 + limit_score * 0.3 + te_score * 0.3

def is_purchasable(fund: OTCFund) -> bool:
    if fund.limit_amount is None:
        return False
    if fund.limit_amount == 0:
        return False
    if "暂停申购" in fund.daily_limit:
        return False
    return True

def get_buy_plan(otc_data: List[OTCFund]) -> str:
    scored = [(compute_score(f), f) for f in otc_data]
    scored.sort(key=lambda x: x[0], reverse=True)

    lines = []
    lines.append("### 📋 综合评分排名（费率40%+限额30%+跟踪误差30%）")
    lines.append("")
    lines.append("| 排名 | 基金名称 | 代码 | 总费率 | 跟踪误差 | 每日限额 | 可买 | 评分 |")
    lines.append("|:---:|---------|:----:|:-----:|:-------:|:--------:|:---:|:---:|")
    for rank, (score, fund) in enumerate(scored, 1):
        limit_display = fund.daily_limit
        buyable = "✅" if is_purchasable(fund) else "❌"
        lines.append(f"| {rank} | {fund.name} | {fund.code} | {fund.total_fee_pct:.2f}% | {fund.tracking_error} | {limit_display} | {buyable} | {score:.1f} |")

    lines.append("")
    lines.append("### 💡 每日购买建议")
    lines.append("")
    lines.append("> 📌 你有京东Plus会员，A类申购费已免除，实际只付管理费+托管费+销售服务费")
    lines.append("")

    available = [(s, f) for s, f in scored if is_purchasable(f)]
    if not available:
        lines.append("⚠️ 当前所有基金均暂停申购或限额为0，请关注后续开放情况。")
        return "\n".join(lines)

    total_score = sum(s for s, _ in available)
    total_daily_capacity = 0
    for s, f in available:
        if f.limit_amount and f.limit_amount != float("inf"):
            total_daily_capacity += f.limit_amount

    lines.append("**可申购基金推荐方案：**")
    lines.append("")
    if total_daily_capacity > 0:
        lines.append(f"每日合计可买入上限：约 **{format_amount(total_daily_capacity)}**")
        lines.append("")

    lines.append("| 基金名称 | 建议比例 | 每日建议金额 | 说明 |")
    lines.append("|:--------|:-------:|:----------:|:----|")
    for s, f in available:
        pct = s / total_score * 100
        note = RECOMMENDATION_NOTES.get(f.code, "")
        if f.limit_amount and f.limit_amount != float("inf") and f.limit_amount > 0:
            suggested = f.limit_amount * 0.8
            amount_str = f"≤ {format_amount(suggested)}"
        else:
            amount_str = "视资金量而定"
        lines.append(f"| {f.name} | {pct:.0f}% | {amount_str} | {note} |")

    lines.append("")
    lines.append("**优先级说明：**")
    lines.append("1. **费率优先**：总费率越低，长期持有成本越低")
    lines.append("2. **跟踪误差**：误差越小，跟踪指数越紧密")
    lines.append("3. **限额优先**：限额越高，可一次性投入更多")
    lines.append("4. **暂停申购的基金不纳入购买方案**，仅展示排名")

    return "\n".join(lines)

def format_amount(val: float) -> str:
    if val == float("inf"):
        return "不限"
    if val >= 100000000:
        return f"{val/100000000:.2f}亿"
    if val >= 10000:
        return f"{val/10000:.1f}万"
    return f"{val:.0f}元"