import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_and_preprocess_price(file_path):
    """
    Load price data from CSV/Parquet, parse dates, and return a DataFrame.
    Expected columns: stock_code, trade_date, adjusted_close
    """
    df = pd.read_parquet(file_path) if file_path.endswith('.parquet') else pd.read_csv(file_path, parse_dates=['trade_date'])
    df = df[['stock_code', 'trade_date', 'adjusted_close']].copy()
    df.sort_values(['stock_code', 'trade_date'], inplace=True)
    return df

def load_selection(file_path):
    """
    Load selection data from Excel, parse dates, and return a DataFrame.
    Expected columns: trade_date, stock_code, selection_rank
    """
    df = pd.read_excel(file_path, parse_dates=['trade_date'])
    df = df[['trade_date', 'stock_code', 'selection_rank']].copy()
    df.sort_values(['trade_date', 'selection_rank'], inplace=True)
    return df

def get_top_n_selection(selection_df, date, n):
    """
    Return list of stock codes for the top n ranks on a given date.
    If fewer than n stocks exist, return all available.
    """
    day_data = selection_df[selection_df['trade_date'] == date]
    if day_data.empty:
        return []
    day_data = day_data.sort_values('selection_rank')
    return day_data['stock_code'].head(n).tolist()

def compute_daily_returns(price_pivot):
    """
    Given a pivot table (index=date, columns=stock_code, values=adjusted_close),
    compute daily returns for each stock and return the returns DataFrame.
    """
    return price_pivot.pct_change().dropna(how='all')

def compute_benchmark_returns(price_pivot, start_date, end_date):
    """
    Compute the daily equal-weighted average return of all stocks in the universe.
    Returns a Series of daily benchmark returns and the cumulative benchmark.
    """
    # Filter dates
    price_pivot = price_pivot.loc[start_date:end_date]
    daily_returns = compute_daily_returns(price_pivot)
    # Equal-weighted average across stocks each day
    benchmark_daily = daily_returns.mean(axis=1, skipna=True)
    benchmark_cum = (1 + benchmark_daily).cumprod()
    return benchmark_daily, benchmark_cum

def compute_metrics(returns_series, rf=0, periods_per_year=252):
    """
    Compute annualized return, volatility, Sharpe ratio, and max drawdown.
    Input: returns_series (pandas Series of daily returns)
    Output: dict of metrics
    """
    if returns_series.empty:
        return {'Annualized Return': np.nan, 'Volatility': np.nan,
                'Sharpe Ratio': np.nan, 'Max Drawdown': np.nan}

    # Total return and annualized
    total_return = (1 + returns_series).prod() - 1
    num_days = len(returns_series)
    annualized_return = (1 + total_return) ** (periods_per_year / num_days) - 1

    # Volatility
    daily_std = returns_series.std()
    volatility = daily_std * np.sqrt(periods_per_year)

    # Sharpe ratio
    sharpe = (annualized_return - rf) / volatility if volatility != 0 else np.nan

    # Max drawdown
    cumulative = (1 + returns_series).cumprod()
    peak = cumulative.expanding().max()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()

    return {
        'Annualized Return': annualized_return,
        'Volatility': volatility,
        'Sharpe Ratio': sharpe,
        'Max Drawdown': max_drawdown
    }

def plot_results(portfolio_values, benchmark_values, dates, title='Backtest Results'):
    """
    Plot portfolio equity curve vs benchmark, and drawdown.
    portfolio_values, benchmark_values: Series with datetime index
    dates: list or index of dates (optional, can use index from series)
    """
    # Use index if dates not provided
    if dates is None:
        dates = portfolio_values.index

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3],
                        subplot_titles=('Equity Curve', 'Drawdown'))

    # Equity curve
    fig.add_trace(go.Scatter(x=dates, y=portfolio_values,
                             mode='lines', name='Portfolio'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=benchmark_values,
                             mode='lines', name='Benchmark (Avg Stock)'),
                  row=1, col=1)

    # Drawdown
    portfolio_returns = portfolio_values.pct_change().dropna()
    cumulative = (1 + portfolio_returns).cumprod()
    peak = cumulative.expanding().max()
    drawdown = (cumulative - peak) / peak
    fig.add_trace(go.Scatter(x=dates[1:], y=drawdown,
                             mode='lines', name='Drawdown', fill='tozeroy'),
                  row=2, col=1)

    fig.update_layout(title=title, height=800,
                      hovermode='x unified',
                      showlegend=True)
    fig.update_yaxes(title_text='Cumulative Return', row=1, col=1)
    fig.update_yaxes(title_text='Drawdown', row=2, col=1, tickformat='.0%')
    fig.update_xaxes(title_text='Date', row=2, col=1)

    fig.show()