# -*- coding: utf-8 -*-
import pybitflyer
import threading
from collections import deque
import sys
import time

# 导入用户库：
sys.path.append("..")
from bitcoin.signal_generation import *


api = pybitflyer.API(api_key="362q3qHwsQaAaY3cgdvaJM", api_secret="Wpd9GQ3W4jCOc18IxFjFngxNWr2zxxoz8z8m9LcvKx8=")
profit=200
size=0.001
position_max=0.01
threshold = 70
reserved_profit = 20


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
                            ,{"product_code":"FX_BTC_JPY","condition_type":"LIMIT","side":"SELL","price":price+profit,"size":size}])
    return parentorder_id


def parent_sell(size,price,profit):
    parentorder_id=api.sendparentorder(order_method="IFD",minute_to_expire='1', time_in_force="GTC",
                            parameters=[{"product_code":"FX_BTC_JPY","condition_type":"LIMIT","side":"SELL","price":price,"size":size}
                            ,{"product_code":"FX_BTC_JPY","condition_type":"LIMIT","side":"BUY","price":price-profit,"size":size}])
    return parentorder_id


def order():
    while True:
        try:
            status=api.getboardstate()
            if (status['health']=='NORMAL' or status['health']=='BUSY') and (status['state']=='RUNNING'):
        #                time1=time.clock()
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
                    executions_data = executions['data']
                    vwap = get_vwap_price(executions_data)
                    middle_price_list.append(board['data']['mid_price'])
                    if vwap != 0:
                        vwap_list.append(vwap)
                    else:
                        vwap_list.append(vwap_list[-1])
        #                time2=time.clock()
        #                time_board.append(time2-time1)
        #                time3=time.clock()
                    if len(middle_price_list) == 5 and len(vwap_list) == 5:
                        signal = signal_generation(board, middle_price_list, vwap_list, executions_data)
                        bid_ask_spread = ask - bid
                        over_price = signal / 4
                        if (signal > threshold) and (position_now<position_max):
                            parent_buy(size=size,price=bid + over_price, profit=signal - reserved_profit)
                            print('buy')
                        elif (signal < -threshold) and (position_now>-position_max):
                            parent_sell(size=size,price=ask - over_price ,profit=signal - reserved_profit)
                            print('sell')
#                        else:
#                            print(signal)
                    else:
                        print(len(middle_price_list))
        #                time4=time.clock()
        #                time_order.append(time4-time3)
            else:
                print(status['health'])
        except:
            print('net error')
        time.sleep(0.1)
        
        
def cancel():
    while True:
        try:
            api.cancelallchildorders(product_code="FX_BTC_JPY")
            print('cancel')
        except:
            print('no order')
        time.sleep(4)

middle_price_list = deque(maxlen=5)
vwap_list = deque(maxlen=5)
#time_board=[]
#time_order=[]
#time_all=[]
try:
    threadss=[]
    tt1 = threading.Thread(target=order)
    tt2 = threading.Thread(target=cancel)
    threadss.append(tt1)
    threadss.append(tt2)
    for t in threadss:
        t.start()
except:
    print('net error')


