import os
from dataclasses import dataclass, field
from typing import List, Optional

SERVERCHAN_KEY = os.getenv("SERVERCHAN_KEY", "")

DAILY_BUDGET = float(os.getenv("DAILY_BUDGET", "210"))

@dataclass
class OTCFund:
    name: str
    code: str
    daily_limit: str = "待查"
    limit_amount: Optional[float] = None
    management_fee: str = "待查"
    custodian_fee: str = "待查"
    sales_service_fee: str = "0.00%"
    total_fee_pct: float = 0.0
    purchase_fee: str = "待查"
    tracking_error: str = "待查"
    tracking_error_avg: str = "待查"
    return_1y: str = "待查"
    return_3y: str = "待查"
    fund_size: str = "待查"
    date: str = ""

@dataclass
class ETFFund:
    name: str
    code: str
    premium_rate: str = "待查"
    price: str = "待查"
    change_pct: str = "待查"
    volume: str = "待查"

OTC_FUNDS: List[OTCFund] = [
    OTCFund(name="广发纳斯达克100A", code="270042"),
    OTCFund(name="国泰纳斯达克100", code="160213"),
    OTCFund(name="大成纳斯达克100A", code="000834"),
    OTCFund(name="华安纳斯达克100A", code="040046"),
    OTCFund(name="易方达纳斯达克100A", code="161130"),
    OTCFund(name="天弘纳斯达克100A", code="018043"),
    OTCFund(name="南方纳斯达克100A", code="016452"),
    OTCFund(name="南方纳斯达克100I", code="021000"),
    OTCFund(name="招商纳斯达克100A", code="019547"),
    OTCFund(name="华夏纳斯达克100A", code="015299"),
    OTCFund(name="嘉实纳斯达克100A", code="016532"),
    OTCFund(name="嘉实纳斯达克100I", code="021838"),
    OTCFund(name="博时纳斯达克100A", code="016055"),
    OTCFund(name="博时纳斯达克100I", code="024237"),
    OTCFund(name="华泰柏瑞纳斯达克100A", code="019524"),
    OTCFund(name="华泰柏瑞纳斯达克100I", code="022664"),
    OTCFund(name="建信纳斯达克100A", code="539001"),
    OTCFund(name="摩根纳斯达克100A", code="019172"),
    OTCFund(name="宝盈纳斯达克100A", code="019736"),
    OTCFund(name="汇添富纳斯达克100A", code="018966"),
    OTCFund(name="万家纳斯达克100A", code="019441"),
]

ETF_FUNDS: List[ETFFund] = [
    ETFFund(name="国泰纳斯达克100ETF", code="513100"),
    ETFFund(name="广发纳斯达克100ETF", code="159941"),
    ETFFund(name="华夏纳斯达克100ETF", code="513300"),
    ETFFund(name="易方达纳斯达克100ETF", code="159696"),
    ETFFund(name="博时纳斯达克100ETF", code="513390"),
    ETFFund(name="华安纳斯达克100ETF", code="159632"),
    ETFFund(name="汇添富纳斯达克100ETF", code="159660"),
    ETFFund(name="嘉实纳斯达克100ETF", code="159501"),
]