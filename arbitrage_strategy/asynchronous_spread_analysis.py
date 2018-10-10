# -*- coding: utf-8 -*-
"""

# 本脚本用于研究有色金属的异步价差模型，为股指期货的套利研究做准备

Fri 2017/12/1

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *

first_instrument_id = "AL1802"
second_instrument_id = "AL1803"
trading_day = "20171218"

first_quote_data = read_data(first_instrument_id, trading_day)
second_quote_data = read_data(second_instrument_id, trading_day)


def transfer_quote_data_with_time_index(quote_data):
    """
    将quote_data的index转化为秒加上毫秒的组合
    :param quote_data:
    :return:
    """
    Update_Millisec_str = []
    stamp_index = []
    data = quote_data.dropna(subset=['Update_Time'], how='any')
    for values in data.Update_Millisec:
        str_values = str(values).zfill(3)
        Update_Millisec_str.append(str_values)
    time_index = data.Update_Time + "." + Update_Millisec_str
    for temp_time in time_index:
        stamp = datetime.strptime(temp_time, '%H:%M:%S.%f')
        stamp_index.append(stamp)
    DF_data = DataFrame(data.values, index=stamp_index, columns=G_TICK_COLUMNS)
    return DF_data


def get_different_spread(first_price, second_price):
    """
    函数用于生成不同的价差序列，sell_spread_ask_bid, sell_spread_ask_ask, sell_spread_bid_bid
    buy_spread_bid_ask
    :param first_price: bid_price1 or ask_price_1
    :param second_price: bid_price1 or ask_price_1
    :return:different price spread series
    """
    spread_arr = first_price - second_price
    spread_arr_night = spread_arr[spread_arr.index >= datetime(1900,1,1,20,59,0)]
    spread_arr_day = spread_arr[spread_arr.index < datetime(1900,1,1,20,59,0)]
    new_spread_arr = pd.concat([spread_arr_night, spread_arr_day])
    new_spread_arr = new_spread_arr.dropna()
    return new_spread_arr


first_quote_data_with_index = transfer_quote_data_with_time_index(first_quote_data)
second_quote_data_with_index = transfer_quote_data_with_time_index(second_quote_data)

sell_spread_ask_bid = get_different_spread(first_quote_data_with_index.Ask_Price1, second_quote_data_with_index.Bid_Price1)
spread_ask_ask = get_different_spread(first_quote_data_with_index.Ask_Price1, second_quote_data_with_index.Ask_Price1)
spread_bid_bid = get_different_spread(first_quote_data_with_index.Bid_Price1, second_quote_data_with_index.Bid_Price1)
buy_spread_bid_ask = get_different_spread(first_quote_data_with_index.Bid_Price1, second_quote_data_with_index.Ask_Price1)

fig, ax0 = plt.subplots()
fig.set_size_inches(23.2, 14.0)
ax0.plot(sell_spread_ask_bid.values, label="sell_spread_ask_bid")
#ax.plot(spread_ask_ask.values, label="sell_spread_ask_ask")
#ax.plot(spread_bid_bid.values, label="sell_spread_bid_bid")

fig, ax1 = plt.subplots()
fig.set_size_inches(23.2, 14.0)
ax1.plot(buy_spread_bid_ask.values, label="buy_spread_bid_ask")

