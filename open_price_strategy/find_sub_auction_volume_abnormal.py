# -*- coding: utf-8 -*-
"""

# 找出次主力成交量比较异常的行情

# 输出一个DataFrame到一个csv中

Thu 2017/11/23

@author: Tracy Zhu
"""
# 导入系统库
import sys
from datetime import timedelta

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *
from python_base.get_open_volume_series_instrument import *
trading_day_list = get_trading_day_list()

variety_id_list = ['RU', 'RB', 'NI', 'SR', 'CF', 'TA', 'RM', 'CU', 'AL', 'ZN', 'BU', 'AG', 'FG', 'MA', 'HC', 'ZC']
open_time = '20:59:00'
limit_ma = 2.5


def get_open_volume(main_quote_data):
    optimal_volume = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0:
        optimal_volume = main_open_quote.Total_Match_Volume.values[0]
        optimal_volume = optimal_volume / 2
    return optimal_volume


result_file_name = '..\\open_price_strategy\\result\\sub_open_volume_above_main_open_volume.csv'
f = open(result_file_name, 'wb')
f.write('sub_instrument_id, trading_day, last_open_volume, mean_volume\n')
for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    if trading_day > '20170701':
        for variety_id in variety_id_list:
            print trading_day, variety_id
            main_instrument_id, sub_instrument_id = get_variety_main(variety_id, trading_day)
            if sub_instrument_id != None:
                last_open_volume, mean_volume = get_open_volume_series(sub_instrument_id, trading_day)
                ma_ratio = float(last_open_volume) / float(mean_volume)
                if ma_ratio > limit_ma:
                    str_line = sub_instrument_id + ',' + trading_day \
                               + ',' + str(last_open_volume) + ',' + str(mean_volume) + '\n'
                    f.write(str_line)
f.close()

