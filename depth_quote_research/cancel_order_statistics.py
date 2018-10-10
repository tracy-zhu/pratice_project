# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 13:57:19 2017

# 用于统计集合竞价的撤单情况

@author: Tracy Zhu
"""


### 导入系统库
import sys,time
import logging
from datetime import datetime, timedelta

### 导入用户库
sys.path.append("..")
from python_base.open_price_algorithm import *

### 设置日志文件
log_file_name = "mbl_quote.log"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s  %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    filename=log_file_name,
                    filemode='w')
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.info(u"开始 mbl quote analyse...")
time.clock()
#########################

# 定义 环境变量
# now = datetime.now()
# trading_day = now.strftime('%Y%m%d')
trading_day = '20170502'
to_deal_file_folder = 'E:\\quote_data\\depth_quote\\' + trading_day + '\\'

instrument_id = 'ZN1707'

output_file_map={}
#处理一次买卖行情数据
def get_open_price(buy_line, sell_line):  
    buy_item_list = buy_line[:-1].split(",")
    sell_item_list = sell_line[:-1].split(",")
    
    update_time = buy_item_list[1].split('.')
    update_time_str = update_time[0] + '.' + update_time[1]
 
    price_total_count = min(len(buy_item_list[2:]), len(sell_item_list[2:]))   
    loop_total_count = price_total_count / 2
    
    total_bid_volume = 0
    total_ask_volume = 0
    bid_price_dict = dict()
    ask_price_dict = dict()
    for i in range(0, loop_total_count):
        bid_price = int(buy_item_list[2:][2 * i])
        ask_price = int(sell_item_list[2:][2 * i])
        bid_volume = int(buy_item_list[2:][2 * i + 1])
        ask_volume = int(sell_item_list[2:][2 *i + 1])
        total_bid_volume += bid_volume
        bid_price_dict[bid_price] = total_bid_volume
        total_ask_volume += ask_volume
        ask_price_dict[ask_price] = total_ask_volume
    
    max_match_volume = 0
    last_ask_price = 0
    last_bid_price = 0
    last_price = 0
    total_match_volume = 0
    final_ask_price = 0
    final_bid_price = 0
    final_deal_price = 0
    for (ask_price, total_ask_volume) in ask_price_dict.items():
        filter_list = [x for x in bid_price_dict.keys() if x >= ask_price]
        if len(filter_list) > 0:
            deal_bid_price = min(filter_list)
            deal_bid_volume = bid_price_dict[deal_bid_price]
            filter_list.sort(reverse=True)
            if deal_bid_volume >= total_ask_volume:
                for bid_price in filter_list:
                    if bid_price_dict[bid_price] >= total_ask_volume:
                        final_bid_price = bid_price
                        final_deal_price = bid_price
                        final_ask_price = ask_price
                        total_match_volume = total_ask_volume
                        break
            else:
                ask_filter_list = [x for x in ask_price_dict.keys() if x <= deal_bid_price]
                ask_filter_list.sort()
                for ask_price in ask_filter_list:
                    if ask_price_dict[ask_price] >= deal_bid_volume:
                        final_bid_price = deal_bid_price
                        final_deal_price = ask_price
                        final_ask_price = ask_price
                        total_match_volume = deal_bid_volume
                        break
        if total_match_volume > max_match_volume:
            max_match_volume = total_match_volume
            last_ask_price = final_ask_price
            last_bid_price = final_bid_price
            last_price = final_deal_price


    print instrument_id, update_time_str, last_ask_price, last_bid_price, max_match_volume, last_price

    logging.info(update_time)


def get_difference_between_quote(now_line, last_line):
    now_item_list = now_line[:-1].split(",")
    last_item_list = last_line[:-1].split(",")

    update_time = now_item_list[1].split('.')
    update_time_str = update_time[0] + '.' + update_time[1]
    
    loop_now_count = len(now_item_list[2:]) / 2
    loop_last_count = len(last_item_list[2:]) / 2
    
    now_price_dict = dict()
    last_price_dict = dict()
    for i in range(0, loop_now_count):
        now_price = int(now_item_list[2:][2 * i])
        now_volume = int(now_item_list[2:][2 * i + 1])
        now_price_dict[now_price] = now_volume

    for i in range(0, loop_last_count):
        last_price = int(last_item_list[2:][2 * i])
        last_volume = int(last_item_list[2:][2 * i + 1])
        last_price_dict[last_price] = last_volume

    for price, volume in now_price_dict.items():
        if price in last_price_dict.keys():
            if now_price_dict[price] < last_price_dict[price]:
                volume_change = now_price_dict[price] - last_price_dict[price]
                if abs(volume_change) > 10:
                    print update_time_str, price, volume_change, last_price_dict[price], 'oredr_reduce\n'

            
    for price, volume in last_price_dict.items():
        if not price in now_price_dict.keys():
            print update_time_str, price, volume, 'cancel_order\n'
            
            
#主函数，参数 mbl 原始文件
def main_deal_func(instrument_id):
    mbl_quote_file_name = to_deal_file_folder + '\\' + instrument_id + '.txt'
    mbl_quote_file = open(mbl_quote_file_name,"r")
    all_lines = mbl_quote_file.readlines()
    line_total_count = len(all_lines)
    loop_total_count = int (line_total_count / 2)
    
    logging.info("total line: %d",line_total_count)
    # 一次数据两行，买一行，卖一行
    for i in range(1, loop_total_count - 1):
        first_line = all_lines[i * 2]
        next_line = all_lines[i * 2 + 1]
        buy_price = float(first_line[:-1].split(",")[2])
        sell_price = float(next_line[:-1].split(",")[2])
        if buy_price > sell_price:
            last_buy_line = all_lines[i*2 - 2]
            last_sell_line = all_lines[i*2 - 1]
            buy_line = all_lines[i*2]
            sell_line = all_lines[i*2 + 1]
            print "buy_direction_difference:\n"
            get_difference_between_quote(buy_line, last_buy_line)
            print "sell_direction_difference:\n"
            get_difference_between_quote(sell_line, last_sell_line)
            get_accumulative_volume_by_price(buy_line, sell_line, 21920)
            # get_open_price(all_lines[i*2 + 2], all_lines[i*2 + 3])
    mbl_quote_file.close()

        
#主函数调用
main_deal_func(instrument_id)


#########################
end_time = time.clock()
logging.info(u"end 共耗时: %s",end_time)

