# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 该脚本用于对judge_direction_after_auction_total_level进行分析
# 首先我根据脚本判断，如果持有一天到收盘，最后能不能盈利？

@author: Tracy Zhu
"""

### 导入系统库
import sys, time
import logging
from collections import deque

### 导入用户库
sys.path.append("C:\\Users\\Tracy Zhu\\Desktop\\tool\\open_price_strategy")
from plot_depth_quote import *
open_time = "20:59:00"
target_result_file_name = "C:\\Users\\Tracy Zhu\\Desktop\\tool\\open_price_strategy\\judge_direction_after_auction_total_level.csv"
target_result_file = open(target_result_file_name, 'r')
result_lines = target_result_file.readlines()
target_result_file.close()

output_file_name = "deal_judge_direction_result_file.csv"
out_file = open(output_file_name, 'wb')
print>>out_file, "instrument_id, trading_day, open_direction, open_price, close_price, profit"
profit = 0
for one_line in result_lines[1:]:
    one_list = one_line.split(',')
    instrument_id = one_list[0]
    trading_day = one_list[1]
    open_direction = one_list[5]
    variety_id = get_variety_id(instrument_id)
    _, unit, _ = get_variety_information(variety_id)
    close_price = get_close_price(instrument_id, trading_day)
    open_price = get_open_price_from_quote_data(instrument_id, trading_day)
    print instrument_id, trading_day
    if open_direction == 'long':
        profit = close_price - open_price
        profit = profit * unit
    elif open_direction == 'short':
        profit = open_price - close_price
        profit = profit * unit
    print >> out_file, instrument_id, ',', trading_day, ',', open_direction, ',', open_price, ',', close_price, ',', profit

out_file.close()