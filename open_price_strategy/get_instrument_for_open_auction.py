# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 本脚本用于找出当天持仓量大于2000，但是没有配置到open_auction的配置文件中的合约

@author: Tracy Zhu
"""

# 导入系统库
import sys, time, os
import logging
import shutil

# 导入用户库
sys.path.append("..")
from python_base.plot_method import *
import xml.dom.minidom
from datetime import datetime, timedelta

### 全局变量
LIMIT_OPEN_INTEREST = 2000
# 全局变量
now = datetime.now()
trading_day = now.strftime('%Y%m%d')
# trading_day = '20170427'
xml_file = 'D:\\strategy\\open_auction_smart\\startegy_xml_bak\\' + trading_day + '\\auction_arbi_config.xml'
g_dom = xml.dom.minidom.parse(xml_file)
trade_phase_file_name = "D:\\open_price_strategy\\Strategy_Service\\auction_arbi\\trade_phase.xml"
g_trade_dom = xml.dom.minidom.parse(trade_phase_file_name)
instrument_file_list = get_instrument_file_list(trading_day)

def get_attribution(variety_id):
    global g_trade_dom
    root = g_trade_dom.documentElement
    itemlist = root.getElementsByTagName('VarietyPhase')
    for item in itemlist:
        if variety_id == item.getAttribute("varietyid").encode("gbk"):
            tick = float(item.getAttribute("tick").encode("gbk"))
            exchtype = float(item.getAttribute("exchtype").encode("gbk"))
            exchange_id = ''
            if exchtype == 3:
                exchange_id = "CZCE"
            elif exchtype == 2:
                exchange_id = "SHFE"
            else:
                exchange_id = 'else'
            return tick, exchange_id

# 得到持仓量大于2000的合约
first_instrument_id_array = []
for variety_id, instrument_list in instrument_file_list.items():
    _, exchange_id = get_attribution(variety_id)
    if exchange_id != 'else':
        for one_file_name in instrument_list:
            quote_file = open(one_file_name, "r")
            quote_list = quote_file.readlines()
            quote_file.close()
            instrument_id = one_file_name.split("\\")[-1].split(".")[0]
            close_quote = CBest_Market_Data_Field()
            if len(quote_list) > 2000:
                if len(quote_list[-1]) > 2:
                    close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-1])
                else:
                    close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-2])
            if close_quote.Open_Interest > LIMIT_OPEN_INTEREST:
                first_instrument_id_array.append(instrument_id)


# 得到配置合约的列表
root = g_dom.documentElement
itemlist = root.getElementsByTagName('auction_arbi_variety')

instrument_id_array = []
for item in itemlist:
    first_instrument = item.getElementsByTagName('main_instrument')[0].firstChild.data
    second_instrument = item.getElementsByTagName('sub_instrument')[0].firstChild.data
    instrument_id_array.append(first_instrument)
    if second_instrument not in instrument_id_array:
        instrument_id_array.append(second_instrument)

# 将持仓量大于2000却没有配置的合约输出到一个文件中去
instrument_compare_file_folder = 'D:\\strategy\\open_auction_smart\\instrument_compare\\' + trading_day
isExists = os.path.exists(instrument_compare_file_folder)
if not isExists:
    os.makedirs(instrument_compare_file_folder)
instrument_compare_file_file = instrument_compare_file_folder + '\\instrument_compare_file.csv'
f = open(instrument_compare_file_file, 'wb')

for raw_instrument_id in first_instrument_id_array:
    if raw_instrument_id not in instrument_id_array:
        print >> f, raw_instrument_id

f.close()
