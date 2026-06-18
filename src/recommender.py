from typing import List, Dict
from src.config import OTCFund, ETFFund

RECOMMENDATION_NOTES = {
    "270042": "广发纳指A，老牌QDII，规模大",
    "160213": "国泰纳指，LOF可场内交易",
    "000834": "大成纳指A，费率1.00%",
    "040046": "华安纳指A，管理费0.60%较低",
    "161130": "易方达纳指A，总费率0.60%最低",
    "018043": "天弘纳指A，总费率0.60%最低",
    "021000": "南方纳指I，I类份额",
    "019547": "招商纳指A，总费率0.65%较低",
    "019441": "万家纳指A",
    "015299": "华夏纳指A",
    "016532": "嘉实纳指A，总费率0.60%最低",
    "021838": "嘉实纳指I",
    "016055": "博时纳指A，总费率0.65%",
    "024237": "博时纳指I",
    "019524": "华泰柏瑞纳指A，总费率0.65%",
    "022664": "华泰柏瑞纳指I",
    "539001": "建信纳指A，费率1.00%",
    "019172": "摩根纳指A，总费率0.60%最低",
    "019736": "宝盈纳指A，总费率0.65%",
    "018966": "汇添富纳指A，总费率0.65%",
    "016452": "南方纳指A，总费率0.65%",
}

DAILY_BUDGET = 210.0

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

def rank_key(fund: OTCFund):
    try:
        ret3y = float(fund.return_3y.replace('%', ''))
    except (ValueError, AttributeError):
        ret3y = None
    try:
        ret1y = float(fund.return_1y.replace('%', ''))
    except (ValueError, AttributeError):
        ret1y = None
    try:
        te = float(fund.tracking_error.replace('%', ''))
    except (ValueError, AttributeError):
        te = 999

    if ret3y is not None and ret3y > 0:
        annualized = ((1 + ret3y / 100) ** (1 / 3) - 1) * 100
        base_return = annualized
    elif ret1y is not None and ret1y > 0:
        base_return = ret1y
    else:
        base_return = 0

    performance = base_return - te * 5
    return (-performance, fund.total_fee_pct)

def get_buy_plan(otc_data: List[OTCFund]) -> str:
    scored = [(compute_score(f), f) for f in otc_data]
    scored.sort(key=lambda x: x[0], reverse=True)

    lines = []
    lines.append("### 📋 综合评分排名（费率40%+限额30%+跟踪误差30%）")
    lines.append("")
    lines.append("| 排名 | 基金名称 | 代码 | 总费率 | 跟踪误差 | 近1年 | 近3年 | 每日限额 | 可买 | 评分 |")
    lines.append("|:---:|---------|:----:|:-----:|:-------:|:----:|:----:|:--------:|:---:|:---:|")
    for rank, (score, fund) in enumerate(scored, 1):
        limit_display = fund.daily_limit
        buyable = "✅" if is_purchasable(fund) else "❌"
        lines.append(f"| {rank} | {fund.name} | {fund.code} | {fund.total_fee_pct:.2f}% | {fund.tracking_error} | {fund.return_1y} | {fund.return_3y} | {limit_display} | {buyable} | {score:.1f} |")

    lines.append("")
    lines.append("### 💡 每日购买方案（总额度210元）")
    lines.append("")
    lines.append("> 📌 优先级：综合表现分(收益-跟踪误差×5) → 总费率 → 买满额度")
    lines.append("> 📌 你有京东Plus会员，A类申购费已免除")
    lines.append("")

    available = [f for f in otc_data if is_purchasable(f)]
    if not available:
        lines.append("⚠️ 当前所有基金均暂停申购或限额为0，请关注后续开放情况。")
        return "\n".join(lines)

    available.sort(key=rank_key)

    budget = DAILY_BUDGET
    plan = []
    for fund in available:
        if budget <= 0:
            break
        limit = fund.limit_amount if fund.limit_amount and fund.limit_amount != float("inf") else budget
        buy_amount = min(limit, budget)
        if buy_amount > 0:
            plan.append((fund, buy_amount))
            budget -= buy_amount

    lines.append("| 优先级 | 基金名称 | 代码 | 总费率 | 跟踪误差 | 近3年 | 限额 | 建议买入 | 说明 |")
    lines.append("|:-----:|---------|:----:|:-----:|:-------:|:----:|:----:|:-------:|:----|")
    for i, (fund, amount) in enumerate(plan, 1):
        limit_str = format_amount(fund.limit_amount) if fund.limit_amount and fund.limit_amount != float("inf") else "不限"
        note = RECOMMENDATION_NOTES.get(fund.code, "")
        lines.append(f"| {i} | {fund.name} | {fund.code} | {fund.total_fee_pct:.2f}% | {fund.tracking_error} | {fund.return_3y} | {limit_str} | {format_amount(amount)} | {note} |")

    total_bought = DAILY_BUDGET - budget
    lines.append("")
    lines.append(f"**合计买入：{format_amount(total_bought)} / {format_amount(DAILY_BUDGET)}**")
    if budget > 0:
        lines.append(f"⚠️ 剩余额度 {format_amount(budget)} 无法分配（所有可买基金限额已用尽）")

    lines.append("")
    lines.append("**方案逻辑：**")
    lines.append("1. 第一排序：综合表现分 = 收益 - 跟踪误差×5（实际表现优先）")
    lines.append("   - 优先用近3年收益，无数据则用近1年")
    lines.append("   - 跟踪误差大但收益高 → 综合分不低，仍可排入")
    lines.append("2. 第二排序：总费率越低越优先（同表现下选低成本）")
    lines.append("3. 从第一名开始，**买满其每日限额**")
    lines.append("4. 剩余额度继续买下一只，直到210元分配完")
    lines.append("5. 暂停申购的基金不参与分配")

    return "\n".join(lines)

def format_amount(val: float) -> str:
    if val == float("inf"):
        return "不限"
    if val >= 100000000:
        return f"{val/100000000:.2f}亿"
    if val >= 10000:
        return f"{val/10000:.1f}万"
    return f"{val:.0f}元"