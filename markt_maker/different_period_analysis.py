# -*- coding: utf-8 -*-
"""

# 本脚本主要分析分段时间的行情的研究
# 首先研究可以通过什么方法就不同的行情切分出来
# 然后研究如何研究不同的行情

Tue 2017/10/19

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math
import talib as ta
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *


def get_quote_segmentation(instrument_id, trading_day):
    period1 = ["24:00:00", "01:00:00"]
    period2 = ['09:00:00', '10:00:00']
    period3 = ["14:00:00", '15:00:00']
    quote_data = read_data(instrument_id, trading_day)
    first_quote = quote_data[quote_data.Update_Time <= period1[1]]
    second_quote = quote_data[quote_data.Update_Time <= period2[1]]
    second_quote = second_quote[second_quote.Update_Time >= period2[0]]
    third_quote = quote_data[quote_data.Update_Time >= period3[0]]
    third_quote = third_quote[third_quote.Update_Time <= period3[1]]
    return first_quote, second_quote, third_quote


def get_distant_change(quote_data):
    """
    获取不同quote_data时间段里中间价格移动的绝对距离
    :param quote_data:
    :return:
    """
    total_match_volume = 0
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    price_change_arr = np.array(middle_price_series.diff())
    abs_price_change_arr = np.abs(price_change_arr)
    abs_price_change_arr = np.nan_to_num(abs_price_change_arr)
    total_change = abs_price_change_arr.sum()
    if len(quote_data) > 0:
        total_match_volume = quote_data.Total_Match_Volume.values[-1] - quote_data.Total_Match_Volume.values[0]
    return total_change, total_match_volume


def different_period_distant():
    result_file_name = '..\\markt_maker\\result\\different_period_distant.csv'
    f = open(result_file_name, 'wb')
    f.write('trading_day, first_quote_distant, second_quote_distant, third_quote_distant, first_match_volume, '
            'second_match_volume, third_match_volume\n')
    instrument_id = 'AL1712'
    trading_day_list = get_trading_day_list()
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        print trading_day
        if trading_day > '20170915':
            first_quote, second_quote, third_quote = get_quote_segmentation(instrument_id, trading_day)
            first_distant, first_match_volume = get_distant_change(first_quote)
            second_distant, second_match_volume = get_distant_change(second_quote)
            third_distant, third_match_volume = get_distant_change(third_quote)
            str_line = trading_day + ',' + str(first_distant) + ',' + str(second_distant) + ',' + str(third_distant) + ','\
                      +  str(first_match_volume) + ','+ str(second_match_volume) + ',' + str(third_match_volume) + '\n'
            f.write(str_line)
    f.close()


if __name__ == '__main__':
    different_period_distant()
