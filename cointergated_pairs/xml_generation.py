# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 本脚本用于在每一个交易小节生成配置文件

@author: Tracy Zhu
"""

# 导入系统库
import sys, time, os
import logging
import shutil

# 导入用户库
sys.path.append("..")
from commodity_pairs_trading import *
int_hour = time.localtime().tm_hour
now = datetime.now()
trading_day = now.strftime('%Y%m%d')
pre_trading_day = get_pre_trading_day(trading_day)
#trading_day = '20170711'
instrument_group_list = [('RM801', 'm1801'), ('RM709', 'm1709'), ('c1709', 'cs1709'),
                         ('c1801', 'cs1801'), ('y1709', 'OI709'), ('y1801', 'OI801')]
variety_id1_list = []
for instrument_group in instrument_group_list:
    variety_id1_list.append(instrument_group[0])
instr_order_unit_dict = {'RM': [7, 5], 'c1': [6, 5], 'y1': [5, 5]}
posi_num_dict = {'RM': 14, 'c1': 12, 'y1' : 10}
direction_dict = {'RM': 0, 'c1': 0, 'y1' : 0}
account_no = '9011398'
high_match_trade_result_file_folder = "E:\\high_match_trade\\" + trading_day + "\\"
isExists = os.path.exists(high_match_trade_result_file_folder)
if not isExists:
    os.makedirs(high_match_trade_result_file_folder)
high_match_trade_result_file = high_match_trade_result_file_folder + 'strategy.xml'
f = open(high_match_trade_result_file, 'wb')
position_file_name = "E:\\high_match_trade_trading_report\\" + u'持仓_' + trading_day[2:] + '.csv'
position_file = open(position_file_name, 'r')
total_posi_dict = dict()
for instrument_id1 in variety_id1_list:
    total_posi_dict[instrument_id1] = ['0', '0']
all_lines = position_file.readlines()
for line in all_lines[1:]:
    line_list = line.split(',')
    variety_id = line_list[0]
    direction = line_list[1]
    if variety_id in variety_id1_list:
        print variety_id
        posi_num = posi_num_dict[variety_id[:2]]
        total_posi = int(line_list[2]) / posi_num * posi_num
        if direction == '\xa1\xa1\xc2\xf4':
            total_posi_dict[variety_id] = ['0', str(total_posi)]
        elif direction == '\xc2\xf2\xa1\xa1':
            total_posi_dict[variety_id] = [str(total_posi), '0']


def get_beta_std(instrument_group):
    instrument_id1 = instrument_group[0]
    instrument_id2 = instrument_group[1]
    variety_id1 = instrument_id1[:-3]
    variety_id2 = instrument_id2[:-3]
    instrument_date = instrument_id2[-3:]
    if 8<= int_hour <=9 and variety_id1[0] == 'c':
        close_price_series1, close_price_series2 = get_price_series(pre_trading_day, instrument_date, variety_id1, variety_id2)
    else:
        close_price_series1, close_price_series2 = get_price_series(trading_day, instrument_date, variety_id1, variety_id2)
    beta, std = linear_model_main(close_price_series2, close_price_series1)
    return beta, std


def print_xml_one_group(instrument_group, num):
    instrument_id1 = instrument_group[0]
    instrument_id2 = instrument_group[1]
    variety_id1 = instrument_id1[:-3]
    instr_order_unit_list = instr_order_unit_dict[variety_id1]
    direction = direction_dict[variety_id1]
    beta, std = get_beta_std(instrument_group)
    if variety_id1[0] == 'c' and std < 2:
        posi_no = 0
    elif variety_id1[0] == 'y' and std < 4:
        posi_no = 0
    else:
        posi_no = posi_num_dict[variety_id1]
    [buy_posi, sell_posi] = total_posi_dict[instrument_id1]
    line1 = "\t<strategy" + str(num) + " note=\"config_data\">\n"
    line2 = "\t\t<instrument1>" + instrument_id1 + "</instrument1>\n"
    line3 =  "\t\t<instrument2>" + instrument_id2 + "</instrument2>\n"
    line4 = "\t\t<instr1_order_unit>" + str(instr_order_unit_list[0]) + "</instr1_order_unit>\n"
    line5 = "\t\t<instr2_order_unit>" + str(instr_order_unit_list[1]) + "</instr2_order_unit>\n"
    line6 = "\t\t<direction>" + str(direction) + "</direction>\n"
    line7 = "\t\t<std>" + str(std) + "</std>\n"
    line8 = "\t\t<beta>" + str(beta) + "</beta>\n"
    line9 = "\t\t<open_std>1.0</open_std>\n"
    line10 = "\t\t<close_std>-1.0</close_std>\n"
    line11 = "\t\t<posi_num>" + str(posi_no) + "</posi_num>\n"
    line12 = "\t\t<account_no>" + account_no + "</account_no>\n"
    line13 = "\t\t<recover_position>\n"
    line14 = "\t\t\t<buy_posi>" + str(buy_posi) + "</buy_posi>\n"
    line15 = "\t\t\t<buy_posi_price>2251.4</buy_posi_price>\n"
    line16 = "\t\t\t<sell_posi>" + str(sell_posi) + "</sell_posi>\n"
    line17 = "\t\t\t<sell_posi_price>2251.4</sell_posi_price>\n"
    line18 = "\t\t</recover_position>\n"
    line19 = "\t\t<trade_phase>\n\t\t\t<trade_begin_time1>21:00:00</trade_begin_time1>\n" \
             "\t\t\t<trade_end_time1>23:29:55</trade_end_time1>\n\n" \
             "\t\t\t<trade_begin_time2>09:00:01</trade_begin_time2>\n" \
             "\t\t\t<trade_end_time2>10:14:55</trade_end_time2>\n\n" \
             "\t\t\t<trade_begin_time3>10:30:01</trade_begin_time3>\n" \
             "\t\t\t<trade_end_time3>11:29:55</trade_end_time3>\n\n" \
             "\t\t\t<trade_begin_time4>13:30:01</trade_begin_time4>\n" \
             "\t\t\t<trade_end_time4>14:59:55</trade_end_time4>\n\n" \
             "\t\t</trade_phase>\n"
    line20 = "\t</strategy" + str(num) + ">"
    print>>f , line1, line2, line3, line4, line5, line6, line7, line8, line9, line10, line11, line12, line13, line14,\
        line15, line16, line17, line18, line19, line20, '\n'


print>>f, "<strategy>\n"
num = 1
for instrument_group in instrument_group_list:
    print_xml_one_group(instrument_group, num)
    num += 1
print>>f, "</strategy>\n"
f.close()










