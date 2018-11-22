# -*- coding: utf-8 -*-
"""

# 根据股票分钟数据计算各种各样的高频因子，这段脚本是计算参与者结构类因子；

1. 收盘成交量因子；
2. 正成交量指标PVI

Fri 2018/11/16

@author: Tracy Zhu
"""

import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_option_base import *
from python_base.plot_method import *


def closing_volume_ratio_day(trading_day):
    """
    计算收盘前15分钟成交量占日总成交量的比例（不包含集合竞价）
    去除掉当天已经涨停的股票；
    :param trading_day:
    :return:
    """
    volume_ratio_dict = defaultdict()
    stock_list = get_all_stock_code_list(trading_day)
    for stock_code in stock_list:
        print(stock_code)
        volume_ratio = closing_volume_ratio(stock_code, trading_day)
        if volume_ratio > 0:
            volume_ratio_dict[stock_code] = volume_ratio
    volume_ratio_series = Series(volume_ratio_dict)
    sort_volume_ratio_series = volume_ratio_series.sort_values()
    return sort_volume_ratio_series


def closing_volume_ratio(stock_code, trading_day):
    """
    计算单个股票的收盘成交量占比,
    要将已经涨跌停的股票删除掉，即使涨停也有排队成交的量；
    :param stock_code:
    :param trading_day:
    :return:
    """
    volume_ratio = 0
    stock_df = read_stock_tick_data_qian(stock_code, trading_day)
    if len(stock_df) > 0:
        spot_time = trading_day + " 14:45:00"
        select_df = stock_df[stock_df.index >= spot_time]
        if select_df.high.values[0] != select_df.latest.values[0] and select_df.low.values[0] != select_df.latest.values[0]:
            spot_volume = select_df.volume.values[-1] - select_df.volume.values[0]
            all_day_volume = select_df.volume.values[-1]
            volume_ratio = float(spot_volume) / float(all_day_volume)
    return volume_ratio


if __name__ == '__main__':
    stock_code = '000001.SZ'
    trading_day = '2018-11-15'

