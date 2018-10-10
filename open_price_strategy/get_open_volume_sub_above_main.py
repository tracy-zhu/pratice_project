# -*- coding: utf-8 -*-
"""

# 将集合竞价成交量次主力合约大于主力合约的情况算出来

# 输出一个DataFrame到一个csv中

Tue 2016/12/21

@author: Tracy Zhu
"""
# 导入系统库
import sys
from datetime import timedelta

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *
trading_day_list = get_trading_day_list()

variety_id_list = ['RU', 'RB', 'NI', 'SR', 'CF', 'TA', 'RM', 'CU', 'AL', 'ZN', 'BU', 'AG', 'FG', 'MA', 'HC', 'ZC']
open_time = '20:59:00'

index_day = datetime.now() - timedelta(days=14)
index_day_str = index_day.strftime('%Y%m%d')


def get_optimal_volume(main_quote_data, sub_quote_data):
    optimal_volume = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    sub_open_quote = sub_quote_data[sub_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0 and len(sub_open_quote) > 0:
        # optimal_volume = min(main_open_quote.Total_Match_Volume.values[0], sub_open_quote.Total_Match_Volume.values[0])
        optimal_volume = main_open_quote.Total_Match_Volume.values[0]
        optimal_volume = optimal_volume / 2
    return optimal_volume


def get_open_volume(main_quote_data):
    optimal_volume = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0:
        optimal_volume = main_open_quote.Total_Match_Volume.values[0]
        optimal_volume = optimal_volume / 2
    return optimal_volume


result_file_name = '..\\open_price_strategy\\result\\sub_open_volume_above_main_open_volume.csv'
f = open(result_file_name, 'wb')
f.write('main_instrument_id, sub_instrument_id, trading_day, main_open_volume, sub_open_volume\n')
for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    if trading_day > '20171001':
        for variety_id in variety_id_list:
            print trading_day, variety_id
            main_instrument_id, sub_instrument_id = get_variety_main(variety_id, trading_day)
            main_quote_data = read_data(main_instrument_id, trading_day)
            sub_quote_data = read_data(sub_instrument_id, trading_day)
            main_open_volume = get_open_volume(main_quote_data)
            sub_open_volume = get_open_volume(sub_quote_data)
            if sub_open_volume > main_open_volume:
                str_line = main_instrument_id + ',' + sub_instrument_id + ',' + trading_day\
                           + ',' + str(main_open_volume) + ',' + str(sub_open_volume) + '\n'
                f.write(str_line)
f.close()

