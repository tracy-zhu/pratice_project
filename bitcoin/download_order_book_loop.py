# -*- coding: utf-8 -*-

import datetime
import time
import requests
import pandas as pd

def download_order_book(f):
    now = datetime.datetime.now()
    depth_fly = {'product_code': 'FX_BTC_JPY'}
    url_fly = "https://api.bitflyer.jp"
    path_fly="/v1/board"
    g1_fly = requests.get(url_fly + path_fly , params=depth_fly)
    depth_data_fly=g1_fly.json()
    write_down_order_book(now, depth_data_fly, f)


def write_down_order_book(now, depth_data_fly, f):
    bid_price_list = depth_data_fly['bids']
    ask_price_list = depth_data_fly['asks']
    mid_price = depth_data_fly['mid_price']
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    bid_str_line = now_str
    ask_str_line = now_str
    for bid_price_dict in bid_price_list:
        bid_str_line = bid_str_line + ',' + str(bid_price_dict['price']) + ',' + str(bid_price_dict['size'])
    bid_str_line = bid_str_line + '\n'

    for ask_price_dict in ask_price_list:
        ask_str_line = ask_str_line + ',' + str(ask_price_dict['price']) + ',' + str(ask_price_dict['size'])
    ask_str_line = ask_str_line + "\n"

    mid_price_str_line = now_str + ',' + str(mid_price) + "\n"

    f.write(mid_price_str_line)
    f.write(bid_str_line)
    f.write(ask_str_line)


if __name__ == '__main__':
    order_book_data = "..\\bitcoin\\order_book_data.txt"
    f = open(order_book_data, 'wb')
    while True:
        download_order_book(f)
        time.sleep(1)
        print 'run the time task at {0}'.format(datetime.datetime.now())

