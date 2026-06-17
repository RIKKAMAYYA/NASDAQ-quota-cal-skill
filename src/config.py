import os
from dataclasses import dataclass, field
from typing import List

SERVERCHAN_KEY = os.getenv("SERVERCHAN_KEY", "")

@dataclass
class OTCFund:
    name: str
    code: str
    daily_limit: str = "待查"
    management_fee: str = "待查"
    custodian_fee: str = "待查"
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
    OTCFund(name="广发纳斯达克100指数C", code="006479"),
    OTCFund(name="国泰纳斯达克100指数", code="160213"),
    OTCFund(name="大成纳斯达克100指数A", code="000834"),
    OTCFund(name="大成纳斯达克100指数C", code="008971"),
    OTCFund(name="华安纳斯达克100指数A", code="040046"),
    OTCFund(name="华安纳斯达克100指数C", code="014978"),
    OTCFund(name="易方达纳斯达克100A", code="161130"),
    OTCFund(name="易方达纳斯达克100C", code="012870"),
    OTCFund(name="天弘纳斯达克100A", code="018043"),
    OTCFund(name="天弘纳斯达克100C", code="018044"),
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