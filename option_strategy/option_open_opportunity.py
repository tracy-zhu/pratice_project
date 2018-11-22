# -*- coding: utf-8 -*-
"""

# 计算商品和股票期权的开盘交易机会；

# 统计方法，开盘多少个tick内，发生剧烈波动的股票；

Mon 2018/11/19

@author: Tracy Zhu
"""
# 导入系统库
import sys
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from stock_base.stock_option_base import *

holding_time = 20
# 开盘之后的瞬间变化，以百分比为单位；
limit_open_change = 2


def find_error_in_call_auction_day(trading_day):
    """
    找出某一个交易日中，50etf期权在集合竞价发生错误定价；
    导致集合竞价开盘后具有较大波动的情况；
    :param trading_day:
    :return:
    """
    global holding_time, limit_open_change,f
    error_file_list = []
    file_name_list = filter_option_file(trading_day)
    for file_name in file_name_list:
        print(file_name)
        open_change, latest_price, open_price = find_error_in_call_auction_file(file_name, holding_time)
        if abs(open_change) > 2:
            str_line = file_name + ',' + str(open_change) + ',' + str(latest_price) + ',' + str(open_price) + '\n'
            f.write(str_line)
            error_file_list.append(file_name)
    return error_file_list


def find_error_in_call_auction_file(file_name, holding_time):
    """
    找出某一个交易日，某一个合约在开盘集合竞价有没有发生错单；
    :param file_name:
    :return:
    """
    open_price, open_tick = read_option_tick_data_ths(file_name)
    latest_price = open_tick.latest.values[holding_time]
    open_change = (float(latest_price) / float(open_price) - 1) * 100
    return open_change, latest_price, open_price


def find_error_in_call_auction(start_date, end_date):
    """
    找出过去一段时间，集合竞价有机会的合约和交易日
    :param start_date:
    :param end_date:
    :return:
    """
    trading_day_list = get_trading_day_list()
    error_file_list = []
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        trading_day = change_trading_day_format(trading_day)
        if start_date <= trading_day <= end_date:
            print(trading_day)
            error_file_list = find_error_in_call_auction_day(trading_day)
    return error_file_list


if __name__ == '__main__':
    result_file_name = "..\\option_strategy\\result\\option_error_in_call_auction_detail.txt"
    f = open(result_file_name, 'wb')
    str_line = 'file_name, open_change, latest_price, open_price\n'
    f.write(str_line)
    start_date = '2018-10-01'
    end_date = '2018-11-16'
    error_file_list = find_error_in_call_auction(start_date, end_date)
    f.close()
