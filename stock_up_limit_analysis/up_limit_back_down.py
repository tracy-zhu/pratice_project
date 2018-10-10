# -*- coding: utf-8 -*-
"""

# 筛选前n天该股票涨停，当股票价格回调到涨停的起点的时候，后面几天的走势；

Mon 2018/7/23

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math
import itertools
import scipy.stats as s

# 导入用户库：
sys.path.append("..")
from stock_base.stock_data_api import *

out_file_folder = '..\\stock_up_limit_analysis\\result\\'
list_A = get_all_stock_code_list("2018-07-20")
trading_day_list = get_trading_day_list()


def find_up_back_down_stock(trading_day, back_period, limit_percent, f):
    """
    找出股票回撤到几天前涨停开始的位置，符合条件的股票，避免前期涨幅过大，正常回调的，要想个办法
    先将股票的结果输出到一个文件中，在对文件进行分析，方便进行操作；
    :param trading_day:
    :param back_period:
    :param limit_percent:
    :return:
    """
    for stock_code in list_A:
        flag, up_date = stock_is_up_limit_back_period(stock_code, trading_day, back_period)
        if flag:
            buy_price, lower_limit_price = judge_stock_back_down(stock_code, trading_day, up_date, limit_percent)
            if buy_price != 0:
                str_line = stock_code + ',' + trading_day + ',' + str(buy_price) + ',' + str(lower_limit_price) + '\n'
                f.write(str_line)


def print_select_code_out(start_date, end_date, back_period, limit_percent):
    """
    将交易日选择的股票输出出来；
    :param start_date:
    :param end_date:
    :param back_period:
    :param limit_percent:
    :return:
    """
    out_file_name = out_file_folder + "up_back_down_stock_" + str(back_period) + '_.csv'
    f = open(out_file_name, 'wb')
    f.write('stock_code, trading_day, buy_price, stop_price\n')
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        trading_day = change_trading_day_format(trading_day)
        print(trading_day)
        if start_date <= trading_day <= end_date:
            find_up_back_down_stock(trading_day, back_period, limit_percent, f)
    f.close()


def judge_stock_back_down(stock_code, trading_day, up_date, limit_percent):
    """
    判断股票是否回撤到距离最近涨停板附近的位置
    :param stock_code:
    :param trading_day:
    :param up_date:
    :return:
    """
    buy_price = 0
    lower_limit_price = 0
    start_date = get_next_trading_day_stock(up_date, -1)
    stock_df = get_stock_df(stock_code, start_date, trading_day)
    if len(stock_df) > 0:
        pre_close = stock_df.CLOSE.values[0]
        up_limit_price = pre_close * (1 + limit_percent)
        lower_limit_price = pre_close * (1 - limit_percent)
        open_price = stock_df.OPEN.values[-1]
        lower_price = stock_df.LOW.values[-1]
        high_price = stock_df.HIGH.values[-1]
        if lower_limit_price <= open_price <= up_limit_price:
            buy_price = open_price
        elif open_price > up_limit_price and lower_price <= up_limit_price:
            buy_price = up_limit_price
        elif open_price <= lower_limit_price and high_price >= lower_limit_price:
            buy_price = lower_limit_price
    return buy_price, lower_limit_price


def stock_holding_description(stock_code, trading_day, holding_period, stop_price):
    """
    计算股票开仓之后的持仓收益，stop_price为止损价格
    :param stock_code:
    :param trading_day:
    :param holding_period:
    :param stop_price:
    :return:
    """
    end_date = get_next_trading_day_stock(trading_day, holding_period)
    start_date = get_next_trading_day_stock(trading_day, 1)
    stock_df = get_stock_df(stock_code, start_date, end_date)
    lowest_price = stock_df.LOW.min()
    if lowest_price < stop_price:
        close_price = stop_price
    else:
        close_price = stock_df.CLOSE.values[-1]
    return close_price


def select_code_analysis(out_file_name, holding_period):
    """
    读取之前得出的文件数据,分析股票后面几天的走势
    :param out_file_name:
    :return:
    """
    profit_yield_list = []
    f = open(out_file_name, 'r')
    result_out_file = "..\\stock_up_limit_analysis\\result\\" + "profit_yield_series_" + str(holding_period) + "_.csv"
    str_lines = f.readlines()
    f.close()
    w = open(result_out_file, 'wb')
    w.write('stock_code, trading_day, buy_price, stop_price, close_price, profit_yield\n')
    for line in str_lines[1:]:
        line_list = line.split(",")
        stock_code = line_list[0]
        trading_day = line_list[1]
        buy_price = float(line_list[2])
        stop_price = float(line_list[3])
        close_price = stock_holding_description(stock_code, trading_day, holding_period, stop_price)
        profit_yield = float(close_price) / float(buy_price) - 1
        str_line = stock_code + ',' + trading_day + ',' + str(buy_price) + ',' + str(stop_price) + ',' + str(close_price) + ',' + str(profit_yield) + '\n'
        w.write(str_line)
    w.close()


def profit_analysis(result_out_file):
    df = pd.read_csv(result_out_file)
    yield_series = df[' profit_yield']
    win_yield_series = yield_series[yield_series > 0]
    win_ratio = float(len(win_yield_series)) / float(len(yield_series))
    yield_series.hist()
    print(yield_series.mean())
    print(win_ratio)
    print(len(yield_series))


if __name__ == '__main__':
    start_date = '2018-01-01'
    end_date = '2018-07-20'
    back_period = 3
    limit_percent = 0.03
    holding_period = 3
    out_file_name = "..\\stock_up_limit_analysis\\result\\up_back_down_stock_3_.csv"
    result_out_file = "..\\stock_up_limit_analysis\\result\\" + "profit_yield_series_" + str(holding_period) + "_.csv"
    # print_select_code_out(start_date, end_date, back_period, limit_percent)
    # select_code_analysis(out_file_name, holding_period)
    profit_analysis(result_out_file)
