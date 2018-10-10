# -*- coding: utf-8 -*-
"""

# 用于对比每天的期权新增合约没有配置进入服务器配置的xml中

# 输出到一个txt文件中

Mon 2017/11/30

@author: Tracy Zhu
"""

from datetime import datetime
import xml.dom.minidom
from glob import glob


now = datetime.now()
trading_day = now.strftime('%Y%m%d')
log_file_name = glob(r"D:\\query_instrument\\log\\strategy.g2log." + trading_day + "-08303?.log")[0]

instrument_id_list = []
with open(log_file_name) as f:
    str_lines = f.readlines()
    for line in str_lines[1:]:
        line_list = line.split(":")
        if len(line_list) > 0:
            after_line = line_list[3]
            instrument_id = after_line[:13]
            #print instrument_id
            instrument_id_list.append(instrument_id)


xml_file_name = "C:\\Users\\Tracy Zhu\\Desktop\\cffex_option_strategy_xml_bak\\counter.xml"
g_dom = xml.dom.minidom.parse(xml_file_name)
g_root = g_dom.documentElement
g_item_list = g_root.getElementsByTagName('subscribs')

xml_instrument_id_list = []
for item in g_item_list:
    num = len(item.getElementsByTagName('subscrib'))
    for index in range(num):
        instrument_id = item.getElementsByTagName('subscrib')[index].firstChild.data
        #print instrument_id
        xml_instrument_id_list.append(instrument_id)

for instrument_id in instrument_id_list:
    if instrument_id not in xml_instrument_id_list:
        print instrument_id


