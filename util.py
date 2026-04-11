import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_and_preprocess_price(file_path):
    """
    Load price data from Parquet, parse dates, and return a DataFrame.
    Expected columns: stock_code, trade_date, adjusted_close
    """
    df = pd.read_parquet(file_path)
    df = df[['stock_code', 'trade_date', 'adjusted_close']].copy()
    df.sort_values(['stock_code', 'trade_date'], inplace=True)
    return df

def load_selection(file_path):
    """
    Load selection data from Excel, parse dates, and return a DataFrame.
    Expected columns: trade_date, stock_code, selection_rank
    """
    df = pd.read_parquet(file_path)
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

def plot_results(portfolio_values, benchmark_values, dates=None, title='Backtest Results', plot_excess=False):
    """
    Plot portfolio equity curve vs benchmark, drawdown, and optionally cumulative excess returns.
    
    Parameters:
    portfolio_values: Series with datetime index (portfolio equity)
    benchmark_values: Series with datetime index (benchmark equity)
    dates: list or index of dates (optional, uses index from portfolio_values if None)
    title: str, plot title
    plot_excess: bool, if True adds a subplot for cumulative excess returns
    """
    # Use index if dates not provided
    if dates is None:
        dates = portfolio_values.index

    # Determine number of rows and heights
    if plot_excess:
        rows = 3
        row_heights = [0.5, 0.25, 0.25]  # equity, excess, drawdown
        subplot_titles = ('Equity Curve', 'Cumulative Excess Return', 'Drawdown')
    else:
        rows = 2
        row_heights = [0.7, 0.3]
        subplot_titles = ('Equity Curve', 'Drawdown')

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=row_heights,
                        subplot_titles=subplot_titles)

    # Equity curve (row 1)
    fig.add_trace(go.Scatter(x=dates, y=portfolio_values,
                             mode='lines', name='Portfolio'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=benchmark_values,
                             mode='lines', name='Benchmark (Avg Stock)'),
                  row=1, col=1)

    # Drawdown (last row)
    portfolio_returns = portfolio_values.pct_change().dropna()
    cumulative = (1 + portfolio_returns).cumprod()
    peak = cumulative.expanding().max()
    drawdown = (cumulative - peak) / peak
    drawdown_dates = portfolio_returns.index  # same as dates[1:]
    fig.add_trace(go.Scatter(x=drawdown_dates, y=drawdown,
                             mode='lines', name='Drawdown', fill='tozeroy'),
                  row=rows, col=1)

    # Excess returns (if requested)
    if plot_excess:
        # Compute daily returns for both series
        port_ret = portfolio_values.pct_change().dropna()
        bench_ret = benchmark_values.pct_change().dropna()
        # Align indices (they should be the same, but just in case)
        common_idx = port_ret.index.intersection(bench_ret.index)
        if len(common_idx) == 0:
            raise ValueError("No overlapping dates for excess returns calculation.")
        port_ret = port_ret.loc[common_idx]
        bench_ret = bench_ret.loc[common_idx]
        # Cumulative excess returns (geometric)
        excess_ret = (1 + port_ret) / (1 + bench_ret) - 1
        cumulative_excess = (1 + excess_ret).cumprod() - 1
        fig.add_trace(go.Scatter(x=common_idx, y=cumulative_excess,
                                 mode='lines', name='Cumulative Excess Return',
                                 fill='tozeroy'),
                      row=2, col=1)
        # Set y-axis format as percentage
        fig.update_yaxes(title_text='Cumulative Excess', row=2, col=1, tickformat='.1%')

    # Format axes
    fig.update_layout(title=title, height=800 if rows==3 else 700,
                      hovermode='x unified', showlegend=True)
    fig.update_yaxes(title_text='Cumulative Return', row=1, col=1, tickformat='.0f')
    fig.update_yaxes(title_text='Drawdown', row=rows, col=1, tickformat='.0%')
    fig.update_xaxes(title_text='Date', row=rows, col=1)

    fig.show()

def calc_factors(price_group, div_group):
    """
    为单个股票计算每个交易日的三个股息因子
    :param price_group: 该股票的价格数据，已按 trade_date 排序
    :param div_group: 该股票的分红数据
    :return: 包含因子结果的 DataFrame
    """
    results = []
    for _, row in price_group.iterrows():
        trade_date = row['trade_date']
        close_price = row['close_price']
        if close_price == 0:
            expected = static = dynamic = 0.0
        else:
            # 预期股息率：announce_date 在 (trade_date-365, trade_date] 内
            mask_exp = (div_group['announce_date'] > trade_date - pd.Timedelta(days=365)) & \
                       (div_group['announce_date'] <= trade_date)
            sum_exp = div_group.loc[mask_exp, 'div_pre_tax'].sum()
            expected = sum_exp / close_price

            # 静态股息率：ex_date < trade_date 且 div_year = 当前年份-1
            prev_year = trade_date.year - 1
            mask_static = (div_group['ex_date'] < trade_date) & (div_group['div_year'] == prev_year)
            sum_static = div_group.loc[mask_static, 'div_pre_tax'].sum()
            static = sum_static / close_price

            # 动态股息率：ex_date 在 (trade_date-365, trade_date] 内
            mask_dyn = (div_group['ex_date'] > trade_date - pd.Timedelta(days=365)) & \
                       (div_group['ex_date'] <= trade_date)
            sum_dyn = div_group.loc[mask_dyn, 'div_pre_tax'].sum()
            dynamic = sum_dyn / close_price

        results.append({
            'stock_code': row['stock_code'],
            'trade_date': trade_date,
            'expected_div_yield': expected,
            'static_div_yield': static,
            'dynamic_div_yield': dynamic
        })
    return pd.DataFrame(results)

# ===================== 新增：封装完整回测函数（含持仓检查+手续费）=====================
def backtest_top_stocks(
    initial_cash: float,
    start_date: str,
    end_date: str,
    rebalance_freq: int,
    top_n: int,
    price_file: str,
    selection_file: str,
    transaction_fee_rate: float = 0.001  # 默认0.1%手续费
):
    """
    顶层回测函数：选股策略回测 + 持仓差异检查 + 调仓手续费
    手续费规则：调仓总交易金额(卖出+买入) × 手续费率
    返回：组合价值序列、基准价值序列、绩效指标
    """
    # 1. 加载数据
    print("Loading data...")
    price_df = load_and_preprocess_price(price_file)
    selection_df = load_selection(selection_file)

    # 2. 数据预处理
    price_pivot = price_df.pivot(index='trade_date', columns='stock_code', values='adjusted_close')
    price_pivot = price_pivot.sort_index()
    price_pivot.index = pd.to_datetime(price_pivot.index)
    price_pivot = price_pivot.loc[start_date:end_date]
    selection_df = selection_df[(selection_df['trade_date'] >= start_date) &
                                (selection_df['trade_date'] <= end_date)]

    # 3. 生成调仓日期
    selection_dates = sorted(selection_df['trade_date'].unique())
    if not selection_dates:
        raise ValueError("No selection data available in the given date range.")
    rebalance_dates = selection_dates[::rebalance_freq]
    print(f"Number of rebalance dates: {len(rebalance_dates)}")

    # 4. 生成回测时间线
    all_dates = price_pivot.index.tolist()
    first_rebalance = rebalance_dates[0]
    timeline = [d for d in all_dates if d >= first_rebalance]

    # 5. 初始化账户
    cash = initial_cash
    holdings = {}  # 持仓：股票代码->股数
    portfolio_values = []

    # 6. 预计算基准
    benchmark_daily, benchmark_cum = compute_benchmark_returns(price_pivot, start_date, end_date)

    # 7. 回测主循环
    for date in timeline:
        today_prices = price_pivot.loc[date]

        # ---------------- 核心：调仓逻辑 + 持仓差异检查 + 手续费 ----------------
        if date in rebalance_dates:
            old_holdings = holdings.copy()  # 保存调仓前持仓
            sell_total = 0.0  # 卖出总金额

            #  step1：卖出所有旧持仓
            for stock, shares in old_holdings.items():
                price = today_prices.get(stock, np.nan)
                if pd.notna(price):
                    sell_amount = shares * price
                    sell_total += sell_amount
                    cash += sell_amount
            holdings = {}

            # step2：筛选目标股票
            selected = get_top_n_selection(selection_df, date, top_n)
            valid_stocks = [s for s in selected if pd.notna(today_prices.get(s, np.nan))]
            buy_total = 0.0  # 买入总金额

            # step3：计算买入金额 & 扣除手续费
            if valid_stocks:
                amount_per_stock = cash / len(valid_stocks)
                # 计算总买入金额
                buy_total = amount_per_stock * len(valid_stocks)
                # 总交易金额 = 卖出总额 + 买入总额 | 计算手续费
                total_trade_amount = sell_total + buy_total
                transaction_fee = total_trade_amount * transaction_fee_rate
                cash -= transaction_fee  # 扣除手续费

                # 打印持仓差异 & 手续费（可直观看到调仓记录）
                sold_stocks = list(old_holdings.keys())
                bought_stocks = valid_stocks
                print(f"\n=== 调仓日期：{date.date()} ===")
                print(f"卖出股票：{sold_stocks if sold_stocks else '无'} | 卖出总额：{sell_total:.2f}")
                print(f"买入股票：{bought_stocks} | 买入总额：{buy_total:.2f}")
                print(f"总交易金额：{total_trade_amount:.2f} | 手续费：{transaction_fee:.2f}")

                # 执行买入
                new_amount_per = cash / len(valid_stocks)
                for stock in valid_stocks:
                    price = today_prices[stock]
                    holdings[stock] = new_amount_per / price
                cash = 0.0

        # ---------------- 计算当日组合价值 ----------------
        portfolio_value = cash
        for stock, shares in holdings.items():
            price = today_prices.get(stock, np.nan)
            if pd.notna(price):
                portfolio_value += shares * price
        portfolio_values.append(portfolio_value)

    # 8. 整理结果
    portfolio_series = pd.Series(portfolio_values, index=timeline, name='Portfolio')
    benchmark_series = benchmark_cum.reindex(timeline, method='ffill').fillna(1.0)
    benchmark_funds = initial_cash * benchmark_series
    metrics = compute_metrics(portfolio_series.pct_change().dropna())

    return portfolio_series, benchmark_funds, metrics

# ===================== 新增：加载【多空选股】数据 =====================
def load_long_short_selection(file_path):
    """
    加载新版多空选股数据（适配你的mv_selection_v3.parquet）
    列：trade_date, stock_code, mv_comp, signal
    """
    df = pd.read_parquet(file_path)
    df = df[['trade_date', 'stock_code', 'signal']].copy()
    df.sort_values(['trade_date', 'stock_code'], inplace=True)
    return df

def backtest_long_only(
    initial_cash: float,
    start_date: str,
    end_date: str,
    rebalance_freq: int,
    price_file: str,
    selection_file: str,
    transaction_fee_rate: float = 0.001
):
    """
    全多头策略回测（修正版）：
    - 每个调仓日等权重买入所有 long 股票
    - 对已持仓股票进行再平衡（差额调整）
    - 仅对实际发生的交易收取手续费
    返回：组合价值序列、基准价值序列、绩效指标
    """
    # 1. 加载数据
    print("Loading data...")
    price_df = load_and_preprocess_price(price_file)
    selection_df = load_long_short_selection(selection_file)

    # 2. 数据预处理
    price_pivot = price_df.pivot(index='trade_date', columns='stock_code', values='adjusted_close')
    price_pivot = price_pivot.sort_index()
    price_pivot.index = pd.to_datetime(price_pivot.index)
    price_pivot = price_pivot.loc[start_date:end_date]
    selection_df = selection_df[(selection_df['trade_date'] >= start_date) &
                                (selection_df['trade_date'] <= end_date)]

    # 3. 生成调仓日期
    selection_dates = sorted(selection_df['trade_date'].unique())
    if not selection_dates:
        raise ValueError("No selection data available in the given date range.")
    rebalance_dates = selection_dates[::rebalance_freq]
    print(f"Number of rebalance dates: {len(rebalance_dates)}")

    # 4. 回测时间线（从第一个调仓日到结束）
    all_dates = price_pivot.index.tolist()
    first_rebalance = rebalance_dates[0]
    timeline = [d for d in all_dates if d >= first_rebalance]

    # 5. 初始化账户
    cash = initial_cash
    holdings = {}          # stock_code: shares
    portfolio_values = []

    # 6. 预计算基准
    benchmark_daily, benchmark_cum = compute_benchmark_returns(price_pivot, start_date, end_date)

    # 7. 回测主循环
    for date in timeline:
        today_prices = price_pivot.loc[date]

        # --- 调仓日：再平衡至等权重 ---
        if date in rebalance_dates:
            # 获取当日目标股票池（signal == 'long'）
            day_selection = selection_df[selection_df['trade_date'] == date]
            target_stocks = day_selection[day_selection['signal'] == 'long']['stock_code'].tolist()
            # 过滤掉当日价格缺失的股票
            valid_targets = [s for s in target_stocks if pd.notna(today_prices.get(s))]

            # 计算当前总资产（现金 + 持仓市值）
            current_holdings_val = sum(holdings.get(s, 0) * today_prices[s] for s in holdings if s in today_prices and pd.notna(today_prices[s]))
            total_asset = cash + current_holdings_val

            if len(valid_targets) == 0:
                # 无目标股票：清空所有持仓
                for stock in list(holdings.keys()):
                    if stock in today_prices and pd.notna(today_prices[stock]):
                        cash += holdings[stock] * today_prices[stock]
                    del holdings[stock]
                # 记录资产
                port_val = total_asset  # 此时已全部变现
                portfolio_values.append(port_val)
                continue

            # 等权重目标：每只股票的目标市值
            target_value_per_stock = total_asset / len(valid_targets)

            # 记录实际交易总额（用于计算手续费）
            total_trade_amount = 0.0

            # --- 处理卖出：不在目标池中的持仓全部卖出 ---
            for stock in list(holdings.keys()):
                if stock not in valid_targets:
                    if stock in today_prices and pd.notna(today_prices[stock]):
                        price = today_prices[stock]
                        shares = holdings[stock]
                        sell_amt = shares * price
                        cash += sell_amt
                        total_trade_amount += sell_amt
                        del holdings[stock]

            # --- 处理买入/卖出调整：对所有目标股票进行再平衡 ---
            for stock in valid_targets:
                price = today_prices[stock]
                if pd.isna(price):
                    continue

                current_shares = holdings.get(stock, 0)
                current_mv = current_shares * price
                target_shares = target_value_per_stock / price
                delta_shares = target_shares - current_shares

                if delta_shares > 1e-6:   # 需要买入
                    buy_amt = delta_shares * price
                    cash -= buy_amt
                    total_trade_amount += buy_amt
                    holdings[stock] = current_shares + delta_shares
                elif delta_shares < -1e-6:  # 需要卖出
                    sell_amt = -delta_shares * price
                    cash += sell_amt
                    total_trade_amount += sell_amt
                    holdings[stock] = current_shares + delta_shares
                    # 如果减仓后份额为零，删除该键
                    if abs(holdings[stock]) < 1e-6:
                        del holdings[stock]

            # 扣除手续费（基于实际总交易额）
            fee = total_trade_amount * transaction_fee_rate
            cash -= fee

            # 打印调仓明细（可选）
            print(f"\n=== 调仓日期：{date.date()} ===")
            print(f"目标股票数：{len(valid_targets)} | 总资产：{total_asset:.2f} | 每只目标市值：{target_value_per_stock:.2f}")
            print(f"实际交易总额：{total_trade_amount:.2f} | 手续费：{fee:.2f} | 剩余现金：{cash:.2f}")

        # --- 每日估值（非调仓日及调仓日估值）---
        port_val = cash
        for stock, shares in holdings.items():
            price = today_prices.get(stock, np.nan)
            if pd.notna(price):
                port_val += shares * price
        portfolio_values.append(port_val)

    # 8. 整理结果
    portfolio_ser = pd.Series(portfolio_values, index=timeline, name='LongOnlyPortfolio')
    benchmark_ser = benchmark_cum.reindex(timeline, method='ffill').fillna(1.0)
    benchmark_funds = initial_cash * benchmark_ser

    # 9. 计算绩效指标（年化收益率、最大回撤、夏普比率等）
    metrics = compute_metrics(portfolio_ser.pct_change().dropna())

    return portfolio_ser, benchmark_funds, metrics

def backtest_long_short(
    initial_cash: float,
    start_date: str,
    end_date: str,
    rebalance_freq: int,
    price_file: str,
    selection_file: str,
    long_fee_rate: float = 0.001,
    short_trade_fee_rate: float = 0.002,
    short_financing_rate: float = 0.08
):
    """
    多空对冲策略回测（收益率平均法）
    - 一半资金做多，一半资金做空
    - 多头：等权重买入，调仓日再平衡，支付交易手续费
    - 空头：等权重融券卖出，调仓日平仓并重新建仓，支付交易手续费 + 每日融券利息
    - 组合日收益率 = 0.5 * 多头日收益率 + 0.5 * 空头日收益率
    返回：组合净值序列、基准净值序列、绩效指标
    """
    import pandas as pd
    import numpy as np
    from util import load_and_preprocess_price, load_long_short_selection, compute_benchmark_returns, compute_metrics

    # 1. 加载数据
    print("Loading data...")
    price_df = load_and_preprocess_price(price_file)
    selection_df = load_long_short_selection(selection_file)

    # 2. 数据预处理
    price_pivot = price_df.pivot(index='trade_date', columns='stock_code', values='adjusted_close')
    price_pivot = price_pivot.sort_index()
    price_pivot.index = pd.to_datetime(price_pivot.index)
    price_pivot = price_pivot.loc[start_date:end_date]
    selection_df = selection_df[(selection_df['trade_date'] >= start_date) &
                                (selection_df['trade_date'] <= end_date)]

    # 3. 生成调仓日期
    selection_dates = sorted(selection_df['trade_date'].unique())
    if not selection_dates:
        raise ValueError("No selection data available.")
    rebalance_dates = selection_dates[::rebalance_freq]
    print(f"Number of rebalance dates: {len(rebalance_dates)}")

    # 4. 时间轴（从第一个调仓日开始）
    all_dates = price_pivot.index.tolist()
    first_rebalance = rebalance_dates[0]
    timeline = [d for d in all_dates if d >= first_rebalance]

    # 5. 预计算基准
    _, benchmark_cum = compute_benchmark_returns(price_pivot, start_date, end_date)
    benchmark_ser = benchmark_cum.reindex(timeline, method='ffill').fillna(1.0)

    # ---------- 辅助函数：计算多头每日收益率（考虑再平衡手续费）----------
    def get_long_daily_returns():
        """返回多头部分的每日收益率序列（已扣除交易手续费）"""
        # 持仓权重：调仓日等权重，非调仓日随价格波动
        weights = {}  # date -> {stock: weight}
        for date in timeline:
            if date in rebalance_dates:
                day_sel = selection_df[selection_df['trade_date'] == date]
                long_stocks = day_sel[day_sel['signal'] == 'long']['stock_code'].tolist()
                # 过滤价格有效股票
                valid = [s for s in long_stocks if s in price_pivot.loc[date] and pd.notna(price_pivot.loc[date, s])]
                if len(valid) == 0:
                    w = {}
                else:
                    w = {s: 1.0/len(valid) for s in valid}
                weights[date] = w
            else:
                # 非调仓日沿用前一日权重（但需前向填充）
                prev_date = timeline[timeline.index(date)-1] if timeline.index(date) > 0 else date
                weights[date] = weights.get(prev_date, {}).copy()
        
        # 计算每日组合收益率（扣除调仓日的手续费）
        daily_ret = []
        prev_port_val = 1.0  # 初始净值1（代表50万资金）
        for i, date in enumerate(timeline):
            prices = price_pivot.loc[date]
            w = weights[date]
            if not w:
                daily_ret.append(0.0)
                continue
            
            # 当日组合收益率（未扣除手续费）
            if i == 0:
                port_ret = 0.0
            else:
                prev_date = timeline[i-1]
                prev_prices = price_pivot.loc[prev_date]
                prev_w = weights[prev_date]
                # 计算从prev_date到date的持有期收益率
                ret_contrib = 0.0
                for stock, weight in prev_w.items():
                    if stock in prices and stock in prev_prices and pd.notna(prices[stock]) and pd.notna(prev_prices[stock]):
                        stock_ret = prices[stock] / prev_prices[stock] - 1
                        ret_contrib += weight * stock_ret
                port_ret = ret_contrib
            
            # 扣除调仓日手续费（如果当天是调仓日）
            if date in rebalance_dates and w:
                # 调仓日：卖出原组合，买入新组合，产生双边交易额
                # 简化：交易额为组合总市值（因为全部换仓），手续费 = 2 * 总市值 * long_fee_rate? 但实际只有变动部分。
                # 更精确：假设调仓日先按旧权重卖出全部（交易额=前一日市值），再按新权重买入（交易额=当日市值）
                # 但为简化且与通常做法一致：手续费 = 当日市值 * long_fee_rate (仅买入)
                # 也可以双边收：2 * 市值 * long_fee_rate。这里采用单边买入收（常见于券商单向收费）
                fee = 1.0 * long_fee_rate  # 按当日净值1计算手续费率，实际需乘净值
                # 扣除手续费相当于净值乘以 (1 - fee)
                port_ret -= fee   # 近似，更精确应为净值乘法，但每日收益率小，加法可接受
            
            daily_ret.append(port_ret)
        
        # 将日收益率序列转换为净值序列（起始1）
        ret_series = pd.Series(daily_ret, index=timeline)
        nav_series = (1 + ret_series).cumprod()
        return ret_series, nav_series

    # ---------- 辅助函数：计算空头每日收益率（考虑交易手续费 + 每日融券利息）----------
    def get_short_daily_returns():
        """返回空头部分的每日收益率序列（已扣除交易手续费和融券利息）"""
        # 空头收益率 = - (股票组合收益率) - 每日利息率 - 调仓日额外手续费率
        weights = {}
        for date in timeline:
            if date in rebalance_dates:
                day_sel = selection_df[selection_df['trade_date'] == date]
                short_stocks = day_sel[day_sel['signal'] == 'short']['stock_code'].tolist()
                valid = [s for s in short_stocks if s in price_pivot.loc[date] and pd.notna(price_pivot.loc[date, s])]
                if len(valid) == 0:
                    w = {}
                else:
                    w = {s: 1.0/len(valid) for s in valid}
                weights[date] = w
            else:
                prev_date = timeline[timeline.index(date)-1] if timeline.index(date) > 0 else date
                weights[date] = weights.get(prev_date, {}).copy()
        
        daily_ret = []
        for i, date in enumerate(timeline):
            prices = price_pivot.loc[date]
            w = weights[date]
            if not w:
                daily_ret.append(0.0)
                continue
            
            # 股票组合的收益率（多头视角）
            if i == 0:
                stock_port_ret = 0.0
            else:
                prev_date = timeline[i-1]
                prev_prices = price_pivot.loc[prev_date]
                prev_w = weights[prev_date]
                ret_contrib = 0.0
                for stock, weight in prev_w.items():
                    if stock in prices and stock in prev_prices and pd.notna(prices[stock]) and pd.notna(prev_prices[stock]):
                        stock_ret = prices[stock] / prev_prices[stock] - 1
                        ret_contrib += weight * stock_ret
                stock_port_ret = ret_contrib
            
            # 空头收益率 = - 股票收益率
            short_ret = -stock_port_ret
            
            # 扣除调仓日手续费（空头交易：融券卖出和买回各收一次，简化按双边收）
            if date in rebalance_dates and w:
                # 假设调仓日全部平仓并重新开仓，交易额为当前空头市值的2倍（卖出+买回）
                # 手续费率 = short_trade_fee_rate，因此手续费占比 = 2 * short_trade_fee_rate
                fee = 2 * short_trade_fee_rate
                short_ret -= fee
            
            # 扣除当日融券利息（年化利率转为日利率）
            daily_interest_rate = short_financing_rate / 252.0
            short_ret -= daily_interest_rate
            
            daily_ret.append(short_ret)
        
        ret_series = pd.Series(daily_ret, index=timeline)
        nav_series = (1 + ret_series).cumprod()
        return ret_series, nav_series

    # 6. 计算多空各自的日收益率和净值
    long_ret, long_nav = get_long_daily_returns()
    short_ret, short_nav = get_short_daily_returns()

    # 7. 组合日收益率 = 0.5 * long_ret + 0.5 * short_ret
    combined_ret = 0.5 * long_ret + 0.5 * short_ret
    combined_nav = (1 + combined_ret).cumprod()
    combined_nav = combined_nav * (initial_cash / 1.0)  # 初始资金映射

    # 基准也按初始资金缩放
    benchmark_funds = initial_cash * benchmark_ser

    # 8. 绩效指标
    metrics = compute_metrics(combined_ret.dropna())

    return combined_nav, benchmark_funds, metrics