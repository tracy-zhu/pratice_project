# -*- coding: utf-8 -*-
"""

# 计算每个指数,股票的波动率，比较使用波动率择时有没有一定的效果；

# 衡量股票的股性程度

Tue 2018/4/11

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math
import itertools
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from stock_base.stock_data_api import *

trading_day_list = get_trading_day_list()


def get_stock_volatility_HL(stock_code, trading_day, period):
    """
    根据最高价和最低价更新过去一段时间的波动率，来衡量这只股票的股性
    :param stock_code:
    :param trading_day: '2018-04-10"
    :return:
    """
    history_volatility = None
    start_date = get_next_trading_day_stock(trading_day, -1 * period)
    stock_df = get_stock_df(stock_code, start_date, trading_day)
    high_low_spread = stock_df.HIGH - stock_df.LOW
    if sum(high_low_spread == 0) <= 0.2 * period:
        high_low_middle = (stock_df.HIGH + stock_df.LOW) / 2
        high_low_yield = high_low_spread / high_low_middle
        history_volatility = calc_history_volatility(high_low_yield)
    return history_volatility


def get_stock_volatility_OC(stock_code, trading_day, period):
    """
    根据开盘价和收盘价计算过去一段时间的波动率，来衡量该股票的另一只股性
    :param stock_code:
    :param trading_day:
    :param period:
    :return:
    """
    history_volatility = None
    start_date = get_next_trading_day_stock(trading_day, -1 * period)
    stock_df = get_stock_df(stock_code, start_date, trading_day)
    high_low_spread = stock_df.CLOSE - stock_df.OPEN
    if sum(high_low_spread == 0) <= 0.2 * period:
        high_low_yield = high_low_spread / stock_df.OPEN
        history_volatility = calc_history_volatility(high_low_yield)
    return history_volatility


def get_stock_volatility_common(stock_code, trading_day, period):
    """
    最普通的用每天的收益率计算波动率
    :param stock_code:
    :param trading_day:
    :param period:
    :return:
    """
    start_date = get_next_trading_day_stock(trading_day, -1 * period)
    stock_df = get_stock_df(stock_code, start_date, trading_day)
    pct_chg_series = stock_df.PCT_CHG
    pct_chg_series = pct_chg_series[pct_chg_series> -20]
    history_volatility = calc_history_volatility(pct_chg_series)
    return history_volatility


def calc_history_volatility(yield_series):
    """
    根据不同生成的yield，计算历史波动率，并标准为年化
    :param yield_series:
    :return:
    """
    history_volatility = yield_series.std() * math.sqrt(252)
    return history_volatility


def volatility_sort(stock_code_list, trading_day, period, flag):
    """
    根据合约按照波动率从小到大排序
    :param stock_code_list:
    :param trading_day:
    :param period:
    :param flag: 0 : HL, 1: OC, 2: common
    :return:
    """
    volatility_stock_dict = defaultdict()
    for stock_code in stock_code_list:
        history_volatility = None
        if flag == 0:
            history_volatility =  get_stock_volatility_HL(stock_code, trading_day, period)
        elif flag == 1:
            history_volatility =  get_stock_volatility_OC(stock_code, trading_day, period)
        elif flag == 2:
            history_volatility = get_stock_volatility_common(stock_code, trading_day, period)
        if history_volatility != None:
            volatility_stock_dict[stock_code] = history_volatility
    sorted_volatility_stock = sorted(volatility_stock_dict.items(), key=lambda d: d[1], reverse=False)
    # for stock_code, volatility_value in sorted_volatility_stock:
    #     print stock_code , volatility_value
    return sorted_volatility_stock


if __name__ == '__main__':
    stock_code_list = ['600901.SH', '000416.SZ', '600830.SH']
    trading_day = '2018-04-11'
    period = 22
    sorted_volatility_stock = volatility_sort(stock_code_list, trading_day, period)
