# Industry Classification Data Description

## File List

- `AShareSWNIndustriesClass.parquet` - SWICS Industry Classification History (Full Version)
- `Stock_Industry_Year.parquet` - Stock-Year Industry Mapping (Simplified Version)

## Data Structure

### AShareSWNIndustriesClass.parquet

| Column | Type | Description |
|--------|------|-------------|
| S_INFO_WINDCODE | object | Stock code |
| SW_IND_CODE | object | SWICS industry code |
| ENTRY_DT | datetime64 | Entry date |
| REMOVE_DT | datetime64 | Removal date (null if still in industry) |
| CUR_SIGN | object | Current flag |
| INDUSTRIESNAME | object | Level-1 industry name |

### Stock_Industry_Year.parquet

| Column | Type | Description |
|--------|------|-------------|
| stock_code | object | Stock code |
| year | int64 | Year |
| industry_name | object | Level-1 industry name |

## Data Notes

- **Classification Standard**: SWICS (Shenwan Industry Classification Standard) - Level 1
- **Time Range**: 2010 to present
- **Update Logic**:
  - Full version retains all historical change records
  - Annual version uses January 1st snapshot, taking latest valid record

## Use Cases

### Case 1: Get industry classification for all stocks in a year

```python
import pandas as pd

df = pd.read_parquet('Stock_Industry_Year.parquet')
industry_2023 = df[df['year'] == 2023]
print(industry_2023)
```

### Case 2: Track industry change history for a stock

```python
df = pd.read_parquet('AShareSWNIndustriesClass.parquet')
history = df[df['S_INFO_WINDCODE'] == '000001.SZ']
print(history[['ENTRY_DT', 'REMOVE_DT', 'INDUSTRIESNAME']])
```

## Notes

- Some stocks may have multiple records at same point in time; annual version auto-deduplicated (keeping latest)
- Null REMOVE_DT indicates stock still in corresponding industry
- Industry classification standards may be adjusted over time; please note historical comparability
