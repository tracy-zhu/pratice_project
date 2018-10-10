#  -*- coding: utf-8 -*-

# 检查前一天根据涨跌停板计算的行情文件和第二天交易所的行情文件的差别

# 导入系统库
import sys, time, os
import logging
import shutil

# 导入用户库
sys.path.append("..")
from python_base.plot_method import *
import xml.dom.minidom
from datetime import datetime, timedelta


# 全局变量
now = datetime.now()
trading_day = now.strftime('%Y%m%d')
second_day = get_pre_trading_day(trading_day)
xml_file = 'Q:\\startegy_xml_bak\\' + second_day + '\\auction_arbi_config.xml'
g_dom = xml.dom.minidom.parse(xml_file)
limit_close_time = '14:58:59'
open_time = '20:59:00'
###################################

def get_instrument_info_dict(instrument_id_array):
    instrument_info_dict = dict()
    info_array = [0, 0]
    tick_quote_name = 'Z:\\' + trading_day + '\\'
    #tick_quote_name = 'D:\\Quote_Data\\Tick_Quote\\' + trading_day + '\\'
    for instrument_id in instrument_id_array:
        #print instrument_id
        quote_file_name = tick_quote_name + instrument_id + ".csv"
        instrument_data_slice = pd.read_csv(quote_file_name, header=0, index_col=False, names=G_TICK_COLUMNS)
        if len(instrument_data_slice) > 5:
            upper_limit_price = instrument_data_slice.Upper_Limit_Price.values[-5]
            lower_limit_price = instrument_data_slice.Lower_Limit_Price.values[-5]
            info_array = [upper_limit_price, lower_limit_price]

        if instrument_info_dict.has_key(instrument_id):
            pass
        else:
            instrument_info_dict[instrument_id] = info_array

    return instrument_info_dict

root = g_dom.documentElement
itemlist = root.getElementsByTagName('auction_arbi_variety')

instrument_id_array = []
for item in itemlist:
    first_instrument = item.getElementsByTagName('main_instrument')[0].firstChild.data
    second_instrument = item.getElementsByTagName('sub_instrument')[0].firstChild.data
    instrument_id_array.append(first_instrument)
    instrument_id_array.append(second_instrument)

instrument_info_dict = get_instrument_info_dict(instrument_id_array)

for item in itemlist:
    limit_delta = 3
    limit_range_tick = 7
    first_instrument = item.getElementsByTagName('main_instrument')[0].firstChild.data
    second_instrument = item.getElementsByTagName('sub_instrument')[0].firstChild.data
    main_upper_limit_price = item.getElementsByTagName('main_upper_limit_price')[0].firstChild.data
    sub_upper_limit_price = item.getElementsByTagName('sub_upper_limit_price')[0].firstChild.data
    main_lower_limit_price = item.getElementsByTagName('main_lower_limit_price')[0].firstChild.data
    sub_lower_limit_price = item.getElementsByTagName('sub_lower_limit_price')[0].firstChild.data

    variety_id = get_variety_id(first_instrument)
    [act_main_upper_limit_price, act_main_lower_limit_price] = instrument_info_dict[first_instrument]
    [act_sub_upper_limit_price, act_sub_lower_limit_price] = instrument_info_dict[second_instrument]
    tick, _, _, = get_variety_information(variety_id)
    main_upper_delta = float(act_main_upper_limit_price - float(main_upper_limit_price)) / tick - limit_range_tick
    main_lower_delta = float(act_main_lower_limit_price - float(main_lower_limit_price)) / tick + limit_range_tick
    sub_upper_delta = float(act_sub_upper_limit_price - float(sub_upper_limit_price)) / tick - limit_range_tick
    sub_lower_delta = float(act_sub_lower_limit_price - float(sub_lower_limit_price)) / tick + limit_range_tick

    if abs(main_upper_delta) < limit_delta and abs(main_lower_delta) < limit_delta and abs(sub_upper_delta) < limit_delta and abs(sub_lower_delta) < limit_delta:
        limit_price_check = "correct"
    else:
        limit_price_check = "wrong!please check it again!"

    str_line1 = first_instrument + ',' + limit_price_check + '\n'

    str_line2 = second_instrument + ',' + limit_price_check + "\n"

    if len(limit_price_check) > 10:
        print str_line1, str_line2




