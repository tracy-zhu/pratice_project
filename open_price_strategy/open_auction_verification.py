#  -*- coding: utf-8 -*-

# 该脚本用于每天晚上的行情能够触发但是没有触发，
# 输出到一个问价夹里面

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
limit_price_range_tick = 8
now = datetime.now()
trading_day = now.strftime('%Y%m%d')
if datetime.now().weekday() == 0:
    yesterday = datetime.now() - timedelta(days=3)
    pre_trading_day = yesterday.strftime('%Y%m%d')
else:
    yesterday = datetime.now() - timedelta(days=1)
    pre_trading_day = yesterday.strftime('%Y%m%d')

# trading_day = '20170307'
# pre_trading_day = '20170306'

xml_file = 'Q:\\startegy_xml_bak\\' + pre_trading_day + '\\auction_arbi_config.xml'
g_dom = xml.dom.minidom.parse(xml_file)
time.clock()
###################################

def get_instrument_info_dict(instrument_id_array):
    instrument_info_dict = dict()
    tick_quote_name = 'Z:\\' + trading_day + '\\'
    for instrument_id in instrument_id_array:
        quote_file_name = tick_quote_name + instrument_id + ".csv"
        instrument_data_slice = pd.read_csv(quote_file_name, header=0, index_col=False, names=G_TICK_COLUMNS)
        open_price_series = instrument_data_slice.Open_Price[instrument_data_slice.Update_Time == '20:59:00'].values
        if  len(open_price_series) > 0:
            open_price = open_price_series[0]
            if np.isnan(open_price):
                open_price = 0
        else:
            open_price = 0

        if instrument_info_dict.has_key(instrument_id):
            pass
        else:
            instrument_info_dict[instrument_id] = open_price
    return instrument_info_dict

verification_path = 'D:\\strategy\\open_price_strategy\\open_auction_verification\\'
verification_folder = verification_path + trading_day

isExists = os.path.exists(verification_folder)
if not isExists:
    os.makedirs(verification_folder)

xml_file_verification_name = verification_folder + '\\' + "open_auction_verification.csv"
write_file = open(xml_file_verification_name, 'wb')
title_line = "first_instrument_id, second_instrument_id, trigger_ref_spread_price, actual_ref_spread_price, trigger_price_range, actual_price_range\n"
write_file.write(title_line)

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
    first_instrument = item.getElementsByTagName('main_instrument')[0].firstChild.data
    second_instrument = item.getElementsByTagName('sub_instrument')[0].firstChild.data
    trigger_price_range = float(item.getElementsByTagName('tigger_price_range')[0].firstChild.data.encode("gbk"))
    trigger_ref_spread_price = float(item.getElementsByTagName('tigger_ref_spread_price')[0].firstChild.data.encode("gbk"))

    variety_id = get_variety_id(first_instrument)
    tick, _, _ = get_variety_information(variety_id)
    first_open_price = instrument_info_dict[first_instrument]
    second_open_price = instrument_info_dict[second_instrument]
    if first_open_price != 0 and second_open_price != 0:
        actual_ref_spread_price = first_open_price - second_open_price
        actual_price_range = actual_ref_spread_price - trigger_ref_spread_price
        if abs(actual_price_range) > abs(trigger_price_range):
            str_line1 = first_instrument + ',' + second_instrument + ',' + str(trigger_ref_spread_price) + ',' + \
                       str(actual_ref_spread_price) + ',' + str(trigger_price_range) + ',' + str(actual_price_range) + ',shoudle trigger!'
            write_file.write(str_line1)
            write_file.write('\n')
        elif abs(actual_price_range) > limit_price_range_tick * tick:
            str_line1 = first_instrument + ',' + second_instrument + ',' + str(trigger_ref_spread_price) + ',' + \
                       str(actual_ref_spread_price) + ',' + str(trigger_price_range) + ',' + str(actual_price_range)  
            write_file.write(str_line1)
            write_file.write('\n')

write_file.close()
#############################
end_time = time.clock()



