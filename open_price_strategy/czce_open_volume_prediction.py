# -*- coding: utf-8 -*-
"""

# 本脚本用来计算不同品种集合竞价最优成交量

# 输出一个DataFrame到一个csv中

Tue 2016/12/21

@author: Tracy Zhu
"""
# 导入系统库
import sys
from datetime import timedelta

# 导入用户库：：
sys.path.append("..")
from open_price_strategy.open_spread_stat import *
trading_day_list = get_trading_day_list()

variety_id_list = ['SR', 'CF', 'TA', 'RM', 'FG', 'MA', 'ZC']
open_time = '20:59:00'
close_period = '14:50:00'
close_period_2 = "14:30:00"


def get_open_volume(main_quote_data):
    optimal_volume = 0
    open_auction_periods = 0
    max_price = 0
    min_price = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0:
        optimal_volume = main_open_quote.Total_Match_Volume.values[0]
        open_auction_periods = main_quote_data.index[main_quote_data.Update_Time == open_time][0]
        open_price_series = main_quote_data.Open_Price.head(open_auction_periods)
        open_price_series = open_price_series[open_price_series > 0]
        max_price = open_price_series.max()
        min_price = open_price_series.min()
        optimal_volume = optimal_volume / 2
    return optimal_volume, open_auction_periods, max_price, min_price


def get_last_index_minutes_match_volume(instrument_id, trading_day, total_match_volume, close_period):
    main_quote_data = read_data(instrument_id, trading_day)
    optimal_volume = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == close_period]
    if len(main_open_quote) > 0:
        optimal_volume = main_open_quote.Total_Match_Volume.values[0]
    else:
        for i in range(1,60):
            close_period_new = close_period[:-2] + str(i).zfill(2)
            if len(main_quote_data[main_quote_data.Update_Time == close_period_new]) > 0:
                optimal_volume = main_quote_data[main_quote_data.Update_Time == close_period_new].Total_Match_Volume.values[0]
                break
    last_30_minutes_match_volume = total_match_volume - optimal_volume
    return last_30_minutes_match_volume


def get_close_quote(instrument_id, trading_day):
    one_file_name = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + trading_day + "\\" + instrument_id + ".csv"
    quote_file = open(one_file_name, "r")
    quote_list = quote_file.readlines()
    quote_file.close()
    close_quote = CBest_Market_Data_Field()
    if len(quote_list) > 2000:
        if len(quote_list[-1]) > 2:
            close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-1])
        else:
            close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-2])
    return close_quote


result_file = '..\\open_price_strategy\\result\\czce_open_volume_prediction\\czce_open_volume_series_wrong_order.csv'
f = open(result_file,'wb')
f.write('instrument_id,trading_day,open_volume,pre_total_volume,last_10m_match_volume, last_30m_match_volume, '
        'last_10m_open_interest_change, last_30m_open_interest_change, spread_change\n')
for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    if trading_day > '20170203':
        pre_trading_day = get_pre_trading_day(trading_day)
        instrument_file_list = get_instrument_file_list(pre_trading_day)
        if instrument_file_list != None:
            for (variety_id, instrument_list) in instrument_file_list.items():
                if variety_id in variety_id_list:
                    main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
                    if sub_instrument_id != None:
                        print trading_day, sub_instrument_id
                        spread_change = open_price_spread_change(main_instrument_id, sub_instrument_id, trading_day)
                        quote_data = read_data(sub_instrument_id, trading_day)
                        pre_quote_data = read_data(sub_instrument_id, pre_trading_day)
                        if len(quote_data) > 0 and len(pre_quote_data) > 0:
                            optimal_volume, _, _, _ = get_open_volume(quote_data)
                            close_quote = get_close_quote(sub_instrument_id, pre_trading_day)
                            total_match_volume = close_quote.Total_Match_Volume
                            open_interest = close_quote.Open_Interest
                            node_quote_1 = get_slice_quote_on_time(pre_quote_data, close_period)
                            node_quote_2 = get_slice_quote_on_time(pre_quote_data, close_period_2)
                            if not (node_quote_1.empty or node_quote_2.empty) and abs(spread_change) > 10:
                                match_volume_10 = total_match_volume - node_quote_1.Total_Match_Volume
                                open_interest_change_10 = open_interest - node_quote_1.Open_Interest
                                match_volume_30 = total_match_volume - node_quote_2.Total_Match_Volume
                                open_interest_change_30 = open_interest - node_quote_2.Open_Interest
                                str_line = sub_instrument_id + "," + trading_day + "," + str(optimal_volume)  + "," + \
                                           str(total_match_volume) + "," + str(match_volume_10) + "," + str(match_volume_30) + "," + \
                                           str(open_interest_change_10) + "," + str(open_interest_change_30) + "," + str(spread_change) + "\n"
                                f.write(str_line)
f.close()
