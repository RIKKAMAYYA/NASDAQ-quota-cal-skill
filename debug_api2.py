import requests, json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

print("=" * 60)
print("ETF 个股API - 全字段测试")
print("=" * 60)

codes = ['513100', '159941', '513300']
for code in codes:
    if code.startswith('51'):
        secid = f'1.{code}'
    else:
        secid = f'0.{code}'

    url = f'http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f169,f170,f171'
    resp = requests.get(url, headers=headers, timeout=8)
    data = resp.json().get('data', {})

    raw_price = data.get('f43', 0)
    raw_change = data.get('f169', 0)
    raw_f170 = data.get('f170', 0)
    raw_f171 = data.get('f171', 0)
    raw_amount = data.get('f48', 0)

    price = raw_price / 1000 if raw_price else 0
    change_pct = raw_change / 10 if raw_change else 0

    print(f"\n--- {data.get('f58','?')} ({code}) ---")
    print(f"  f43(价格原始)={raw_price} → 转换后={price:.4f}元")
    print(f"  f169(涨跌幅原始)={raw_change} → 转换后={change_pct:.2f}%")
    print(f"  f170(原始)={raw_f170}")
    print(f"  f171(原始)={raw_f171}")
    print(f"  f48(成交额原始)={raw_amount}")

    # 尝试不同的溢价率解析
    if raw_f171 != 0:
        print(f"  f171/100 = {raw_f171/100:.2f}%")
        print(f"  f171/10  = {raw_f171/10:.2f}%")
        print(f"  f171/1000= {raw_f171/1000:.4f}%")

print("\n" + "=" * 60)
print("场外基金费率页限额测试")
print("=" * 60)

fund_codes = ['270042', '160213', '000834', '040046', '161130', '018043', '015062']
for fc in fund_codes:
    url = f'https://fundf10.eastmoney.com/jjfl_{fc}.html'
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        text = resp.text

        import re
        found = False
        for kw in ['暂停大额申购', '暂停申购', '限额', '限购', '大额']:
            matches = [(m.start(), text[max(0,m.start()-30):m.end()+80]) for m in re.finditer(kw, text)]
            if matches:
                print(f"\n--- {fc} 关键词:{kw} ---")
                for pos, ctx in matches[:3]:
                    clean = re.sub(r'<[^>]+>', '', ctx)
                    print(f"  {clean.strip()}")
                found = True
        if not found:
            print(f"\n--- {fc} --- 未找到限额关键词")
    except Exception as e:
        print(f"  {fc} 失败: {e}")