import os
from dataclasses import dataclass, field
from typing import List, Optional

SERVERCHAN_KEY = os.getenv("SERVERCHAN_KEY", "")

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
    OTCFund(name="广发纳斯达克100指数A", code="270042"),
    OTCFund(name="国泰纳斯达克100指数", code="160213"),
    OTCFund(name="大成纳斯达克100指数A", code="000834"),
    OTCFund(name="华安纳斯达克100指数A", code="040046"),
    OTCFund(name="易方达纳斯达克100A", code="161130"),
    OTCFund(name="天弘纳斯达克100A", code="018043"),
    OTCFund(name="南方纳斯达克100I", code="021000"),
    OTCFund(name="招商纳斯达克100A", code="019547"),
    OTCFund(name="景顺长城纳斯达克100A", code="019118"),
    OTCFund(name="万家纳斯达克100A", code="019005"),
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