# NASDAQ-quota-cal-skill

安装
``` sh
npx skills add https://github.com/RIKKAMAYYA/NASDAQ-quota-cal-skill.git -y -g --skill nasdaq-quota-cal 
```

每日统计国内跟踪纳斯达克100指数的场外基金限额/费率/跟踪误差，以及场内ETF溢价率，并生成每日购买方案，通过 Server酱 推送到微信。

## 功能

- **场外基金**（21只A类/I类）：每日限额、管理费/托管费/销售服务费、总费率、跟踪误差、近1年/近3年收益
- **场内ETF**（8只）：实时价格、涨跌幅、溢价率、成交额
- **购买方案**：按综合表现分（年化收益-跟踪误差×5）排序，优先买满低费率基金，支持自定义每日额度
- **溢价预警**：溢价率超3%黄色预警，超5%红色预警
- **并发查询**：8线程并发，21只基金3秒完成
- **数据交叉验证**：ETF溢价率用估算净值计算，与同花顺一致

## 快速开始

通过 `npx skills add` 安装后，skill 目录里已自带可运行脚本：

```bash
# 找到 npx 装出来的 skill 目录（一般是 ~/.claude/skills/nasdaq-quota-cal/）
cd ~/.claude/skills/nasdaq-quota-cal

# 安装依赖
pip install -r requirements.txt

# 配置 Server酱（可选，不配置则只打印不推送）
export SERVERCHAN_KEY="your_serverchan_key"

# 运行（默认每日额度210元）
python src/main.py

# 自定义每日额度
python src/main.py -b 500          # 命令行参数
DAILY_BUDGET=1000 python src/main.py  # 环境变量
```

如果你是从 GitHub 克隆仓库直接运行，则路径对应 `仓库根/.trae/skills/nasdaq-quota-cal/`：

```bash
cd /path/to/NASDAQ-quota-cal-skill/.trae/skills/nasdaq-quota-cal
pip install -r requirements.txt
python src/main.py
```

## 配置参数

| 参数 | 环境变量 | 命令行 | 默认值 | 说明 |
|------|---------|--------|--------|------|
| Server酱Key | `SERVERCHAN_KEY` | - | 空 | 微信推送密钥 |
| 每日购买额度 | `DAILY_BUDGET` | `-b` | 210 | 每日购买总额度（元） |

优先级：命令行参数 > 环境变量 > 默认值

## 数据源

| 数据 | 来源 | 接口 |
|------|------|------|
| 场外基金限额 | 天天基金网 | `fundf10.eastmoney.com/jjfl_{code}.html` |
| 场外基金费率 | 天天基金网 | `fundf10.eastmoney.com/jjfl_{code}.html` |
| 跟踪误差 | 天天基金网 | `fundf10.eastmoney.com/tsdata_{code}.html` |
| 近1年收益 | 天天基金网 | `pingzhongdata/{code}.js` → `syl_1n` |
| 近3年收益 | 天天基金网 | `fund.eastmoney.com/{code}.html` |
| ETF行情 | 东方财富 | `push2.eastmoney.com/api/qt/stock/get` |
| ETF估算净值 | 天天基金网 | `fundgz.1234567.com.cn/js/{code}.js` → `gsz` |

## 购买方案排序逻辑

1. **第一排序**：综合表现分 = 年化收益 - 跟踪误差×5
   - 有近3年数据 → 年化复利计算 `((1+r)^(1/3)-1)`
   - 无近3年数据 → 直接用近1年收益
2. **第二排序**：总费率（同表现下选低成本）
3. **分配策略**：从第一名开始买满其每日限额，剩余额度继续下一只，直到总额度分配完
4. 暂停申购的基金不参与分配

## 监控基金列表

### 场外基金（21只）

广发、国泰、大成、华安、易方达、天弘、南方(A+I)、招商、华夏、嘉实(A+I)、博时(A+I)、华泰柏瑞(A+I)、建信、摩根、宝盈、汇添富、万家

### 场内ETF（8只）

513100、159941、513300、159696、513390、159632、159660、159501

## 项目结构

```
NASDAQ-quota-cal-skill/
├── README.md
├── .gitignore
├── debug_*.py                # 调试脚本（开发用，不随 skill 一起发布）
└── .trae/skills/nasdaq-quota-cal/    # Skill 完整包（npx skills add 装的就是这里）
    ├── SKILL.md              # Trae Skill 定义
    ├── requirements.txt
    └── src/
        ├── config.py         # 基金列表 + 配置参数
        ├── otc_funds.py      # 场外基金数据采集（并发）
        ├── etf_funds.py      # 场内ETF数据采集（并发）
        ├── recommender.py    # 购买方案推荐
        ├── notifier.py       # 消息格式化 + Server酱推送
        └── main.py           # 主入口
```

> npx 装出来的目录里只包含 `.trae/skills/nasdaq-quota-cal/` 子树，
> 不包含仓库根的 `debug_*.py` 和 `README.md`。

## 定时运行

### macOS/Linux crontab

```bash
# 每天早上9点运行（路径换成实际 skill 安装位置）
0 9 * * * cd /path/to/nasdaq-quota-cal && DAILY_BUDGET=300 python3 src/main.py
```

### GitHub Actions

在仓库 Settings → Secrets 中添加 `SERVERCHAN_KEY` 和 `DAILY_BUDGET`，然后添加 workflow：

```yaml
name: Daily NASDAQ Fund Report
on:
  schedule:
    - cron: '0 1 * * *'  # UTC 1:00 = 北京时间 9:00
  workflow_dispatch:
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r .trae/skills/nasdaq-quota-cal/requirements.txt
      - run: python src/main.py
        working-directory: .trae/skills/nasdaq-quota-cal
        env:
          SERVERCHAN_KEY: ${{ secrets.SERVERCHAN_KEY }}
          DAILY_BUDGET: ${{ secrets.DAILY_BUDGET }}
```

## License

MIT
