#  -*- coding: utf-8 -*-

# 用于比较每天生成的open_auction_smart两个配置文件的合约是否一致

# 导入系统库
import sys, time, os

# 导入用户库
sys.path.append("..")
import xml.dom.minidom

# 全局变量
auction_arbi_config_file = "D:\\strategy\\open_auction_smart\\auction_arbi_config.xml"
open_auction_smart_file = "D:\\strategy\\open_auction_smart\\open_auction_smart.xml"
result_file = "D:\\strategy\\open_auction_smart\\compare_instrument.txt"

raw_instrument_id_array = []

open_auction_smart_dom = xml.dom.minidom.parse(open_auction_smart_file)
open_auction_smart_root = open_auction_smart_dom.documentElement
open_auction_smart_itemlist = open_auction_smart_root.getElementsByTagName('query_instrument_list')

for item in open_auction_smart_itemlist:
    num = len(item.getElementsByTagName('query_instrument'))
    for index in range(num):
        instrument_id = item.getElementsByTagName('query_instrument')[index].firstChild.data
        raw_instrument_id_array.append(instrument_id)

auction_arbi_config_dom = xml.dom.minidom.parse(auction_arbi_config_file)
auction_arbi_config_root = auction_arbi_config_dom.documentElement
auction_arbi_config_itemlist = auction_arbi_config_root.getElementsByTagName('auction_arbi_variety')

f = open(result_file, 'wb')
for item in auction_arbi_config_itemlist:
    first_instrument = item.getElementsByTagName('main_instrument')[0].firstChild.data
    second_instrument = item.getElementsByTagName('sub_instrument')[0].firstChild.data
    if len(second_instrument) > 5 and len(first_instrument) > 5:
        if first_instrument not in raw_instrument_id_array:
            print >> f, first_instrument, "\n"
        if second_instrument not in raw_instrument_id_array:
            print >> f, second_instrument, "\n"

f.close()
