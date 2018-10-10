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
profit=1000
size=0.001
position_limit=0.1
threshold = 270
# 取得交易所状态
status=api.getboardstate()

def getboard(board):
    board['data']=api.board(product_code="FX_BTC_JPY")
def getexcutions(excutions):
    excutions['data']=api.getexecutions(product_code="FX_BTC_JPY",count=10)
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

middle_price_list = deque(maxlen=5)
while True:
    if status['health']=='NORMAL' and status['state']=='RUNNING':
        board = {}
        excutions = {}
        position = {}
        threads = []
        t1 = threading.Thread(target=getboard,args=(board,))
        t2 = threading.Thread(target=getexcutions,args=(excutions,))
        t3 = threading.Thread(target=get_position,args=(position,))
        threads.extend([t1,t2,t3])
        for t in threads:
            t.setDaemon(True)
            t.start()
        t.join()
        ask=board['data']['asks'][0]['price']
        bid=board['data']['bids'][0]['price']
        position_limit=position['data']
        middle_price_list.append(board['data']['mid_price'])
        signal = signal_generation(board, middle_price_list)
        if signal > threshold and position<position_limit:
            buy=parent_buy(size=size,price=bid+1,profit=profit)
            print('buy')
        elif signal < -threshold and position>-position_limit:
            sell=parent_sell(size=size,price=ask-1,profit=profit)
            print('sell')
        else:
            print('do nothing')
    else:
        print('status error')
    time.sleep(0.1)
    
