# -*- coding: utf-8 -*-
"""

# 测试个股领先性对大盘指数择时的影响；

# 参考的是银河证券：个股特征研究策略之一基于个股领先方向性的大盘择时策略；

Thu 2018/11/22

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_backtest_function import *
from python_base.plot_method import *


def absolute_direction_judge(index_stock, index_df):
    """
    接受某个指数所有成分股的日线数据，计算每只股票的相对方向预测；
    还有绝对方向预测持续天数；
    :param index_stock: 指数成分股日线表
    :param index_df: 指数日线表
    :return:
    """
    absolute_judge_dict = defaultdict()
    stock_pct_dict = defaultdict()
    index_df = index_df.set_index('time')
    index_stock = index_stock.set_index('time')
    for stock_code, group in index_stock.groupby('code'):
        absolute_judge_dict[stock_code] = index_df['pct_chg'] * group["PCT_CHG"].shift(1)
        stock_pct_dict[stock_code] = group["PCT_CHG"]
    absolute_judge_df = DataFrame(absolute_judge_dict)
    stock_pct_df = DataFrame(stock_pct_dict)
    absolute_judge_df[absolute_judge_df > 0] = 1
    absolute_judge_df[absolute_judge_df < 0] = -1
    judge_df = stock_pct_df * absolute_judge_df
    indicator_series = (judge_df < 0).sum(axis=1)
    indicator_series[indicator_series < 100] = 0
    indicator_series[indicator_series >= 100] = 1
    # stock_pct_df[judge_df > 0]  = 0
    # indicator_series = stock_pct_df.mean(axis=1)
    # indicator_series[indicator_series > 0] = 1
    # indicator_series[indicator_series < 0] = 0
    return indicator_series


def relative_direction_judge(index_stock, index_df):
    """
    接受某个指数所有成分股的日线数据，计算每只股票的相对方向预测；
    还有相对方向预测持续天数；
    :param index_stock: 指数成分股日线表
    :param index_df: 指数日线表
    :return:
    """
    absolute_judge_dict = defaultdict()
    stock_pct_dict = defaultdict()
    index_df = index_df.set_index('time')
    index_stock = index_stock.set_index('time')
    for stock_code, group in index_stock.groupby('code'):
        stock_pct_chg_chg = group["PCT_CHG"].shift(1) - group['PCT_CHG'].shift(2)
        absolute_judge_dict[stock_code] = index_df['pct_chg'] * stock_pct_chg_chg
        stock_pct_dict[stock_code] = group["PCT_CHG"]
    absolute_judge_df = DataFrame(absolute_judge_dict)
    stock_pct_df = DataFrame(stock_pct_dict)
    absolute_judge_df[absolute_judge_df > 0] = 1
    absolute_judge_df[absolute_judge_df < 0] = -1
    judge_df = stock_pct_df * absolute_judge_df
    stock_pct_df[judge_df > 0]  = 0
    indicator_series = stock_pct_df.mean(axis=1)
    indicator_series[indicator_series > 0] = 1
    indicator_series[indicator_series < 0] = 0
    return indicator_series


def back_test_by_indicator(indicator_series):
    """
    根据indicator_series生成的信号进行回测；
    :param indicator_series:
    :return:
    """
    # constituent_vd = index_df['vd_ma']
    holding_cumprod_pct = 0
    index_cumprod_pct = 0
    start_date = chang_time_to_str(indicator_series.index[0])
    end_date = chang_time_to_str(indicator_series.index[-1])
    df_300 = get_index_data("000300.SH", start_date, end_date)
    index_series = pd.to_datetime(df_300['time'], format='%Y/%m/%d %H:%M:%S')
    pct_chg_series = Series(df_300.pct_chg.values, index=index_series)

    holding_pct_series = pct_chg_series.shift(-1) * indicator_series
    holding_pct_series.dropna(inplace=True)
    if len(holding_pct_series) > 0:
        pct_chg_series = pct_chg_series[pct_chg_series.index >= holding_pct_series.index[0]]
        holding_cumprod_pct = trans_cumprod_pct(holding_pct_series)
        index_cumprod_pct = trans_cumprod_pct(pct_chg_series)
    strategy_index_ratio = holding_cumprod_pct / index_cumprod_pct
    holding_cumprod_pct.plot()
    index_cumprod_pct.plot()
    strategy_index_ratio.plot()
    return holding_cumprod_pct, index_cumprod_pct


if __name__ == '__main__':
    start_date = '2010-01-01'
    end_date = '2018-11-21'
    index_name = '000300.SH'
    index_stock = get_index_stock_df(start_date, end_date, index_name)
    index_df = get_index_data(index_name, start_date, end_date)
    indicator_series = absolute_direction_judge(index_stock, index_df)
    holding_cumprod_pct, index_cumprod_pct = back_test_by_indicator(indicator_series)
    annulized_return, sharpe_ratio, max_drawback = calc_evaluation_index(holding_cumprod_pct)
    index_annulized_return, index_sharpe_ratio, index_drawback = calc_evaluation_index(index_cumprod_pct)

