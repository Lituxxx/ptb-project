# 数据说明文档

## 文件结构

### EOD_PRICES.parquet
| 字段名 | 类型 | 描述 |
|--------|------|------|
| stock_code | object/category | 股票代码 |
| trade_date | object (原始数据未转换为datetime64) | 交易日期 |
| close_price | object/float64 (根据实际数据而定) | 收盘价（元） |
| adjusted_close | object/float64 (根据实际数据而定) | 复权收盘价（元） |
| adj_factor | object/float64 (根据实际数据而定) | 复权因子 |
| volume | object/float64 (根据实际数据而定) | 成交量（手） |
| turnover | object/float64 (根据实际数据而定) | 成交额 |

### INCOME.parquet
| 字段名 | 类型 | 描述 |
|--------|------|------|
| stock_code | category | 股票代码 |
| report_period | category | 报告期 |
| announce_date | category | 公告日期 |
| statement_type | category | 报表类型，详见下方说明 |
| revenue | float64 | 营业收入（元） |
| operating_profit | float64 | 营业利润（元） |
| net_profit_all | float64 | 净利润(含少数股东权益)（元） |
| net_profit_parent | float64 | 净利润(不含少数股东权益)（元） |
| total_operating_cost | float64 | 营业总成本（元） |
| operating_cost | float64 | 营业成本（元） |
| selling_expenses | float64 | 销售费用（元） |
| admin_expenses | float64 | 管理费用（元） |
| financial_expenses | float64 | 财务费用（元） |
| ebit | float64 | 息税前利润（元） |
| ebitda | float64 | 息税折旧摊销前利润（元） |
| eps_basic | float64 | 基本每股收益（元） |
| rd_expense | float64 | 研发费用（元） |

### BALANCE.parquet
| 字段名 | 类型 | 描述 |
|--------|------|------|
| stock_code | category | 股票代码 |
| report_period | category | 报告期 |
| announce_date | category | 公告日期 |
| statement_type | category | 报表类型，详见下方说明 |
| equity_all | float64 | 股东权益合计(含少数股东权益)（元） |
| equity_parent | float64 | 归属母公司股东权益（元） |
| total_shares | float64 | 总股本 |
| treasury_stock | float64 | 库存股 |
| short_term_debt | float64 | 短期借款（元） |
| long_term_debt | float64 | 长期借款（元） |
| bonds_payable | float64 | 应付债券（元） |
| cash | float64 | 货币资金（元） |
| settlement_reserve | float64 | 结算备付金（元） |
| total_liabilities | float64 | 负债合计（元） |
| total_assets | float64 | 资产总计（元） |

### CASHFLOW.parquet
| 字段名 | 类型 | 描述 |
|--------|------|------|
| stock_code | category | 股票代码 |
| report_period | category | 报告期 |
| announce_date | category | 公告日期 |
| statement_type | category | 报表类型，详见下方说明 |
| operating_cf | float64 | 经营活动现金流量净额（元） |
| capex | float64 | 购建固定资产、无形资产和其他长期资产支付的现金（元） |
| depreciation | float64 | 固定资产折旧（元） |
| amortization | float64 | 无形资产摊销（元） |
| operating_cf_indirect | float64 | 经营活动现金流量净额(间接法)（元） |
| fcff | float64 | 企业自由现金流量（元） |

### CAPITAL.parquet
| 字段名 | 类型 | 描述 |
|--------|------|------|
| stock_code | category | 股票代码 |
| change_date | category | 变动日期 |
| total_shares | float64 | 总股本 |
| float_shares | float64 | 流通股本(万股) |
| total_a_shares | float64 | A股总股本(万股) |
| float_a_shares | float64 | A股流通股本(万股) |

### DIVIDEND.parquet
| 字段名 | 类型 | 描述 |
|--------|------|------|
| stock_code | category | 股票代码 |
| announce_date | category | 公告日期 |
| ex_date | category | 除权除息日 |
| div_pre_tax | float64 | 税前每股派息（元） |
| div_after_tax | float64 | 税后每股派息（元） |
| progress | category | 方案进度 |
| base_shares | float64 | 分红基准股本(万股) |
| div_year | category | 分红所属年度 |
| currency | category | 货币类型 |
| is_no_div | int64 | 是否不分红(0-分红,1-不分红) |
| total_cash_div | float64 | 现金分红总额 |

## Statement Type 字段说明

财务报表（Income、Balance、Cashflow）中的 `statement_type` 字段用于区分不同版本的报表数据，共有4种类型：

| 报表类型 | 数据量占比 | 使用说明 |
|----------|-----------|----------|
| ORIGINAL | ~53% | 公司首次发布的合并报表数据 |
| ORIGINAL_VOID | ~2% | 标注为"更正前"的原始版本（已作废，仅供分析重复记录） |
| RESTATED | ~43% | 因会计准则变更、企业合并等原因对历史数据的重述 |
| RESTATED_VOID | ~0.75% | 追溯调整的"更正前"版本（已作废，仅供分析重复记录） |

### 数据提取说明

本数据集仅提取了上述4种报表类型（占历史数据的99%），其他类型（如差错更正CORRECTION、追溯调整的更正RESTATED_COR等）因数据量极少（<1%）且多为作废版本，未包含在本数据集中。

### 标记为 _VOID 的数据

- **ORIGINAL_VOID** : 这些是后来被更正的原始报表，当公司发现错误并发布更正时，原始版本被标记为"更正前"
- **RESTATED_VOID** : 这些是被进一步调整的追溯报表

这些 _VOID 数据主要用于构建时点数据时， 对于同一 `(stock_code, report_period)` 组合，优先使用最新公布日期的数据（更正或调整）。

## 注意事项

- **时间范围**：20130101至20251130
- **数据类型说明**: 此文档中的数据类型反映了实际存储的数据类型
- **Point-in-time基准**: 基于 `announce_date`（公告日期）字段
- **日期格式**: 所有日期字段为原始格式（YYYYMMDD字符串，未转换为datetime64）
- **分红数据**: 仅包含已实施完成（progress=3）的人民币现金分红
