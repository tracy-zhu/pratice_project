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
