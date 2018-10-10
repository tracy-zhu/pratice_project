# -*- coding: utf-8 -*-
"""

# 筛选前n天该股票涨停，当天高开5%，或低开5%后前的走势；

# 注意要当天一字板涨停的股票筛除，没有参考意义；

Mon 2018/7/23

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
from datetime import date

list_A = get_all_stock_code_list("2018-07-20")
trading_day_list = get_trading_day_list()
out_file_folder = '..\\stock_up_limit_analysis\\result\\'


def find_condition_stock(trading_day, back_period, limit_percent, f):
    """
    找出当天符合条件的股票，前n天有涨停，当天低开或者高开5%,选出该股票后期的走势
    :param trading_day:
    :param back_period:
    :return:
    """
    condition_num = 0
    for stock_code in list_A:
        flag, up_date = stock_is_up_limit_back_period(stock_code, trading_day, back_period)
        if flag:
            open_flag = calc_open_percent(stock_code, trading_day, limit_percent)
            if open_flag:
                condition_num += 1
                str_line = stock_code + ',' + trading_day + '\n'  
                f.write(str_line)


def calc_open_percent(stock_code, trading_day, limit_percent):
    """
    计算一只股票开盘高开或者低开幅度；
    :param stock_code:
    :param trading_day:
    :param limit_percent: 0.05
    :return:
    """
    flag = False
    start_date = get_next_trading_day_stock(trading_day, -1)
    stock_df = get_stock_df(stock_code, start_date, trading_day)
    if len(stock_df) > 0:
        pre_close_price = stock_df.CLOSE.values[0]
        if pre_close_price != 0:
            open_percent = float(stock_df.OPEN.values[-1]) / float(pre_close_price) - 1
            if open_percent > limit_percent or open_percent < -1 * limit_percent:
                flag = True
    return flag


def stock_description_today(stock_code, trading_day, holding_period):
    """
    描述该股票选出的当天的走势，是否涨停，是否收阳线，以及n天后收盘价如何；
    :param stock_code:
    :param trading_day:
    :return: is_cross_bar是否为一字板
    """
    up_flag = False
    profit_flag = False
    is_cross_bar = False
    holding_profit = 0
    end_date = get_next_trading_day_stock(trading_day, holding_period)
    stock_df = get_stock_df_qfq(stock_code, trading_day, end_date)
    if len(stock_df) > 0:
        open_price = stock_df.OPEN.values[0]
        close_price = stock_df.CLOSE.values[0]
        pct_chg =  stock_df.PCT_CHG.values[0]
        end_close_price = stock_df.CLOSE.values[-1]
        up_flag = True if pct_chg > 9.3 else False
        profit_flag = True if close_price >= open_price else False
        if open_price != 0 and end_close_price >0:
            holding_profit = float(end_close_price) / float(open_price) - 1
        is_cross_bar = True if open_price == close_price else False
    return up_flag, profit_flag, holding_profit, is_cross_bar


def print_select_code_out(start_date, end_date):
    """
    将符合条件的代码输出到一个csv文件中去
    """
    back_period = 1
    limit_percent = 0.05
    out_file_name = out_file_folder + "abnormal_opening_stock_" + str(limit_percent) + ".csv"
    f = open(out_file_name, 'wb')
    f.write('stock_code, trading_day\n')
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        trading_day = change_trading_day_format(trading_day)
        if start_date <= trading_day <= end_date:
            find_condition_stock(trading_day, back_period, limit_percent, f)
    f.close()


def result_stat(out_file_name, holding_period):
    """
    统计指定日期，符合该条件的概率；
    :param start_date:
    :param end_date:
    :return:
    """
    f = open(out_file_name, 'r')
    str_lines = f.readlines()
    f.close()
    result_file = out_file_folder + 'abnormal_open_result_stat.csv'
    w = open(result_file, 'wb')
    w.write('stock_code,trading_day,holding_profit,up_flag,profit_flag,is_cross_bar\n')
    for line in str_lines[1:]:
        stock_code = line.split(',')[0]
        trading_day = line.split(',')[1][:-1]
        trading_day = "-".join([trading_day.split('-')[0], (trading_day.split('-')[1]).zfill(2),(trading_day.split('-')[2]).zfill(2)])
        up_flag, profit_flag, holding_profit, is_cross_bar = stock_description_today(stock_code, trading_day, holding_period)
        up_flag_num = 1 if up_flag else 0
        profit_flag_num = 1 if profit_flag else 0
        is_cross_bar_num = 1 if is_cross_bar else 0 
        str_line = stock_code + ',' + trading_day + ',' + str(holding_profit) + ',' + str(up_flag_num) + ',' + str(profit_flag_num) + ',' + str(is_cross_bar_num) + '\n'
        w.write(str_line)
    print "total_condition_num is " + str(len(str_lines))
    w.close()


def profit_result_analysis(result_file):
    df = pd.read_csv(result_file)
    df = df[df['is_cross_bar'] == 0]
    yield_series = df['holding_profit']
    profit_num = len(df[df['profit_flag'] == 1])
    up_num = len(df[df['up_flag'] == 1])
    profit_ratio = float(profit_num) / float(len(df))
    up_ratio = float(up_num) / float(len(df))
    win_yield_series = yield_series[yield_series > 0]
    win_ratio = float(len(win_yield_series)) / float(len(yield_series))
    print "profit ratio is " + str(profit_ratio)
    print "up_ratio is " + str(up_ratio)
    print "condition num is " + str(len(df))
    print "holding profit ratio is " + str(win_ratio)
    yield_series.hist()


if __name__ == '__main__':
    start_date = '2018-01-01'
    end_date = '2018-07-27'
    holding_period = 3
    limit_percent = 0.05
    # print_select_code_out(start_date, end_date)
    out_file_name = out_file_folder + "abnormal_opening_stock_" + str(limit_percent) + ".csv"
    result_stat(out_file_name, holding_period)
    result_file = out_file_folder + 'abnormal_open_result_stat.csv'
    profit_result_analysis(result_file)
