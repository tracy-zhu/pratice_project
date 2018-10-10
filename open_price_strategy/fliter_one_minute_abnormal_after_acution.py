# -*- coding: utf-8 -*-
"""

# 本脚本用于计算开盘一分钟比较特殊的情况
# 并计算反方向持有到两个时间节点的利润
# 要将主力和次主力发生错单的情况筛选出去

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
duration_time = '21:00:10'
node_1 = '21:05:00'
node_2 = '21:10:00'
limit_tick_change = 10
limit_spread_tick_change = 12

trading_day_list = get_trading_day_list()

#variety_id_list = ['RU', 'RB', 'NI', 'CU', 'AL', 'ZN', 'BU', 'AG', 'HC', "PB"]
variety_id_list = ["RB", "ZC", "JM", "J"]


def get_open_interest_change(instrument_id, trading_day):
    pre_open_interest = 0
    open_interest = 0
    file_name = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + trading_day + "\\" + instrument_id + ".csv"
    with open(file_name, 'r') as f2:
        str_lines = f2.readlines()
        line = str_lines[1]
        line_list = line.split(",")
        pre_open_interest = float(line_list[22])
    quote_data = read_data(instrument_id, trading_day)
    main_open_quote = quote_data[quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0:
        open_interest = main_open_quote.Open_Interest.values[0]
    open_interest_change = open_interest - pre_open_interest
    return open_interest_change


def get_open_price_change_from_close_price(main_quote_data, sub_quote_data):
    spread_change_price = 100
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    sub_open_quote = sub_quote_data[sub_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0 and len(sub_open_quote) > 0 :
        main_open_price = main_open_quote.Last_Price.values[0]
        sub_open_price = sub_open_quote.Last_Price.values[0]
        main_pre_close_price = main_open_quote.Pre_Close_Price.values[0]
        sub_pre_close_price = sub_open_quote.Pre_Close_Price.values[0]
        pre_close_spread = main_pre_close_price - sub_pre_close_price
        open_price = main_open_price - sub_open_price
        spread_change_price = abs(open_price - pre_close_spread)
    return spread_change_price


def get_change_during_first_change(main_quote_data):
    """
    找出前20s，一个合约的价格变化
    :param main_quote_data: 一个合约的行情读入内存
    :return:
    """
    price_change = -9999999
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    duration_quote = main_quote_data[main_quote_data.Update_Time >= open_time]
    duration_quote = duration_quote[duration_quote.Update_Time <= duration_time]
    if len(main_open_quote) > 0:
        open_price = main_open_quote.Last_Price.values[0]
        close_price = duration_quote.Last_Price.values[-1]
        price_change = close_price - open_price
    return price_change


def find_extreme_price_change_corrleation_variety():
    """
    这个函数应用找出4个黑色系开盘后20s波动超过一定幅度的行情，分方向，希望能够从中找出两个相似合约
    :return:
    """
    out_file_name = '..\\open_price_strategy\\result\\extreme_change_in_10_secs_after_open_auction_without_wrong_order.csv'
    f = open(out_file_name, "wb")
    print>> f, "main_instrument_id, trading_day, tick_change, open_volume, open_interest_change"
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day > '20180301':
            print trading_day
            instrument_file_list = get_instrument_file_list(trading_day)
            for (variety_id, instrument_list) in instrument_file_list.items():
                if variety_id != "AP":
                    print variety_id
                    tick, unit, _ = get_variety_information(variety_id)
                    main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
                    if main_instrument_id != None and sub_instrument_id != None:
                        main_quote_data = read_data(main_instrument_id, trading_day)
                        sub_quote_data = read_data(sub_instrument_id, trading_day)
                        #open_volume, mean_volume = get_open_volume_series(main_instrument_id, trading_day)
                        # _, spread_price_change = \
                        #     get_open_minute_change_except_wrong_order(main_quote_data, sub_quote_data)
                        main_price_change = get_change_during_first_change(main_quote_data)
                        main_tick_change = main_price_change / tick
                        sub_price_change = get_change_during_first_change(sub_quote_data)
                        sub_tick_change = sub_price_change / tick
                        spread_price_change = get_open_price_change_from_close_price(main_quote_data, sub_quote_data)
                        spread_tick_change = spread_price_change / tick
                        if abs(main_tick_change) > limit_tick_change and spread_tick_change < limit_spread_tick_change:
                            open_interest_change = get_open_interest_change(main_instrument_id, trading_day)
                            open_volume = get_open_volume(main_quote_data)
                            str_line = main_instrument_id + ',' + trading_day + ',' + str(main_tick_change) + ',' \
                                       + str(open_volume) + "," + str(open_interest_change) + "\n"
                            f.write(str_line)
                        if abs(sub_tick_change) > limit_tick_change and spread_tick_change < limit_spread_tick_change:
                            open_volume = get_open_volume(sub_quote_data)
                            open_interest_change = get_open_interest_change(sub_instrument_id, trading_day)
                            str_line = sub_instrument_id + ',' + trading_day + ',' + str(sub_tick_change) + ',' \
                                       + str(open_volume) + "," + str(open_interest_change) + "\n"
                            f.write(str_line)
    f.close()


def find_extreme_price_change_during_20secs():
    out_file_name = '..\\open_price_strategy\\result\\extreme_change_in_20_secs_after_open_auction_without_wrong_order_test.csv'
    f = open(out_file_name, "wb")
    print>> f, "main_instrument_id, trading_day, tick_change, open_volume, open_interest_change"
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day > '20170502':
            print trading_day
            instrument_file_list = get_instrument_file_list(trading_day)
            for (variety_id, instrument_list) in instrument_file_list.items():
                if variety_id in variety_id_list:
                    print variety_id
                    tick, unit, _ = get_variety_information(variety_id)
                    main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
                    if main_instrument_id != None and sub_instrument_id != None:
                        main_quote_data = read_data(main_instrument_id, trading_day)
                        sub_quote_data = read_data(sub_instrument_id, trading_day)
                        #open_volume, mean_volume = get_open_volume_series(main_instrument_id, trading_day)
                        # _, spread_price_change = \
                        #     get_open_minute_change_except_wrong_order(main_quote_data, sub_quote_data)
                        main_short_profit, main_long_profit, main_open_price = get_open_minute_change(main_quote_data)
                        main_price_change = abs(main_short_profit) if abs(main_short_profit) > abs(main_long_profit) else abs(main_long_profit)
                        main_tick_change = main_price_change / tick
                        sub_short_profit, sub_long_profit, sub_open_price = get_open_minute_change(sub_quote_data)
                        sub_price_change = abs(sub_short_profit) if abs(sub_short_profit) > abs(sub_long_profit) else abs(sub_long_profit)
                        sub_tick_change = sub_price_change / tick
                        spread_price_change = get_open_price_change_from_close_price(main_quote_data, sub_quote_data)
                        spread_tick_change = spread_price_change / tick
                        if main_tick_change > limit_tick_change and spread_tick_change < limit_spread_tick_change:
                            open_interest_change = get_open_interest_change(main_instrument_id, trading_day)
                            open_volume = get_open_volume(main_quote_data)
                            str_line = main_instrument_id + ',' + trading_day + ',' + str(main_tick_change) + ',' \
                                       + str(open_volume) + "," + str(open_interest_change) + "\n"
                            f.write(str_line)
                        if sub_tick_change > limit_tick_change and spread_tick_change < limit_spread_tick_change:
                            open_volume = get_open_volume(sub_quote_data)
                            open_interest_change = get_open_interest_change(sub_instrument_id, trading_day)
                            str_line = sub_instrument_id + ',' + trading_day + ',' + str(sub_tick_change) + ',' \
                                       + str(open_volume) + "," + str(open_interest_change) + "\n"
                            f.write(str_line)
    f.close()

if __name__ == '__main__':
    find_extreme_price_change_corrleation_variety()
