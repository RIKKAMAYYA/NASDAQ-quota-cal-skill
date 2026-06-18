import requests, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

print("=" * 60)
print("1. ETF 个股API测试")
print("=" * 60)
codes = ['513100', '159941', '513300', '159696']
for code in codes:
    if code.startswith('51'):
        secid = f'1.{code}'
    else:
        secid = f'0.{code}'
    url = f'http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f170,f171,f169'
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        data = resp.json()
        d = data.get('data', {})
        print(f"\n--- {code} ---")
        print(f"  f43(最新价)={d.get('f43')}")
        print(f"  f44(最高)={d.get('f44')}")
        print(f"  f45(最低)={d.get('f45')}")
        print(f"  f46(开盘)={d.get('f46')}")
        print(f"  f47(成交量)={d.get('f47')}")
        print(f"  f48(成交额)={d.get('f48')}")
        print(f"  f169(涨跌幅)={d.get('f169')}")
        print(f"  f170(IOPV)={d.get('f170')}")
        print(f"  f171(溢价率)={d.get('f171')}")
        print(f"  f57(代码)={d.get('f57')}")
        print(f"  f58(名称)={d.get('f58')}")
    except Exception as e:
        print(f"  {code} 失败: {e}")

print("\n" + "=" * 60)
print("2. ETF 列表API测试")
print("=" * 60)
secids = '1.513100,0.159941,1.513300,0.159696,1.513390,0.159632,0.159660,0.159501'
url2 = f'http://push2.eastmoney.com/api/qt/ulist.np/get?fields=f2,f3,f12,f14,f23,f37,f170,f171&secids={secids}&ut=fa5fd1943c7b386f172d6893dbfd32bb'
try:
    resp2 = requests.get(url2, headers=headers, timeout=8)
    data2 = resp2.json()
    if data2.get('data') and data2['data'].get('diff'):
        for item in data2['data']['diff']:
            print(f"\n--- {item.get('f14','?')} ({item.get('f12','?')}) ---")
            print(f"  f2(价格)={item.get('f2')}")
            print(f"  f3(涨跌幅)={item.get('f3')}")
            print(f"  f23(溢价率?)={item.get('f23')}")
            print(f"  f37(成交额?)={item.get('f37')}")
            print(f"  f170(IOPV?)={item.get('f170')}")
            print(f"  f171(溢价率?)={item.get('f171')}")
except Exception as e:
    print(f"列表API失败: {e}")

print("\n" + "=" * 60)
print("3. 场外基金限额API测试")
print("=" * 60)
fund_codes = ['270042', '160213', '000834', '040046', '161130', '018043', '015062']
for fc in fund_codes:
    url3 = f'https://fund.eastmoney.com/pingzhongdata/{fc}.js'
    try:
        resp3 = requests.get(url3, headers=headers, timeout=8)
        text = resp3.text
        buy_idx = text.find('Data_buySedemption')
        if buy_idx >= 0:
            snippet = text[buy_idx:buy_idx+300]
            print(f"\n--- {fc} Data_buySedemption ---")
            print(f"  {snippet[:200]}")
        rate = re.search(r'fund_sourceRate="([^"]+)"', text)
        now_rate = re.search(r'fund_Rate="([^"]+)"', text)
        minsg = re.search(r'fund_minsg="([^"]+)"', text)
        syl_1n = re.search(r'syl_1n\s*=\s*"?([^";\n]+)', text)
        syl_1y = re.search(r'syl_1y\s*=\s*"?([^";\n]+)', text)
        syl_3y = re.search(r'syl_3y\s*=\s*"?([^";\n]+)', text)
        print(f"  原费率={rate.group(1) if rate else '?'} 现费率={now_rate.group(1) if now_rate else '?'} 最低申购={minsg.group(1) if minsg else '?'}")
        print(f"  近1年={syl_1y.group(1) if syl_1y else '?'} 近3年={syl_3y.group(3) if syl_3y else '?'} 成立来={syl_1n.group(1) if syl_1n else '?'}")
    except Exception as e:
        print(f"  {fc} 失败: {e}")

print("\n" + "=" * 60)
print("4. 同花顺ETF溢价率API测试")
print("=" * 60)
for code in ['513100', '159941']:
    try:
        url4 = f'http://stockpage.10jqka.com.cn/{code}/'
        resp4 = requests.get(url4, headers=headers, timeout=8)
        resp4.encoding = 'utf-8'
        text4 = resp4.text
        for kw in ['溢价', '折价', 'IOPV', '参考净值']:
            idx = text4.find(kw)
            if idx >= 0:
                print(f"\n--- {code} {kw} ---")
                print(f"  {text4[max(0,idx-50):idx+100]}")
    except Exception as e:
        print(f"  {code} 同花顺失败: {e}")