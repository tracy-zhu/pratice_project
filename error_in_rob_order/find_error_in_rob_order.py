# -*- coding: utf-8 -*-
"""
Created on Mon JAN 16 09:53:00 2017

该文件用于查找在抢单中出现错误的情况

@author: Tracy Zhu
"""

# 导入系统库
import sys
import logging

# 导入用户库
sys.path.append("..")
from python_base.plot_method import *
import xml.dom.minidom
from datetime import datetime, timedelta

# 日志文件
log_file_name = "limit_price_analyse.log"

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s  %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    filename=log_file_name,
                    filemode='w')

# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# 全局变量
LIMIT_OPEN_VOLUME = 500
LIMIT_DEVIATION = 8
DURATION_TICK_NUM = 20
LIMIT_OPEN_INTEREST_CHANGE = -5000
LIMIT_OPEN_TICK_CHANGE = 25
VARIETY_ID_LIST = ['RM', 'SR', 'OI', 'M', 'P', 'Y', 'RB', 'RU', 'CU','AG', 'AU']

# ----------------------------------------------------------------------
def get_open_info(main_instrument_id, trading_day):
    quote_data = read_data(main_instrument_id, trading_day)
    variety_id = get_variety_id(main_instrument_id)
    tick, unit, exchange_id = get_variety_information(variety_id)
    morning_open_time = '09:00:00'
    open_index = quote_data.index[quote_data.Update_Time == morning_open_time]
    if len(open_index) > 0:
        open_index = open_index[0]
        rob_volume = quote_data.ix[open_index].Total_Match_Volume - quote_data.ix[open_index - 1].Total_Match_Volume
        rob_turnover = quote_data.ix[open_index].Turnover - quote_data.ix[open_index - 1].Turnover
        rob_open_price = quote_data.Last_Price[open_index]
        open_price_change = (rob_open_price - quote_data.Last_Price[open_index - 1]) / tick
        rob_average_price = rob_turnover / rob_volume / unit
        deviation_tick = abs(rob_open_price - rob_average_price) / tick

        next_bid_price = quote_data.Bid_Price1[open_index]
        next_ask_price = quote_data.Ask_Price1[open_index]

        tick_change = (quote_data.Last_Price[open_index + DURATION_TICK_NUM] - rob_open_price) / tick
        open_interest_change = quote_data.Open_Interest[open_index + DURATION_TICK_NUM] - quote_data.Open_Interest[open_index]
        next_info = [next_bid_price, next_ask_price, tick_change, open_interest_change]
        return deviation_tick, rob_volume, rob_open_price, open_price_change, rob_average_price, next_info
    else:
        return None, None, None, None, None, None

# ----------------------------------------------------------------------
result_file_name = "big_market_result.csv"
result_file = open(result_file_name, "w")
print>>result_file, "main_instrument_id, trading_day, deviation_tick, rob_volume, rob_open_price, open_tick_change, rob_average_price, bid_price, ask_price, tick_change, open_interest_change"

# ----------------------------------------------------------------------
trading_day_list = get_trading_day_list()
for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    if trading_day >= '20161001':
        instrument_file_list = get_instrument_file_list(trading_day)
        for variety_id, instrument_list in instrument_file_list.items():
            main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
            logging.debug('find error in %s for %s', trading_day, variety_id)
            if main_instrument_id != None and variety_id in VARIETY_ID_LIST:
                deviation_tick, rob_volume, rob_open_price, open_price_change, rob_average_price, next_info = get_open_info(main_instrument_id, trading_day)
                if deviation_tick != None:
                    next_bid_price = next_info[0]
                    next_ask_price = next_info[1]
                    tick_change = next_info[2]
                    open_interest_change = next_info[3]
                    # if deviation_tick > LIMIT_DEVIATION and rob_volume > LIMIT_OPEN_VOLUME:
                    if abs(open_price_change) > LIMIT_OPEN_TICK_CHANGE:
                        print>>result_file, main_instrument_id, ',', trading_day, ',', deviation_tick, ",", rob_volume, ",",\
                        rob_open_price, ",", open_price_change, ",", rob_average_price, ",", next_bid_price, ",", next_ask_price, ",", tick_change, \
                        ",", open_interest_change
                        result_file.flush()

result_file.close()

