# -*- coding: utf-8 -*-
"""

# 用于储存计算股票持有收益的部分函数

Fri 2018/09/07

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *


def stock_holding_profit(stock_code, trading_day, holding_period):
    """
    股票从当天选出，以收盘价持有n天的收益；
    :param stock_code:
    :param trading_day:
    :param holding_period:
    :return:
    """
    start_date = get_next_trading_day_stock(trading_day, 1)
    end_date = get_next_trading_day_stock(trading_day, holding_period)
    stock_df = get_stock_df(stock_code, start_date, end_date)
    stock_df = stock_df[stock_df.PCT_CHG > -10]
    cumprod_series = Series((stock_df.PCT_CHG / 100 + 1).cumprod().values, index=stock_df.time)
    return cumprod_series.values[-1]


def trans_cumprod_pct(pct_chg_series):
    """
    将日收益率序列转化成累计收益率序列
    """
    cumprod_pct = (1 + pct_chg_series / 100).cumprod()
    return cumprod_pct


def calc_evaluation_index(holding_cumprod_pct):
    """
    根据策略收益率序列计算出策略的参数：夏普比，最大回撤，年化收益率
    年化收益率, 夏普比仅适用于日线数据，最大回撤可以应用到其他数据；
    :param holding_cumprod_pct:
    :return:
    """
    trading_days = len(holding_cumprod_pct)
    annulized_return = float(holding_cumprod_pct.values[-1] + 1) ** (float(252) / float(trading_days)) - 1
    sharpe_ratio = holding_cumprod_pct.mean() / (holding_cumprod_pct.std() + 1e-8) * float(252) ** 0.5
    res = pd.DataFrame()
    max_value = -999
    for index_name in holding_cumprod_pct.index[1:]:
        if not np.isnan(holding_cumprod_pct.loc[index_name]):
            max_value = max(max_value, holding_cumprod_pct.loc[index_name])
        res.loc[index_name, 'drawback'] = float(holding_cumprod_pct.loc[index_name]) / float(max_value) - 1
    max_drowback = res['drawback'].min()
    print("annulized return is {}%".format(annulized_return * 100))
    print("sharp ratio is {}".format(sharpe_ratio))
    print("max drawback is {}%".format(max_drowback * 100))
    return annulized_return, sharpe_ratio, max_drowback
