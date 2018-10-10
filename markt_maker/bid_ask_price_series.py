# -*- coding: utf-8 -*-
"""

# 本脚本根据上期所行情，将最新价和上下买卖价挂单根据bid_ask_spread画出来
# 上期所筛选深度行情数据， 郑商所得出前开盘价

Tue 2017/08/21

@author: Tracy Zhu
"""
# 导入系统库
import sys
import logging

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *

now = datetime.now()
#trading_day = now.strftime('%Y%m%d')
trading_day = '20170828'
instrument_id = 'SPD MA801&MA805'
quote_data = read_data(instrument_id, trading_day)
bid_ask_spread = 1
out_file_folder = '..\\picture\\'


def get_bid_ask_price_series(instrument_id, trading_day, bid_ask_spread, begin_time, end_time):
    quote_data = read_data(instrument_id, trading_day)
    quote_data = quote_data[quote_data.Update_Time > begin_time]
    quote_data = quote_data[quote_data.Update_Time < end_time]
    initial_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    price_arr = initial_price_series.values
    #price_arr = quote_data.Last_Price.values
    T = len(price_arr)
    #T = 1500
    a = np.zeros(T)
    a[0] = price_arr[0]

    for t in range(T-1):
        if price_arr[t] < a[t]:
            a[t+1] = price_arr[t]
        elif price_arr[t] > a[t] + bid_ask_spread:
            a[t+1] = price_arr[t] - bid_ask_spread
        else:
            a[t+1] = a[t]

    bid_spread_arr = a
    ask_spread_arr = a + bid_ask_spread
    new_price_arr = price_arr[:T]
    return new_price_arr, bid_spread_arr, ask_spread_arr


def plot_spread_series(price_arr, bid_spread_arr, ask_spread_arr):
    fig, ax = plt.subplots()
    fig.set_size_inches(23.2, 14.0)
    out_title = 'bid_ask_spread_array'
    ax.set_title(out_title)
    ax.plot(price_arr, color='r', label='last_spread')
    ax.plot(bid_spread_arr, color='b', label='bid_price_arr')
    ax.plot(ask_spread_arr, color='y', label='ask_price_arr')
    ax.legend(loc='upper left')
    path_name = out_file_folder + trading_day
    isExists = os.path.exists(path_name)
    if not isExists:
        os.makedirs(path_name)
    out_file_name = path_name + '\\' + instrument_id + ' in ' + str(
        trading_day) + '.png'
    plt.savefig(out_file_name)


if __name__ == '__main__':
    begin_time = '09:18:00'
    end_time = '09:27:00'
    price_arr, bid_spread_arr, ask_spread_arr = get_bid_ask_price_series(instrument_id, trading_day, bid_ask_spread, begin_time, end_time)
    plot_spread_series(price_arr, bid_spread_arr, ask_spread_arr)
