
# -*- coding: utf-8 -*-
"""

# 用于比特币交易信号的生成；

Tue 2018/03/01

@author: Tracy Zhu
"""


def get_momentum_factor(middle_price_list):
    price_momentum = middle_price_list[-1] - middle_price_list[0]
    return price_momentum


def get_order_imbalance_ratio(board, depth_level):
    total_bid_volume = 0
    total_ask_volume = 0
    ask_list = board['data']['asks']
    bid_list = board['data']['bids']
    for i in range(depth_level):
        ask_volume = ask_list[i]['size']
        bid_volume = bid_list[i]['size']
        total_ask_volume += ask_volume
        total_bid_volume += bid_volume
    order_imbalance_ratio = float(total_bid_volume - total_ask_volume) / float(total_bid_volume + total_ask_volume)
    return order_imbalance_ratio


def signal_generation(board, middle_price_list):
    momentum_factor = get_momentum_factor(middle_price_list)
    signal = momentum_factor * 0.5
    return signal

