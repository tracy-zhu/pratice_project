# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 09:53:00 2017

该文件用于找集合竞价撮合出错单，10个tick后价格会发生较大偏离的情况

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
TRADE_PHASE_FILE = "F:\\python_project_contract_spread\\trade_phase\\20160503-99999999_trade_phase.xml"
LIMIT_OPEN_VOLUME = 500
LIMIT_DEVIATION = 8
LIMIT_PERCENT_CHANGE = 0.003

# ----------------------------------------------------------------------
def get_open_info(main_instrument_id, trading_day):
    quote_data = read_data(main_instrument_id, trading_day)
    variety_id = get_variety_id(main_instrument_id)
    open_time = get_opentime(variety_id, TRADE_PHASE_FILE)
    if open_time != None:
        if open_time[0:2] == '20':
            call_auction_open_time = '20:59:00'
        else:
            call_auction_open_time = '8:59:00'
        open_index = quote_data.index[quote_data.Update_Time == call_auction_open_time]
        if len(open_index) > 0:
            open_index = open_index[0]
            end_index = open_index + 10
            open_price = quote_data.Last_Price[open_index]
            open_end_price = quote_data.Last_Price[end_index]
            tick, unit, exchange_id = get_variety_information(variety_id)
            percent_change = abs(float(open_end_price - open_price) / float(open_price))
            tick_change = (open_end_price - open_price) / tick
            return percent_change, tick_change
        else:
            return None, None
    else:
        return None, None

# ----------------------------------------------------------------------
result_file_name = "error_in_call_auction.txt"
result_file = open(result_file_name, "w")
print>>result_file, "main_instrument_id, trading_day, percent_change, tick_change"

# ----------------------------------------------------------------------
trading_day_list = get_trading_day_list()
for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    if trading_day >= '20170201':
        instrument_file_list = get_instrument_file_list(trading_day)
        for variety_id, instrument_list in instrument_file_list.items():
            logging.debug('find error in %s for %s', trading_day, variety_id)
            main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
            if main_instrument_id != None:
                percent_change, tick_change = get_open_info(main_instrument_id, trading_day)
                if percent_change != None and percent_change >= LIMIT_PERCENT_CHANGE:
                    print>>result_file, main_instrument_id, ',', trading_day, ',', percent_change, ',', tick_change
                    result_file.flush()

result_file.close()

