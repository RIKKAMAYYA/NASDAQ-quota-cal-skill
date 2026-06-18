import sys
import os
import argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.otc_funds import collect_otc_data
from src.etf_funds import fetch_etf_data
from src.notifier import notify
from src.config import DAILY_BUDGET

def main():
    parser = argparse.ArgumentParser(description='纳斯达克100指数基金数据采集')
    parser.add_argument('-b', '--budget', type=float, default=None,
                        help=f'每日购买总额度（默认 {DAILY_BUDGET} 元，也可通过环境变量 DAILY_BUDGET 设置）')
    args = parser.parse_args()

    if args.budget is not None:
        os.environ['DAILY_BUDGET'] = str(args.budget)
        import src.config as config
        config.DAILY_BUDGET = args.budget
        import src.recommender as recommender
        recommender.DAILY_BUDGET = args.budget

    budget = args.budget if args.budget is not None else DAILY_BUDGET

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n📅 纳斯达克100指数基金数据采集 - {today}")
    print(f"💰 每日购买额度: {budget} 元\n")

    print("=" * 40)
    print("1️⃣  采集场外基金数据...")
    print("=" * 40)
    otc_data = collect_otc_data()

    print("\n" + "=" * 40)
    print("2️⃣  采集场内ETF数据...")
    print("=" * 40)
    etf_data = fetch_etf_data()

    print("\n" + "=" * 40)
    print("3️⃣  推送通知...")
    print("=" * 40)
    success = notify(otc_data, etf_data)

    if success:
        print(f"\n✅ {today} 数据采集完成，已推送!")
    else:
        print(f"\n⚠️  {today} 数据采集完成，但推送失败（请检查 SERVERCHAN_KEY 配置）。")

if __name__ == "__main__":
    main()