# 行业分类数据说明

## 文件列表

- `AShareSWNIndustriesClass.parquet` - 申万行业分类历史记录（完整版）
- `Stock_Industry_Year.parquet` - 股票年度行业映射表（简化版）

## 数据结构

### AShareSWNIndustriesClass.parquet

| 字段名 | 类型 | 描述 |
|--------|------|------|
| S_INFO_WINDCODE | object | 股票代码 |
| SW_IND_CODE | object | 申万行业代码 |
| ENTRY_DT | datetime64 | 纳入日期 |
| REMOVE_DT | datetime64 | 移除日期（空值表示仍在该行业） |
| CUR_SIGN | object | 当前标志 |
| INDUSTRIESNAME | object | 一级行业名称 |

### Stock_Industry_Year.parquet

| 字段名 | 类型 | 描述 |
|--------|------|------|
| stock_code | object | 股票代码 |
| year | int64 | 年份 |
| industry_name | object | 一级行业名称 |

## 数据说明

- **行业分类标准**: 申万行业分类（一级行业）
- **时间范围**: 2010年至今
- **更新逻辑**:
  - 完整版保留所有历史变更记录
  - 年度版以每年1月1日时点为准，取最新有效记录

## 使用场景

### 场景1: 获取某年所有股票的行业分类

```python
import pandas as pd

df = pd.read_parquet('Stock_Industry_Year.parquet')
industry_2023 = df[df['year'] == 2023]
print(industry_2023)
```

### 场景2: 追溯某股票的行业变更历史

```python
df = pd.read_parquet('AShareSWNIndustriesClass.parquet')
history = df[df['S_INFO_WINDCODE'] == '000001.SZ']
print(history[['ENTRY_DT', 'REMOVE_DT', 'INDUSTRIESNAME']])
```

## 注意事项

- 部分股票可能在同一时点有多条记录，年度版已自动去重（保留最新）
- REMOVE_DT 为空表示该股票仍在对应行业
- 行业分类标准可能随时间调整，请注意历史可比性
