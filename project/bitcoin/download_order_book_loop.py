# -*- coding: utf-8 -*-

import datetime
import time
import requests
import sys
import pandas as pd

# 导入用户库：
sys.path.append("..")
from bitcoin.signal_generation import *


def download_order_book(f):
    now = datetime.datetime.now()
    depth_fly = {'product_code': 'FX_BTC_JPY'}
    url_fly = "https://api.bitflyer.jp"
    path_fly="/v1/board"
    g1_fly = requests.get(url_fly + path_fly , params=depth_fly)
    depth_data_fly=g1_fly.json()
    executions = None
    write_down_order_book(now, depth_data_fly, f, executions)


def write_down_order_book(now, depth_data_fly, f, executions):
    bid_price_list = depth_data_fly['bids']
    ask_price_list = depth_data_fly['asks']
    mid_price = depth_data_fly['mid_price']
    vwap_price = get_vwap_price(executions)
    lee_ready_vol, lee_ready_ratio = lee_ready_factor(executions)
    now_str = now.strftime('%Y-%m-%d %H:%M:%S.%f')
    bid_str_line = now_str
    ask_str_line = now_str
    for bid_price_dict in bid_price_list[:10]:
        bid_str_line = bid_str_line + ',' + str(bid_price_dict['price']) + ',' + str(bid_price_dict['size'])
    bid_str_line = bid_str_line + '\n'

    for ask_price_dict in ask_price_list[:10]:
        ask_str_line = ask_str_line + ',' + str(ask_price_dict['price']) + ',' + str(ask_price_dict['size'])
    ask_str_line = ask_str_line + "\n"

    mid_price_str_line = now_str + ',' + str(mid_price) + ',' + str(vwap_price) + "," + str(lee_ready_vol)\
                         + ',' + str(lee_ready_ratio) +  "\n"

    f.write(mid_price_str_line.encode())
    f.write(bid_str_line.encode())
    f.write(ask_str_line.encode())


if __name__ == '__main__':
    order_book_data = "..\\bitcoin\\order_book_data.txt"
    f = open(order_book_data, 'wb')
    while True:
        download_order_book(f)
        time.sleep(1)
        print ('run the time task at {0}'.format(datetime.datetime.now()))

