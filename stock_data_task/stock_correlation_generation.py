# -*- coding: utf-8 -*-
"""

# 计算股票组的相关性；按日收益率计算，过去一个月；或者5分钟收益率计算，过去两周的

# 衡量股票的股性程度

Mon 2018/4/16

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math
import itertools
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from stock_base.stock_file_api import *

trading_day_list = get_trading_day_list()


def get_minute_close_yield_series(stock_code, trading_day, frequency):
    resample_data = resample_minute_data(stock_code, trading_day, frequency)
    close_price_series = resample_data.close
    log_close_series = np.log(close_price_series)
    yield_series = log_close_series.diff()
    return yield_series


def get_total_minute_close_yield(stock_code, end_date, frequency, period):
    """
    函数将end_date前10天的收益率序列结合在一起
    :param stock_code:
    :param end_date: '2018-04-16
    :param frequency:"5min"
    :param period:period代表是过去是多少天，10个交易日
    :return:
    """
    total_close_yield = Series()
    start_date = get_next_trading_day_stock(end_date, -1 * period)
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        trading_day = change_trading_day_format(trading_day)
        if start_date <= trading_day <= end_date:
            close_yield_series = get_minute_close_yield_series(stock_code, trading_day, frequency)
            total_close_yield = pd.concat([total_close_yield, close_yield_series])
    total_close_yield = total_close_yield.dropna()
    return total_close_yield


def get_stock_correlation_matrix_minute(stock_code_list, end_date, frequency, period):
    """
    给定一系列的股票，根据这些股票前段时间的5分钟收益率
    :param stock_code_list:[]
    :param end_date: '2018-04-16'
    :param frequency:'5min'
    :param period: 10
    :return:
    """
    yield_dict = defaultdict()
    for stock_code in stock_code_list:
        print stock_code
        close_yield = get_total_minute_close_yield(stock_code, end_date, frequency, period)
        yield_dict[stock_code] = close_yield

    yield_data_frame = DataFrame(yield_dict)
    yield_data_frame = yield_data_frame.dropna(how="all")
    result = yield_data_frame.corr()
    return result


def get_stock_correlation_matrix_days(stock_code_list, end_date, period):
    """
    给定一系列的股票，这些股票的日收益率计算相关性
    :param stock_code_list:[]
    :param end_date: '2018-04-16'
    :param period: 10
    :return:
    """
    yield_dict = defaultdict()
    start_date = get_next_trading_day_stock(end_date, -1 * period)
    for stock_code in stock_code_list:
        print stock_code
        stock_df = get_stock_df(stock_code, start_date, end_date)
        yield_dict[stock_code] = stock_df.PCT_CHG

    yield_data_frame = DataFrame(yield_dict)
    yield_data_frame = yield_data_frame.dropna(how="all")
    result = yield_data_frame.corr()
    return result


if __name__ == '__main__':
    stock_code_list = ['600901.SH', '000416.SZ', '600830.SH']
    end_date = '2018-04-11'
    period = 10
    frequency = "5min"
    result = get_stock_correlation_matrix_minute(stock_code_list, end_date, frequency, period)
    day_period = 22
    day_result = get_stock_correlation_matrix_days(stock_code_list, end_date, day_period)

