# Data Description

## File Structure

### EOD_PRICES.parquet
| Column | Type | Description |
|--------|------|-------------|
| stock_code | object | Ticker code |
| trade_date | object | Trading date |
| close_price | float64 | Close price (CNY) |
| adjusted_close | float64 | Adjusted close price (CNY) |
| adj_factor | float64 | Adjustment factor |
| volume | float64 | Volume (lots, 1 lot = 100 shares) |
| turnover | float64 | Turnover (CNY) |

### INCOME.parquet
| Column | Type | Description |
|--------|------|-------------|
| stock_code | category | Ticker code |
| report_period | category | Reporting period |
| announce_date | category | Announcement date |
| statement_type | category | Statement type, see details below |
| revenue | float64 | Operating revenue (CNY) |
| operating_profit | float64 | Operating profit (CNY) |
| net_profit_all | float64 | Net profit (incl. minority interest) (CNY) |
| net_profit_parent | float64 | Net profit (attributable to parent) (CNY) |
| total_operating_cost | float64 | Total operating cost (CNY) |
| operating_cost | float64 | Operating cost (CNY) |
| selling_expenses | float64 | Selling expenses (CNY) |
| admin_expenses | float64 | Administrative expenses (CNY) |
| financial_expenses | float64 | Financial expenses (CNY) |
| ebit | float64 | EBIT (CNY) |
| ebitda | float64 | EBITDA (CNY) |
| eps_basic | float64 | Basic EPS (CNY) |
| rd_expense | float64 | R&D expense (CNY) |

### BALANCE.parquet
| Column | Type | Description |
|--------|------|-------------|
| stock_code | category | Ticker code |
| report_period | category | Reporting period |
| announce_date | category | Announcement date |
| statement_type | category | Statement type, see details below |
| equity_all | float64 | Total equity incl. minority interest (CNY) |
| equity_parent | float64 | Equity attributable to parent (CNY) |
| total_shares | float64 | Total shares |
| treasury_stock | float64 | Treasury stock |
| short_term_debt | float64 | Short-term debt (CNY) |
| long_term_debt | float64 | Long-term debt (CNY) |
| bonds_payable | float64 | Bonds payable (CNY) |
| cash | float64 | Cash (CNY) |
| settlement_reserve | float64 | Settlement reserve (CNY) |
| total_liabilities | float64 | Total liabilities (CNY) |
| total_assets | float64 | Total assets (CNY) |

### CASHFLOW.parquet
| Column | Type | Description |
|--------|------|-------------|
| stock_code | category | Ticker code |
| report_period | category | Reporting period |
| announce_date | category | Announcement date |
| statement_type | category | Statement type, see details below |
| operating_cf | float64 | Net cash flow from operating activities (CNY) |
| capex | float64 | Cash paid for fixed/intangible/other long-term assets (CNY) |
| depreciation | float64 | Depreciation of fixed assets (CNY) |
| amortization | float64 | Amortization of intangible assets (CNY) |
| operating_cf_indirect | float64 | Net cash flow from operating activities (indirect) (CNY) |
| fcff | float64 | Free cash flow to firm (CNY) |

### CAPITAL.parquet
| Column | Type | Description |
|--------|------|-------------|
| stock_code | category | Ticker code |
| change_date | category | Change date |
| total_shares | float64 | Total shares |
| float_shares | float64 | Free-float shares (10k shares) |
| total_a_shares | float64 | Total A-shares (10k shares) |
| float_a_shares | float64 | Free-float A-shares (10k shares) |

### DIVIDEND.parquet
| Column | Type | Description |
|--------|------|-------------|
| stock_code | category | Ticker code |
| announce_date | category | Announcement date |
| ex_date | category | Ex-dividend date |
| div_pre_tax | float64 | Cash dividend per share (pre-tax) (CNY) |
| div_after_tax | float64 | Cash dividend per share (after tax) (CNY) |
| progress | category | Plan status |
| base_shares | float64 | Base shares for dividend (10k shares) |
| div_year | category | Dividend year |
| currency | category | Currency |
| is_no_div | int64 | No-dividend flag (0 = dividend, 1 = no dividend) |
| total_cash_div | float64 | Total cash dividend (CNY) |

## Statement Type Field Description

The `statement_type` field in financial statements (Income, Balance, Cashflow) distinguishes different versions of reported data. There are 4 types:

| statement_type | Data Share | Usage Notes |
|--------------|-----------|-------------|
| ORIGINAL | ~53% | Initial consolidated statements published by companies |
| ORIGINAL_VOID | ~2% | Original versions marked as "pre-correction"  |
| RESTATED | ~43% | Historical data restated due to accounting standard changes, business combinations, etc. |
| RESTATED_VOID | ~0.75% | Restated versions marked as "pre-correction" |

### Data Extraction Notes

This dataset only extracts the above 4 statement types (covering 99% of historical data). Other types (such as error corrections CORRECTION, restated corrections RESTATED_COR, etc.) are excluded due to minimal volume (<1%) and being mostly voided versions.

### Understanding _VOID Data

- **ORIGINAL_VOID** : These are original statements that were later corrected. When companies discover errors and publish corrections, the original versions are marked as "pre-correction"
- **RESTATED_VOID** : These are restated statements that were further adjusted

These _VOID data are primarily useful for point-in-time purpose. For the same `(stock_code, report_period)` combination, prioritize latest announced data(data corrected / adjusted for accounting standards is more accurate).

## Notes

- **Time Range**: 20130101 to 20251130
- **Data Types**: Data types shown reflect actual stored types
- **Point-in-Time Basis**: Based on `announce_date` (announcement date) field
- **Date Format**: All date fields are in original format (YYYYMMDD string, not converted to datetime64)
- **Dividend Data**: Only includes completed (progress=3) RMB cash dividends
