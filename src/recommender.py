from typing import List, Dict
from src.config import OTCFund, ETFFund

RECOMMENDATION_NOTES = {
    "270042": "广发纳指A，老牌QDII，规模大额度充足，首选配置",
    "160213": "国泰纳指，LOF可场内交易，限额可能偏紧",
    "000834": "大成纳指A，费率低，QDII额度较充裕",
    "040046": "华安纳指A，费率较高(1.20%)，可作为补充",
    "161130": "易方达纳指A，老牌基金公司，QDII额度管理严格",
    "018043": "天弘纳指A，新基金，当前暂停申购需关注恢复",
    "015062": "南方纳指I类，I类份额费率优，适合长持",
}

def compute_score(fund: OTCFund) -> float:
    fee_score = max(0, 100 - (fund.total_fee_pct - 0.80) * 200)
    if fund.limit_amount is None:
        limit_score = 50
    elif fund.limit_amount == float("inf"):
        limit_score = 100
    elif fund.limit_amount == 0:
        limit_score = 0
    else:
        log_val = min(100, max(0, (fund.limit_amount ** 0.3) / 50))
        limit_score = log_val * 100

    return fee_score * 0.6 + limit_score * 0.4

def get_buy_plan(otc_data: List[OTCFund]) -> str:
    scored = [(compute_score(f), f) for f in otc_data]
    scored.sort(key=lambda x: x[0], reverse=True)

    lines = []
    lines.append("### 📋 综合评分排名")
    lines.append("")
    lines.append("| 排名 | 基金名称 | 代码 | 总费率 | 每日限额 | 评分 |")
    lines.append("|:---:|---------|:----:|:-----:|:--------:|:---:|")
    for rank, (score, fund) in enumerate(scored, 1):
        limit_display = fund.daily_limit
        score_str = f"{score:.1f}"
        lines.append(f"| {rank} | {fund.name} | {fund.code} | {fund.total_fee_pct:.2f}% | {limit_display} | {score_str} |")

    lines.append("")
    lines.append("### 💡 每日购买建议")
    lines.append("")
    lines.append(f"> 📌 你有京东Plus会员，申购费已免除，以下方案基于长期持有(A类)设计")
    lines.append("")

    available = [(s, f) for s, f in scored if f.limit_amount != 0]
    if not available:
        lines.append("当前无基金可申购，请关注后续开放情况。")
        return "\n".join(lines)

    total_score = sum(s for s, _ in available)
    total_daily_capacity = 0
    for s, f in available:
        if f.limit_amount and f.limit_amount != float("inf"):
            total_daily_capacity += f.limit_amount

    lines.append("**推荐方案：**")
    lines.append("")
    if total_daily_capacity > 0:
        lines.append(f"每日合计可买入上限：约 **{format_amount(total_daily_capacity)}**")
        lines.append("")

    lines.append("| 基金名称 | 建议比例 | 每日建议金额 | 说明 |")
    lines.append("|:--------|:-------:|:----------:|:----|")
    for s, f in available[:5]:
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
    lines.append("2. **限额优先**：限额越高，可一次性投入更多")
    lines.append("3. **分散配置**：建议按评分比例分散到多只基金，降低单只限额不足风险")

    return "\n".join(lines)

def format_amount(val: float) -> str:
    if val == float("inf"):
        return "不限"
    if val >= 100000000:
        return f"{val/100000000:.2f}亿"
    if val >= 10000:
        return f"{val/10000:.1f}万"
    return f"{val:.0f}元"