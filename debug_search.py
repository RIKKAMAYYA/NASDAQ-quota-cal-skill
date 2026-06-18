import requests, re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

url = 'http://fund.eastmoney.com/js/fundcode_search.js'
resp = requests.get(url, headers=headers, timeout=15)
resp.encoding = 'utf-8'
text = resp.text

matches = re.findall(r'"(\d{6})","([^"]+)","([^"]+)","([^"]+)","([^"]+)"', text)

nasq_funds = []
for code, pinyin, name, type_name, pinyin_full in matches:
    if '纳斯达克100' in name or '纳指100' in name:
        nasq_funds.append((code, name, type_name, pinyin_full))

print(f"共找到 {len(nasq_funds)} 只纳斯达克100相关基金:\n")
print(f"{'代码':<8} {'类型':<10} {'名称'}")
print("-" * 60)
for code, name, type_name, _ in sorted(nasq_funds, key=lambda x: x[1]):
    print(f"{code:<8} {type_name:<10} {name}")
