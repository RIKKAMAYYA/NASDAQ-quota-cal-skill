import requests, re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

for code in ['270042', '160213', '015062']:
    url = f'https://fundf10.eastmoney.com/jjfl_{code}.html'
    resp = requests.get(url, headers=headers, timeout=10)
    resp.encoding = 'utf-8'
    text = resp.text

    print(f"\n{'='*60}")
    print(f"=== {code} ===")
    print(f"{'='*60}")

    for kw in ['日累计申购限额', '单日累计购买上限', '交易状态', '限大额', '暂停申购']:
        for m in re.finditer(kw, text):
            ctx = text[max(0,m.start()-20):m.end()+100]
            clean = re.sub(r'<[^>]+>', ' ', ctx)
            clean = re.sub(r'\s+', ' ', clean).strip()
            print(f"  [{kw}] → {clean}")
