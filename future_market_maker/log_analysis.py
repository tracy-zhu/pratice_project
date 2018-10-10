# -*- coding: utf-8 -*-
"""

# 对期货做市策略的日志进行分析；绘出MSP, 成交价等因素

Tue 2018/5/15

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *

instrument_id_list = ["RB1810", "RB1901", "J1809", "JM1809"]
order_key_1 = "order:instrument:"
order_key_2 = "|Order"
# log_file_folder = "D:\\build_noctp\\log\\"
log_file_folder = "C:\\Users\\Tracy Zhu\\Desktop\\build\\market_maker_strategy\\log\\"
out_file_folder = "..\\future_market_maker\\result\\"

log_file_name = "strategy.g2log.20180724-104445.log"

file_name = log_file_folder + log_file_name

f = open(file_name, 'r')
log_file_lines = f.readlines()
f.close()

trade_info_list = []
trade_info_list_li = []

for line in log_file_lines:
    if order_key_1 in line:
        trade_info_list.append(line)
    if order_key_2 in line and len(line) > 170:
        trade_info_list_li.append(line)

update_time_list = []
instrument_list = []
vwap_list = []
direction_list = []
offset_list = []
position_list = []
risk_list = []
order_bid_price_list = []
order_ask_price_list = []
msp_list = []
tv_list = []
market_bid_list = []
market_ask_list = []

for trade_info in trade_info_list:
    str_list = trade_info.split('|')
    update_time = str_list[0]
    update_time_list.append(update_time)
    trade_information = str_list[3]
    order_list = trade_information.split(',')
    instrument = order_list[0].split(":")[-1]
    instrument_list.append(instrument)
    price = float(order_list[1].split(":")[-1])
    vwap_list.append(price)
    direction = order_list[2].split(":")[-1]
    direction_list.append(direction)
    offset = order_list[3].split(":")[-1]
    offset_list.append(offset)
    position = int(order_list[4].split(":")[-1])
    position_list.append(position)
    risk = float(order_list[5].split(":")[-1])
    risk_list.append(risk)
    bid_price = float(order_list[6].split(":")[-1])
    order_bid_price_list.append(bid_price)
    ask_price = float(order_list[7].split(":")[-1])
    order_ask_price_list.append(ask_price)
    msp = float(order_list[8].split(":")[-1])
    msp_list.append(msp)
    tv = float(order_list[9].split(":")[-1])
    tv_list.append(tv)
    market_bid_price = float(order_list[10].split(":")[-1])
    market_bid_list.append(market_bid_price)
    market_ask_price = float(order_list[11].split(":")[-1])
    market_ask_list.append(market_ask_price)


update_time_li = []
bid_price_list_li = []
ask_price_list_li = []
instrument_li = []
raw_bid_list = []
raw_ask_list = []
market_bid_list_li = []
market_ask_list_li = []
for trade_info_li in trade_info_list_li:
    update_time_li.append(trade_info_li.split('|')[0])
    trade_info = trade_info_li.split('|')[3]
    info_list = trade_info.split(',')
    instrument_li.append(info_list[0].split('=')[-1])
    raw_bid_list.append(float(info_list[1].split('=')[-1]))
    raw_ask_list.append(float(info_list[2].split('=')[-1]))
    market_bid_list_li.append(float(info_list[4].split('=')[-1]))
    market_ask_list_li.append(float(info_list[5].split('=')[-1]))
    bid_price_list_li.append(float(info_list[6].split('=')[-1]))
    ask_price_list_li.append(float(info_list[7].split('=')[-1]))


trade_dict_li = {'instrument': instrument_li, 'raw_bid': raw_bid_list, 'raw_ask': raw_ask_list,
                 'market_bid': market_bid_list_li, 'market_ask': market_ask_list_li, 'order_bid_price': bid_price_list_li,
                 'order_ask_price': ask_price_list_li, 'update_time': update_time_li}
trade_df_li = DataFrame(trade_dict_li)
trade_df_li.index = trade_df_li.update_time
JM_df = trade_df_li[trade_df_li.instrument == 'jm1809']
JM_df.to_csv("test2.csv")

trade_dict = {"instrument": instrument_list, "vwap": vwap_list, "direction": direction_list,
              "offset": offset_list, "position": position_list, "risk": risk_list, "order_bid_price": order_bid_price_list,
              "order_ask_price": order_ask_price_list, "msp": msp_list, "tv": tv_list, "update_time": update_time_list,
              "market_bid_price": market_bid_list, "market_ask_price": market_ask_list}
trade_df = DataFrame(trade_dict)
trade_df.index = trade_df.update_time

RB1901_df = trade_df[trade_df.instrument == 'jm1809']
instrument_trade_df = RB1901_df[RB1901_df.direction == " sell"]
delta = instrument_trade_df.tv - instrument_trade_df.vwap.shift(-10)
instrument_trade_df.to_csv("test.csv")
instrument_trade_df.position.plot()


def plot_tv_and_market_bid_ask(instrument_trade_df):
    """
    根据前面整合出的单合约的trade_df, 画出bid, ask价格，和tv价格
    :param trade_df:
    :return:
    """
    begin_N = 0
    end_N = begin_N + len(instrument_trade_df)
    bid_price_series = instrument_trade_df.order_bid_price
    ask_price_series = instrument_trade_df.order_ask_price
    market_bid_price_series = instrument_trade_df.market_bid_price
    market_ask_price_series = instrument_trade_df.market_ask_price
    mid_price_series = (market_bid_price_series + market_ask_price_series) / 2
    tv_series = instrument_trade_df.tv


    fig, ax = plt.subplots(figsize=(23.2, 14.0))
    # ax.plot(bid_price_series.values[begin_N:end_N], color='r', label='order bid price')
    # ax.plot(ask_price_series.values[begin_N:end_N], color='b', label='order ask price')
    ax.plot(tv_series, color='y', label='tv series')
    ax.plot(mid_price_series, color='pink', label='middle price')
    ax1 = ax.twinx()
    ax1.plot(instrument_trade_df.position, color='b', label='position')
    ax.legend(loc='upper left')
    ax1.legend(loc='upper right')



    spread = tv_series - mid_price_series
    fig, ax = plt.subplots(figsize=(23.2, 14.0))
    # ax.plot(bid_price_series.values[begin_N:end_N], color='r', label='order bid price')
    # ax.plot(ask_price_series.values[begin_N:end_N], color='b', label='order ask price')
    ax.plot(tv_series.values[begin_N:end_N], color='y', label='tv series')
    ax.plot(mid_price_series.values[begin_N:end_N], color='pink', label='middle price')
    ax.legend(loc='best')
    title = "bid ask true price"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)






