# ETF持仓数据说明

## 文件列表

本目录包含主要宽基ETF的成分股持仓数据：

- `ETF_hold_510300.SH.parquet` - 沪深300ETF持仓
- `ETF_hold_510500.SH.parquet` - 中证500ETF持仓
- `ETF_hold_512100.SH.parquet` - 中证1000ETF持仓

## 数据结构

| 字段名 | 类型 | 描述 |
|--------|------|------|
| fund_code | object | 基金代码 |
| end_date | datetime64 | 报告期结束日期 |
| stock_code | object | 成分股代码 |
| index_value | float64 | 持仓市值 |
| report_year | int64 | 报告年份 |
| report_type | object | 报告类型（中报/年报） |

## 数据说明

- **数据来源**: 基金定期报告
- **更新频率**: 半年度（中报、年报）
- **时间范围**: 历史至今
- **数据过滤**: 仅保留有效持仓（index_value > 0）

## 使用示例

```python
import pandas as pd

# 读取沪深300ETF持仓
df = pd.read_parquet('ETF_hold_510300.SH.parquet')

# 查看最新持仓
latest = df[df['end_date'] == df['end_date'].max()]
print(latest)
```

## 注意事项

- 仅包含中报和年报数据
- 持仓数据有一定时滞，以基金披露时间为准
- index_value 代表持仓市值，非持仓数量
