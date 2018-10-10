# -*- coding: utf-8 -*-
import pybitflyer
import threading
from collections import deque
import sys
import time

# 导入用户库：
sys.path.append("..")
from bitcoin.download_order_book_loop import *

api = pybitflyer.API(api_key="362q3qHwsQaAaY3cgdvaJM", api_secret="Wpd9GQ3W4jCOc18IxFjFngxNWr2zxxoz8z8m9LcvKx8=")
profit=500
size=0.002
position_max=0.01
threshold = 250
limit_each_data_num = 10000

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


def getboard(board):
    board['data']=api.board(product_code="FX_BTC_JPY")


def getexcutions(excutions):
    excutions['data']=api.executions(product_code="FX_BTC_JPY",count=20)


def get_position(position):
    get_position=api.getpositions(product_code="FX_BTC_JPY")
    position['data']=0
    if len(get_position) > 0:
        for position_dict in get_position:
            if position_dict['side']=="SELL":
                position['data'] += -position_dict['size']
            elif position_dict['side']=="BUY":
                position['data'] += position_dict['size']


def parent_buy(size,price,profit):
    parentorder_id=api.sendparentorder(order_method="IFD",minute_to_expire='1', time_in_force="GTC",
                            parameters=[{"product_code":"FX_BTC_JPY","condition_type":"LIMIT","side":"BUY","price":price,"size":size}
                            ,{"product_code":"FX_BTC_JPY","condition_type":"LIMIT","side":"SELL","price":price+profit,"size":size/2}])
    return parentorder_id


def parent_sell(size,price,profit):
    parentorder_id=api.sendparentorder(order_method="IFD",minute_to_expire='1', time_in_force="GTC",
                            parameters=[{"product_code":"FX_BTC_JPY","condition_type":"LIMIT","side":"SELL","price":price,"size":size}
                            ,{"product_code":"FX_BTC_JPY","condition_type":"LIMIT","side":"BUY","price":price-profit,"size":size/2}])
    return parentorder_id


middle_price_list = deque(maxlen=5)
data_file_num = 0
data_num = 0
order_book_data = "..\\bitcoin\\order_book_data_" + str(data_file_num) +  ".txt"
f = open(order_book_data, 'wb')
while True:
    if data_num <= limit_each_data_num:
        # 取得交易所状态
        status=api.getboardstate()
        if (status['health']=='NORMAL' or status['health']=='BUSY') and (status['state']=='RUNNING'):
            board = {}
            executions = {}
            position = {}
            threads = []
            t1 = threading.Thread(target=getboard,args=(board,))
            t2 = threading.Thread(target=getexcutions,args=(executions,))
            t3 = threading.Thread(target=get_position,args=(position,))
            threads.append(t1)
            threads.append(t2)
            threads.append(t3)
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            ask=board['data']['asks'][0]['price']
            bid=board['data']['bids'][0]['price']
            position_now=position['data']
            middle_price_list.append(board['data']['mid_price'])
            now = datetime.datetime.now()
            depth_data_fly = board['data']
            executions_data = executions['data']
            write_down_order_book(now, depth_data_fly, f, executions_data)
            data_num += 1
            print ('run the time task at {0}'.format(datetime.datetime.now()))
        time.sleep(0.1)
    else:
        data_num = 0
        f.close()
        data_file_num += 1
        order_book_data = "..\\bitcoin\\order_book_data_" + str(data_file_num) +  ".txt"
        f = open(order_book_data, 'wb')
        status=api.getboardstate()
        if (status['health']=='NORMAL' or status['health']=='BUSY') and (status['state']=='RUNNING'):
            board = {}
            executions = {}
            position = {}
            threads = []
            t1 = threading.Thread(target=getboard,args=(board,))
            t2 = threading.Thread(target=getexcutions,args=(executions,))
            t3 = threading.Thread(target=get_position,args=(position,))
            threads.append(t1)
            threads.append(t2)
            threads.append(t3)
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            ask=board['data']['asks'][0]['price']
            bid=board['data']['bids'][0]['price']
            position_now=position['data']
            middle_price_list.append(board['data']['mid_price'])
            now = datetime.datetime.now()
            depth_data_fly = board['data']
            executions_data = executions['data']
            write_down_order_book(now, depth_data_fly, f, executions_data)
            data_num += 1
            print ('run the time task at {0}'.format(datetime.datetime.now()))
        time.sleep(0.1)


