# -*- coding: utf-8 -*-
"""

# 测试指数的单项波动率差值的择时效应；

# 简单的是单指数的波动率择时，后面有成分股的波动率择时；

# 参考的是国信证券：基于成分股波动率差值指数择时；

Tue 2018/11/20

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_backtest_function import *
from python_base.plot_method import *


def get_index_volatility_difference(start_date, end_date, index_code):
    """
    计算指数的上行波动率和下行波动率之差
    :param start_date:
    :param end_date:
    :index_code : 000300.SH
    :return:
    """
    index_df = get_index_data(index_code, start_date, end_date)
    index_df['volatility_difference'] = (index_df.high + index_df.low - 2 * index_df.open) / index_df.open
    index_df['vd_ma'] = index_df['volatility_difference'].rolling(window=20).mean()
    print(index_df.tail())
    return index_df


def get_df_vd(index_df, rolling_window):
    """
    传入某只股票的日线列表，生成波动率差值；
    :param stock_df:
    :return:
    """
    index_df['volatility_difference'] = (index_df.HIGH + index_df.LOW - 2 * index_df.OPEN) / index_df.OPEN
    index_df['vd_ma'] = index_df['volatility_difference'].rolling(window=rolling_window).mean()
    return index_df


def get_constituent_stock_vd(start_date, end_date, index_name):
    """
    用指数的成分股计算每天波动率差值参数；
    :param start_date:
    :param end_date:
    :param index_name:hs300, sh50, zz500
    :return:
    """
    df_table = get_index_stock_df(start_date, end_date, index_name)
    df_table['code'] = df_table.index
    df_table = df_table.reset_index()
    df_2 = df_table.groupby('code').apply(lambda x : get_df_vd(x, rolling_window=10))
    # df_3 = df_2[df_2.time == change_trading_day_date_stock(end_date)]
    constituent_vd = df_2.groupby('time').apply(lambda x: float(sum(x.vd_ma > 0)) / float(len(x)))
    print(constituent_vd.tail(10))
    return constituent_vd


def back_test_by_indicator(constituent_vd):
    """
    根据constituent_vd生成信号，对股指进行回测
    :param constituent_vd:
    :return:
    """
    # constituent_vd = index_df['vd_ma']
    limit_value = 0
    holding_cumprod_pct = 0
    index_cumprod_pct = 0
    total_fee = 0
    bilateral_fee = 0.004
    trade_times = 0
    position_list = []
    start_date = chang_time_to_str(constituent_vd.index[0])
    end_date = chang_time_to_str(constituent_vd.index[-1])
    df_300 = get_index_data("000300.SH", start_date, end_date)
    index_series = pd.to_datetime(df_300['time'], format='%Y/%m/%d %H:%M:%S')
    pct_chg_series = Series(df_300.pct_chg.values, index=index_series)

    position = 0
    for indicator in constituent_vd:
        if indicator > limit_value:
            position = 1
        if indicator <= limit_value:
            if position != 0:
                trade_times += 1
            position = 0
        position_list.append(position)
    print ("trade times is " + str(trade_times))
    position_series = Series(position_list, index=pct_chg_series.index)
    holding_pct_series = pct_chg_series.shift(-1) * position_series
    holding_pct_series.dropna(inplace=True)
    if len(holding_pct_series) > 0:
        pct_chg_series = pct_chg_series[pct_chg_series.index >= holding_pct_series.index[0]]
        holding_cumprod_pct = trans_cumprod_pct(holding_pct_series)
        index_cumprod_pct = trans_cumprod_pct(pct_chg_series)
        total_fee = trade_times * bilateral_fee
    strategy_index_ratio = holding_cumprod_pct / index_cumprod_pct
    holding_cumprod_pct.plot()
    index_cumprod_pct.plot()
    strategy_index_ratio.plot()
    return holding_cumprod_pct, index_cumprod_pct, total_fee


if __name__ == '__main__':
    start_date = '2017-01-01'
    end_date = '2018-11-22'
    index_name = 'hs300'
    index_code = '000300.SH'
    constituent_vd = get_constituent_stock_vd(start_date, end_date, index_name)
    holding_cumprod_pct, index_cumprod_pct, total_fee = back_test_by_indicator(constituent_vd)
    annulized_return, sharpe_ratio, max_drawback = calc_evaluation_index(holding_cumprod_pct)
    index_annulized_return, index_sharpe_ratio, index_drawback = calc_evaluation_index(index_cumprod_pct)
