# ETF Holdings Data Description

## File List

This directory contains constituent stock holdings data for major broad-based ETFs:

- `ETF_hold_510300.SH.parquet` - CSI 300 ETF Holdings
- `ETF_hold_510500.SH.parquet` - CSI 500 ETF Holdings
- `ETF_hold_512100.SH.parquet` - CSI 1000 ETF Holdings

## Data Structure

| Column | Type | Description |
|--------|------|-------------|
| fund_code | object | Fund code |
| end_date | datetime64 | Report period end date |
| stock_code | object | Constituent stock code |
| index_value | float64 | Holding market value |
| report_year | int64 | Report year |
| report_type | object | Report type (Semi-annual/Annual) |

## Data Notes

- **Data Source**: Fund periodic reports
- **Update Frequency**: Semi-annual (interim and annual reports)
- **Time Range**: Historical to present
- **Data Filter**: Only valid holdings (index_value > 0)

## Usage Example

```python
import pandas as pd

# Load CSI 300 ETF holdings
df = pd.read_parquet('ETF_hold_510300.SH.parquet')

# View latest holdings
latest = df[df['end_date'] == df['end_date'].max()]
print(latest)
```

## Notes

- Only includes semi-annual and annual report data
- Holdings data has certain lag, subject to fund disclosure time
- index_value represents holding market value, not quantity
