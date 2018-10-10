# -*- coding: utf-8 -*-
"""

# 脚本将一个合约的开盘集合竞价之后的价差相对于昨日收盘价的价差做一个统计分析

# 算出什么样的价差合适做价差范围

Tue 2017/12/12

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：：
sys.path.append("..")
from python_base.open_price_algorithm import *
from python_base.get_open_volume_series_instrument import *


def get_open_price_pre_close_price(instrument_id, trading_day):
    open_price = None
    pre_close_price = None
    quote_data = read_data(instrument_id, trading_day)
    if len(quote_data) > 100:
        open_price = get_open_price_from_quote_data(instrument_id, trading_day)
        pre_close_price = quote_data.Pre_Close_Price.values[0]
    return open_price, pre_close_price


def open_price_spread_change(first_instrument_id, second_instrument_id, trading_day):
    """
    计算两个合约价格集合竞价相对于前收盘价的价差变化, unit: tick
    :param first_instrument_id:
    :param second_instrument_id:
    :param trading_day:
    :return: 当个交易日开盘的价差变化
    """
    spread_change = np.nan
    variety_id = get_variety_id(first_instrument_id)
    tick, _ ,_ = get_variety_information(variety_id)
    first_open_price, first_pre_close_price = get_open_price_pre_close_price(first_instrument_id, trading_day)
    second_open_price, second_pre_close_price = get_open_price_pre_close_price(second_instrument_id, trading_day)
    if first_pre_close_price != None and second_pre_close_price != None and first_open_price != None \
            and second_open_price != None:
        pre_close_spread = (first_pre_close_price - second_pre_close_price) / tick
        open_spread = (first_open_price - second_open_price) / tick
        spread_change = open_spread - pre_close_spread
    return spread_change


def get_sort_instrument_id(variety_id, trading_day):
    best_quote_frame = Series()
    best_quote_frame_sort = Series()
    instrument_file_list = get_instrument_file_list(trading_day)
    instrument_list = instrument_file_list[variety_id]
    quote_map = {}
    if len(instrument_list) > 2:
        for one_file_name in instrument_list:
            quote_file = open(one_file_name, "r")
            quote_list = quote_file.readlines()
            quote_file.close()
            instrument_id = one_file_name.split("\\")[-1].split(".")[0]
            close_quote = CBest_Market_Data_Field()
            if len(quote_list) > 2000:
                if len(quote_list[-1]) > 2:
                    close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-1])
                else:
                    close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-2])
                quote_map[instrument_id] = close_quote
            else:
                close_quote = CBest_Market_Data_Field()
                close_quote.Total_Match_Volume = 10
                quote_map[instrument_id] = close_quote


        # 寻找主力合约
        if len(quote_map) > 2:
            # 寻找主力合约
            for (instrument_id, close_quote) in quote_map.items():
                best_quote = Series([instrument_id, close_quote.Total_Match_Volume])
                best_quote_frame = best_quote_frame.append(best_quote)
            best_quote_frame = Series(best_quote_frame[1].values, index=best_quote_frame[0].values)
            best_quote_frame_sort = best_quote_frame.sort_values()
    instrument_id_list = best_quote_frame_sort.index
    instrument_id_sort = instrument_id_list[::-1]
    return instrument_id_sort


def open_price_spread_change_for_variety_id(variety_id, trading_day, arg):
    """
    根据合约算出主力和次主力或者之后的价差的变化
    :param variety_id:
    :param trading_day:
    :param arg: 0, 次主力; 1, 次次主力；， 2，次次次主力；
    :return: spread_change
    """
    spread_change = None
    instrument_id_sort = get_sort_instrument_id(variety_id, trading_day)
    tick, _, _ = get_variety_information(variety_id)
    first_instrument_id = instrument_id_sort[0]
    second_instrument_id = None
    if arg == 0:
        second_instrument_id = instrument_id_sort[1]
    elif arg == 1:
        second_instrument_id = instrument_id_sort[2]
    elif arg == 2:
        second_instrument_id = instrument_id_sort[3]
    first_open_price, first_pre_close_price = get_open_price_pre_close_price(first_instrument_id, trading_day)
    second_open_price, second_pre_close_price = get_open_price_pre_close_price(second_instrument_id, trading_day)
    if first_pre_close_price != None and second_pre_close_price != None and first_open_price != None \
            and second_open_price != None:
        pre_close_spread = (first_pre_close_price - second_pre_close_price) / tick
        open_spread = (first_open_price - second_open_price) / tick
        spread_change = open_spread - pre_close_spread
    return spread_change


if __name__ == '__main__':
    result_name = "..\\open_price_strategy\\result\\price_range_tick_stat\\price_range_tick.csv"
    f = open(result_name, 'wb')
    f.write("variety_id, sub_tick_range, ssub_tick_range\n")
    variety_id_list = ['RU', 'RB', 'NI', 'SR', 'CF', 'TA', 'RM', 'OI', 'CU', 'AL', 'ZN', 'BU', 'AG', 'FG', 'WH', 'MA', 'HC', 'ZC', 'PB',
     'SN', 'AU']
    trading_day_list = get_trading_day_list()
    for variety_id in variety_id_list:
        spread_change_list_sub = []
        spread_change_list_ssub = []
        for trade_day in trading_day_list:
            trading_day = trade_day[:-1]
            if trading_day > "20170101":
                    print trading_day, variety_id
                    spread_change_sub = open_price_spread_change_for_variety_id(variety_id, trading_day, 1)
                    spread_change_ssub = open_price_spread_change_for_variety_id(variety_id, trading_day, 2)
                    if spread_change_sub < 200 and spread_change_ssub < 200 and spread_change_ssub != None \
                            and spread_change_sub != None:
                        spread_change_list_sub.append(spread_change_sub)
                        spread_change_list_ssub.append(spread_change_ssub)
        sub_tick_range = np.std(spread_change_list_sub) * 1.28
        ssub_tick_range = np.std(spread_change_list_ssub) * 1.65
        str_line = variety_id + "," + str(sub_tick_range) + "," + str(ssub_tick_range) + '\n'
        f.write(str_line)
    f.close()



