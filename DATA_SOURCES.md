# A 股数据源强制规则（2026-09-14）

数据源固定为 **hithink-finance -> mootdx**，这是能力分工，不是失败回退。

- HiThink-Tech Financial-API / hithink-finance 是所有公开支持的 A 股信息的唯一主源：最新行情、历史日线、指数、行业/概念板块及成分、集合竞价、涨跌停、炸板、异动、热榜、龙虎榜、财务、估值、交易日历等。
- mootdx 只提供 1m/5m/15m/30m/60m 分钟 K 线；禁止用其报价、日线或财务替换同花顺主源。
- 禁用 Tushare，包括 replay、本地代理、自定义 HTTP 地址、Token、默认链路和回退链路。禁止自动改用东方财富、AKShare、BaoStock、网页抓价或其他来源。
- 主源/分钟源认证失败、超时、协议失败、数据为空、能力不支持时，明确报错并停止依赖该数据的判断。不得用旧缓存、静态文件、示例或模拟数据冒充当前市场数据。
- 历史报告和原始历史来源标签是审计记录，不得改写成同花顺数据。历史数据用于当前计算前必须重新从同花顺获取，或验证缓存来源为同花顺、日期/复权/证券代码满足请求；未知来源缓存不可作为当前依据。
- 密钥只读取 HITHINK_FINANCE_API_KEY 或用户级 credentials.env；只显示存在性和真实认证结果，不显示值、前后缀或长度，不写入 Git。
- 数据输出必须保留来源、原始时间、请求时间、标的、复权和单位。请求时间不是行情时间；没有原始时间时写“上游未提供”，不得声称已验证实时新鲜度。
- 同花顺公开不支持的新闻/公告原文、未来交易日历等必须报能力缺口，不能让分钟源补齐。术数推断不能代替市场数据。
- 使用现有同花顺授权与开源 mootdx，不增加付费数据源；开源许可证不代表账号额度无限或永久免费。

## 统一可执行入口

股票主项目的 `scoring_system/market_data.py` 为统一入口，`config/data_endpoints.json` 为公开能力目录。参数采用上游 REST 契约，不冒充旧 Tushare 字段。

```text
python -m scoring_system.market_data auth-status
python -m scoring_system.market_data snapshot --thscode 600519.SH
python -m scoring_system.market_data minutes --thscode 600519.SH --interval 1m --count 5
python -m scoring_system.market_data smoke --output reports/data-source-smoke.json
python -m scoring_system.market_data a-share.prices.historical --params '{"thscode":"600519.SH","interval":"1d","start":1788192000000,"end":1789401600000,"adjust":"forward"}' --output reports/daily.json
```

其他能力按 `--help` 和 `config/data_endpoints.json` 选择；只允许固定官方 HTTPS 域名。大量/全市场结果必须 `--output` 落盘；单页不代表全量，需按官方契约分页。

mootdx 无需密钥，默认行情服务器来自其发布包，可用 `MOOTDX_SERVER=IP:7709` 指定同协议服务器；连接失败仍报错，不换数据供应商。分钟线未复权，成交量保留手，成交额为元。

上游文档：https://github.com/HiThink-Tech/Financial-API ，https://github.com/mootdx/mootdx 。当前规则适用于本项目及关联股票 Skill；已打开的其他会话/其他机器必须重新加载更新后的仓库，不能声称远端推送会自动更新它们。
