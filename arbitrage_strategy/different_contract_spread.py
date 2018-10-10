# -*- coding: utf-8 -*-
"""
This script is used for get contract spread of different contract

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


def get_spread_array_map(main_instrument_id, sub_instrument_id, trading_day):
    main_quote_data = read_data(main_instrument_id, trading_day)
    sub_quote_data = read_data(sub_instrument_id, trading_day)
    df_main = get_dataframe(main_quote_data, '1s')
    df_sub = get_dataframe(sub_quote_data, '1s')
    spread_array_bid = df_main.Bid_Price1 - df_sub.Bid_Price1
    spread_array_ask = df_main.Ask_Price1 - df_sub.Ask_Price1
    spread_array_bid, spread_array_ask = conjunction_spread_array(spread_array_bid, spread_array_ask)
    bid_spread_arr = rearrangement_data_series(spread_array_bid)
    ask_spread_arr = rearrangement_data_series(spread_array_ask)
    moving_bid_spread_arr = moving_average(bid_spread_arr, 120)
    moving_ask_spread_arr = moving_average(ask_spread_arr, 120)
    moving_bid_spread_arr2 = moving_average(bid_spread_arr, 30)
    moving_bid_spread_arr2 = moving_bid_spread_arr2[-len(moving_bid_spread_arr):]
    moving_ask_spread_arr2 = moving_average(ask_spread_arr, 30)
    moving_ask_spread_arr2 = moving_ask_spread_arr2[-len(moving_ask_spread_arr):]
    moving_bid_std = moving_std(bid_spread_arr, 120)
    upper_arr = moving_ask_spread_arr + 2 * moving_bid_std
    lower_arr = moving_bid_spread_arr - 2 * moving_bid_std
    upper_arr2 = moving_ask_spread_arr2 + 2 * moving_bid_std
    lower_arr2 = moving_bid_spread_arr2 - 2 * moving_bid_std
    total_num = len(upper_arr)
    fig = plt.figure()
    fig.set_size_inches(23.2, 14.0)
    ax = fig.add_subplot(1, 1, 1)
    png_title = 'Contract Spread array of ' + main_instrument_id + ' & ' + sub_instrument_id
    ax.set_title(png_title)
    ax.plot(bid_spread_arr[-total_num:], 'b')
    ax.plot(ask_spread_arr[-total_num:], 'r')
    ax.plot(upper_arr)
    ax.plot(lower_arr)
    ax.plot(upper_arr2)
    ax.plot(lower_arr2)
    plt.legend(["ask_price", "bid_price"], loc='best')
    out_file_name = out_file_folder + str(trading_day) + 'EMA.png'
    plt.savefig(out_file_name)


def main():
    main_instrument_id = 'SP JM1801&JM1805'
    sub_instrument_id = 'SP J1801&J1805'
    trading_day = '20171030'
    get_spread_array_map(main_instrument_id, sub_instrument_id, trading_day)


if __name__ == '__main__':
    main()