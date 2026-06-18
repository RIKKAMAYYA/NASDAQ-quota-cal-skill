import requests, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
code = '270042'

print("=" * 60)
print("方法1: pingzhongdata 所有syl变量")
print("=" * 60)
url = f'https://fund.eastmoney.com/pingzhongdata/{code}.js'
resp = requests.get(url, headers=headers, timeout=8)
text = resp.text
for m in re.finditer(r'var\s+(syl_\w+)\s*=\s*"?([^";\n]+)', text):
    print(f"  {m.group(1)} = {m.group(2)}")

print("\n" + "=" * 60)
print("方法2: 基金净值页 jjjz")
print("=" * 60)
url2 = f'https://fundf10.eastmoney.com/jjjz_{code}.html'
resp2 = requests.get(url2, headers=headers, timeout=10)
resp2.encoding = 'utf-8'
clean = re.sub(r'<[^>]+>', ' | ', resp2.text)
clean = re.sub(r'\s+', ' ', clean)
for kw in ['近1年', '近3年', '近1月', '近3月', '近6月', '今年以来', '成立来']:
    idx = clean.find(kw)
    if idx >= 0:
        print(f"  {kw}: {clean[idx:idx+40].strip()}")

print("\n" + "=" * 60)
print("方法3: 业绩评价页 jdzf")
print("=" * 60)
url3 = f'https://fundf10.eastmoney.com/jdzf_{code}.html'
resp3 = requests.get(url3, headers=headers, timeout=10)
resp3.encoding = 'utf-8'
clean3 = re.sub(r'<[^>]+>', ' | ', resp3.text)
clean3 = re.sub(r'\s+', ' ', clean3)
for kw in ['近1年', '近3年', '近1月', '近3月', '近6月', '今年以来', '成立来']:
    idx = clean3.find(kw)
    if idx >= 0:
        print(f"  {kw}: {clean3[idx:idx+40].strip()}")

print("\n" + "=" * 60)
print("方法4: 基金详情API")
print("=" * 60)
url4 = f'http://fundgz.1234567.com.cn/js/{code}.js'
resp4 = requests.get(url4, headers=headers, timeout=10)
m4 = re.search(r'jsonpgz\((.+?)\);', resp4.text)
if m4:
    info = json.loads(m4.group(1))
    print(f"  {info}")

print("\n" + "=" * 60)
print("方法5: 东方财富基金数据API")
print("=" * 60)
url5 = f'http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex=1&pageSize=1'
try:
    resp5 = requests.get(url5, headers=headers, timeout=8)
    print(f"  {resp5.text[:300]}")
except Exception as e:
    print(f"  失败: {e}")
