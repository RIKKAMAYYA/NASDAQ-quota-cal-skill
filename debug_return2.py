import requests, re, json, time
from datetime import datetime, timedelta

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
code = '270042'

print("=" * 60)
print("方法1: 基金主页 fund.eastmoney.com/{code}.html")
print("=" * 60)
url = f'http://fund.eastmoney.com/{code}.html'
resp = requests.get(url, headers=headers, timeout=10)
resp.encoding = 'utf-8'
clean = re.sub(r'<[^>]+>', ' | ', resp.text)
clean = re.sub(r'\s+', ' ', clean)
for kw in ['近1年', '近3年', '近1月', '近3月', '近6月', '今年以来', '成立来']:
    idx = clean.find(kw)
    if idx >= 0:
        print(f"  {kw}: {clean[idx:idx+50].strip()}")

print("\n" + "=" * 60)
print("方法2: 从Data_netWorthTrend计算近3年")
print("=" * 60)
url2 = f'https://fund.eastmoney.com/pingzhongdata/{code}.js'
resp2 = requests.get(url2, headers=headers, timeout=8)
text2 = resp2.text

nwt_idx = text2.find('Data_netWorthTrend')
if nwt_idx >= 0:
    bracket_start = text2.find('[', nwt_idx)
    bracket_end = text2.find('];', bracket_start)
    if bracket_start >= 0 and bracket_end >= 0:
        nwt_json = text2[bracket_start:bracket_end+1]
        try:
            nwt_data = json.loads(nwt_json)
            print(f"  共 {len(nwt_data)} 条净值记录")
            if nwt_data:
                latest = nwt_data[-1]
                print(f"  最新: 日期={latest.get('x')}, 净值={latest.get('y')}")
                latest_date = datetime.fromtimestamp(latest['x']/1000)
                print(f"  最新日期: {latest_date.strftime('%Y-%m-%d')}")

                target_3y = latest_date - timedelta(days=365*3)
                target_1y = latest_date - timedelta(days=365)
                print(f"  3年前目标: {target_3y.strftime('%Y-%m-%d')}")

                nav_3y_ago = None
                nav_1y_ago = None
                for item in nwt_data:
                    item_date = datetime.fromtimestamp(item['x']/1000)
                    if nav_3y_ago is None and item_date >= target_3y:
                        nav_3y_ago = item['y']
                        date_3y = item_date
                    if nav_1y_ago is None and item_date >= target_1y:
                        nav_1y_ago = item['y']
                        date_1y = item_date
                        break

                latest_nav = latest['y']
                if nav_3y_ago:
                    ret_3y = (latest_nav - nav_3y_ago) / nav_3y_ago * 100
                    print(f"  3年前净值({date_3y.strftime('%Y-%m-%d')}): {nav_3y_ago}")
                    print(f"  近3年收益率: {ret_3y:.2f}%")
                if nav_1y_ago:
                    ret_1y = (latest_nav - nav_1y_ago) / nav_1y_ago * 100
                    print(f"  1年前净值({date_1y.strftime('%Y-%m-%d')}): {nav_1y_ago}")
                    print(f"  近1年收益率(计算): {ret_1y:.2f}%")
        except json.JSONDecodeError as e:
            print(f"  JSON解析失败: {e}")

print("\n" + "=" * 60)
print("方法3: 东方财富基金排名API")
print("=" * 60)
url3 = f'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=1nzf&st=desc&pi=1&pn=5&dx=1&v=1'
try:
    resp3 = requests.get(url3, headers={**headers, 'Referer': 'http://fund.eastmoney.com/'}, timeout=8)
    print(f"  {resp3.text[:400]}")
except Exception as e:
    print(f"  失败: {e}")
