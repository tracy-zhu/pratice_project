# -*- coding: utf-8 -*-
"""
脚本用于统计在不同均线条件下一天的触发次数

Created on Mon Jun 27 09:02:46 2016

@author: Tracy Zhu
"""

import os
import matplotlib.pyplot as plt
import talib as ta
from datetime import datetime

# 日志文件
from python_base.plot_method import *

# 全局变量
out_file_folder = "F:\\different_contract_spread_picture\\"
result_file_folder = "..\\arbitrage_strategy\\result\\"


def moving_average(arr, period):
    arr_moving_average = ta.EMA(arr, period)
    arr_moving_average = arr_moving_average[period-1 :]
    return arr_moving_average


def moving_std(arr, period):
    std_list = []
    for start_index in range(len(arr) - period + 1):
        moving_std_value = arr[start_index : start_index + period].std()
        std_list.append(moving_std_value)
    std_arr = np.array(std_list)
    return std_arr


def rearrangement_data_series(data_series):
    night_data_series = data_series[data_series.index >= datetime(1900,1,1,21,0,0)]
    day_data_series = data_series[data_series.index < datetime(1900,1,1,21,0,0)]
    concat_data = pd.concat([night_data_series, day_data_series])
    concat_data_arr = np.array(concat_data.values)
    return concat_data_arr


def conjunction_spread_array(spread_array_bid, spread_array_ask):
    concat_df = pd.concat([spread_array_bid, spread_array_ask], axis=1)
    concat_df = concat_df.dropna(how='any')
    spread_array_bid_new = concat_df.Bid_Price1
    spread_array_ask_new = concat_df.Ask_Price1
    return spread_array_bid_new, spread_array_ask_new


def get_trigger_times(main_instrument_id, sub_instrument_id, trading_day, long_period, short_period, open_std, close_std):
    flag = 0
    direction = -1
    trigger_times = 0
    cum_profit = 0
    open_price = 0
    close_price = 0
    main_quote_data = read_data(main_instrument_id, trading_day)
    sub_quote_data = read_data(sub_instrument_id, trading_day)
    df_main = get_dataframe(main_quote_data, '1s')
    df_sub = get_dataframe(sub_quote_data, '1s')
    spread_array_bid = df_main.Bid_Price1 - df_sub.Bid_Price1
    spread_array_ask = df_main.Ask_Price1 - df_sub.Ask_Price1
    spread_array_bid, spread_array_ask = conjunction_spread_array(spread_array_bid, spread_array_ask)
    bid_spread_arr = rearrangement_data_series(spread_array_bid)
    ask_spread_arr = rearrangement_data_series(spread_array_ask)
    moving_bid_spread_arr = moving_average(bid_spread_arr, long_period)
    moving_ask_spread_arr = moving_average(ask_spread_arr, long_period)
    moving_bid_spread_arr2 = moving_average(bid_spread_arr, short_period)
    moving_bid_spread_arr2 = moving_bid_spread_arr2[-len(moving_bid_spread_arr):]
    moving_ask_spread_arr2 = moving_average(ask_spread_arr, short_period)
    moving_ask_spread_arr2 = moving_ask_spread_arr2[-len(moving_ask_spread_arr):]
    moving_bid_std = moving_std(bid_spread_arr, long_period)

    for index in range(1, len(moving_bid_std)):
        if flag == 0:
            if spread_array_bid[index] <= moving_bid_spread_arr[index-1] - moving_bid_std[index - 1] * open_std:
                open_price = spread_array_bid[index]
                flag = 1
                direction = 0
            elif spread_array_ask[index] >= moving_ask_spread_arr[index - 1] + moving_bid_std[index - 1] * open_std:
                open_price = spread_array_ask[index]
                flag = 1
                direction = 1

        if flag == 1:
            if spread_array_bid[index] <= moving_bid_spread_arr[index-1] - moving_bid_std[index - 1] * close_std \
                    and direction == 1:
                close_price = spread_array_bid[index]
                profit = open_price - close_price
                cum_profit += profit
                trigger_times += 1
                flag = 0
            elif spread_array_ask[index] >= moving_ask_spread_arr[index - 1] + moving_bid_std[index - 1] * close_std\
                    and direction == 0:
                open_price = spread_array_ask[index]
                profit = close_price - open_price
                cum_profit += profit
                trigger_times += 1
                flag = 0
    cum_profit = cum_profit - trigger_times * 2.4
    return cum_profit, trigger_times

    # for index in range(len(moving_bid_std)):
    #     str_line = str(bid_spread_arr[index]) + ',' + str(ask_spread_arr[index]) + ',' + \
    #                str(moving_bid_spread_arr[index]) + ',' + str(moving_bid_spread_arr2[index]) + ',' + \
    #                 str(moving_ask_spread_arr[index]) + ',' + str(moving_ask_spread_arr2[index]) + ',' + \
    #                 str(moving_bid_std[index]) + '\n'
    #     f.write(str_line)



def main():
    main_instrument_id = 'ZN1710'
    sub_instrument_id = 'ZN1711'
    long_period = 120
    short_period = 30
    trading_day = '20170904'
    result_file_name = result_file_folder + 'profit_std.csv'
    f = open(result_file_name, 'wb')
    #print>>f, 'cum_profit, trigger_times, open_std, close_std'
    open_std_list = [x / 10.0 for x in range(10, 21)]
    close_std_list = [x / 10.0 for x in range(11)]
    for open_std in open_std_list:
        for close_std in close_std_list:
            cum_profit, trigger_times = \
                get_trigger_times(main_instrument_id, sub_instrument_id, trading_day, long_period, short_period, open_std, close_std)
            print cum_profit, trigger_times, open_std, close_std
            print>>f, cum_profit, ',', trigger_times, ',' , open_std, ',', close_std
    f.close()

    # with open(result_file, 'wb') as f:
    #     f.write('bid_spread, ask_spread, long_bid_spread, short_ma_bid_spread, long_ask_spread, short_ma_ask_spread, std\n')
    #     get_trigger_times(main_instrument_id, sub_instrument_id, trading_day, long_period, short_period, f)


if __name__ == '__main__':
    main()

