# -*- coding: utf-8 -*-
"""

# 不同于通过同品种不同合约的价差来判断开盘价差的问题
# 对于相似品种，比如RB,ZC,J,JM通过相对与前收盘价的涨跌幅，如果偏差过大，开盘是否有类似于根据跨期价差的套利机会

# 输出一个DataFrame到一个csv中

Tue 2017/3/14

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：：
sys.path.append("..")
from open_price_strategy.get_open_minute_info import *
open_time = '20:59:00'
duration_time = '21:00:30'
node_1 = '21:05:00'
node_2 = '21:10:00'
limit_tick_change = 25
limit_spread_tick_change = 12
limit_percent_change = 0.005
trading_day_list = get_trading_day_list()
first_variety_id = "ZC"
second_variety_id = "I"


def get_change_during_first_change(main_quote_data):
    price_change = -9999999
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    duration_quote = main_quote_data[main_quote_data.Update_Time >= open_time]
    duration_quote = duration_quote[duration_quote.Update_Time <= duration_time]
    if len(main_open_quote) > 0:
        open_price = main_open_quote.Last_Price.values[0]
        close_price = duration_quote.Last_Price.values[-1]
        price_change = close_price - open_price
    return price_change


def open_price_change_base_on_pre_close_price(instrument_id, trading_day):
    open_price_change = 0
    price_change = 0
    quote_data = read_data(instrument_id, trading_day)
    open_price = get_open_price_from_quote_data(instrument_id, trading_day)
    pre_close_price = quote_data.Pre_Close_Price.values[0]
    if open_price != None:
        open_price_change = float(open_price - pre_close_price) / float(pre_close_price)
        price_change = get_change_during_first_change(quote_data)
    return open_price_change, price_change


out_put_file_name = "..\\open_price_strategy\\result\\open_price_abnormal_30secs_between_zc_" + second_variety_id + ".csv"
f = open(out_put_file_name, 'wb')
f.write("trading_day, percent_change_spread, first_main_instrument_id, second_main_instrument_id,"
        " first_profit, second_profit\n")


for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    if trading_day >= "20160201":
        print trading_day
        first_main_instrument_id, _ = get_variety_main(first_variety_id, trading_day)
        second_main_instrument_id, _ = get_variety_main(second_variety_id, trading_day)
        if first_main_instrument_id != None and second_main_instrument_id != None:
            first_open_price_change, first_price_change = open_price_change_base_on_pre_close_price(first_main_instrument_id, trading_day)
            second_open_price_change, second_price_change = open_price_change_base_on_pre_close_price(second_main_instrument_id, trading_day)
            price_change_spread = first_open_price_change - second_open_price_change
            if price_change_spread < 0:
                first_profit = first_price_change
                second_profit = -second_price_change
            else:
                first_profit = -first_price_change
                second_profit = second_price_change
            if abs(price_change_spread) > limit_percent_change:
                str_line = trading_day + ',' + str(price_change_spread) + ',' + first_main_instrument_id + ',' + \
                           second_main_instrument_id + "," + str(first_profit) + "," + str(second_profit) + '\n'
                f.write(str_line)

f.close()
        



    
