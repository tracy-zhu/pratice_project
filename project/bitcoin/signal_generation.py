
# -*- coding: utf-8 -*-
"""

# 用于比特币交易信号的生成；

Tue 2018/03/01

@author: Tracy Zhu
"""


def get_momentum_factor(middle_price_list):
    price_momentum = middle_price_list[-1] - middle_price_list[0]
    return price_momentum


def get_vwap_momentum_factor(vwap_list):
    vwap_momentum = vwap_list[-1] - vwap_list[0]
    return vwap_momentum


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


def get_order_imbalance(board):
    ask_list = board['data']['asks']
    bid_list = board['data']['bids']
    bid_product = bid_list[0]['size'] * bid_list[0]['price']
    ask_product = ask_list[0]['size'] * ask_list[0]['price']
    order_imbalance = float(bid_product - ask_product) / float(bid_product + ask_product)
    return order_imbalance


def lee_ready_factor(executions):
    """
    根据成交数据计算在主动买单上和主动卖单的成交额
    :param executions:
    :return:
    """
    total_buy_vol = 0
    total_sell_vol = 0
    lee_ready_ratio = 0
    for each_execution in executions:
        side = each_execution['side']
        size = each_execution['size']
        if side == "BUY":
            total_buy_vol += size
        elif side == "SELL":
            total_sell_vol += size
    lee_ready_vol = total_buy_vol - total_sell_vol
    if (total_buy_vol + total_sell_vol) > 0:
        lee_ready_ratio = float(lee_ready_vol) / float(total_buy_vol + total_sell_vol)
    return lee_ready_vol, lee_ready_ratio


def get_vwap_price(executions):
    """
    计算每个executions的成交均价
    :param executions:
    :return:
    """
    turnover = 0
    total_match_volume = 0
    vwap = 0
    for each_execution in executions:
        size = each_execution['size']
        price = each_execution['price']
        turnover += size * price
        total_match_volume += size
    if total_match_volume > 0:
        vwap = turnover / total_match_volume
    return vwap


def ticker_process(ticker):
    bid_price1 = ticker['best_bid']
    bid_volume1 = ticker['best_bid_size']
    ask_price1 = ticker['best_ask']
    ask_volume1 = ticker['best_ask_size']
    update_time = ticker['timestamp']
    last_price = ticker['ltp']
    str_line = update_time + ',' + str(last_price) + ',' + str(bid_price1) + ',' + str(bid_volume1) + ',' + \
               str(ask_price1) + ',' + str(ask_volume1)
    return str_line


def signal_generation(board, middle_price_list, vwap_list, executions):
    momentum_factor = get_momentum_factor(middle_price_list)
    order_imbalance = get_order_imbalance(board)
    order_imbalance_ratio = get_order_imbalance_ratio(board, 1)
    lee_ready_vol, lee_ready_ratio = lee_ready_factor(executions)
    vwap_momentum = get_vwap_momentum_factor(vwap_list)
    # signal = momentum_factor * 70.848 + 11 * lee_ready_ratio + 89080 * order_imbalance - 89080 * order_imbalance_ratio + 0.0283 * vwap_momentum
    signal = momentum_factor * 0.391 + lee_ready_ratio * 15.91 - vwap_momentum * 0.0001
    return signal

