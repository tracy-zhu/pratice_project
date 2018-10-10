# encoding: utf-8
"""
Created on Mon Apr 10 14:49:45 2017

# 本脚本通过判断最近五档，挂单量增长的速度，判断出行情出现反转的机会
# 前提为总买量和总卖量已经处于不平衡的状态

@author: Tracy Zhu
"""

### 导入系统库
import sys, time
import logging
from collections import deque

reload(sys)

### 导入用户库
sys.path.append("..")
from python_base.open_price_algorithm import *

g_direction = 0
open_price = 0

now = datetime.now()
# trading_day = now.strftime('%Y%m%d')
trading_day = '20170420'
limit_order_volume_ratio = 1.5
depth_quote_after_auction_file_folder = 'E:\\quote_data\\depth_quote_after_auction\\'
to_deal_file_folder = 'E:\\quote_data\\depth_quote_after_auction\\' + trading_day + '\\'
out_file_folder = 'E:\\quote_data\\bid_ask_volume_arr\\' + trading_day + '\\'
isExists = os.path.exists(out_file_folder)
if not isExists:
    os.makedirs(out_file_folder)
instrument_id = 'RB1710'


# 根据深度买卖挂单量判断短时间走势
def get_bid_ask_volume(buy_line,sell_line):
    buy_item_list = buy_line[:-1].split(",")
    sell_item_list = sell_line[:-1].split(",")

    instrument_id = buy_item_list[0]
    variety_id = get_variety_id(instrument_id)
    tick, _, _ = get_variety_information(variety_id)
    sum_bid_volume = 0
    sum_ask_volume = 0

    bid_price1 = float(buy_item_list[2])
    ask_price1 = float(sell_item_list[2])
    last_middle_price = (bid_price1 + ask_price1) / 2

    bid_price_dict = dict()
    ask_price_dict = dict()

    for bid_index in range(1, len(buy_item_list)/2):
        bid_price = float(buy_item_list[bid_index*2])
        bid_volume = int(buy_item_list[bid_index*2+1])
        bid_price_dict[bid_price] = bid_volume
        sum_bid_volume = sum_bid_volume + bid_volume

    for ask_index in range(1, len(sell_item_list)/2):
        ask_price = float(sell_item_list[ask_index*2])
        ask_volume = int(sell_item_list[ask_index*2+1])
        ask_price_dict[ask_price] = ask_volume
        sum_ask_volume = sum_ask_volume + ask_volume

    return sum_bid_volume, sum_ask_volume, last_middle_price

def get_update_time(buy_line):
    buy_item_list = buy_line[:-1].split(",")
    update_time = buy_item_list[1]
    return update_time


def find_high_speed_volume_change(instrument_id, trading_day):
    mbl_quote_file_name = depth_quote_after_auction_file_folder + trading_day + '\\' + instrument_id + '.txt'
    mbl_quote_file = open(mbl_quote_file_name,"r")
    all_lines = mbl_quote_file.readlines()
    line_total_count = len(all_lines)
    loop_total_count = int(line_total_count / 2)
    spam_bid_volume = deque(maxlen=6)
    spam_ask_volume = deque(maxlen=6)
    bid_volume_change_array = deque(maxlen=12)
    ask_volume_change_array = deque(maxlen=12)

    logging.info("total line: %d",line_total_count)
    # 一次数据两行，买一行，卖一行
    for i in range(1, loop_total_count):
        buy_line = all_lines[i * 2]
        sell_line = all_lines[i * 2 + 1]
        update_time = get_update_time(buy_line)
        logging.info("plot time: %s", update_time)
        print update_time
        sum_bid_volume, sum_ask_volume, _= get_bid_ask_volume(buy_line, sell_line)
        spam_bid_volume.append(sum_bid_volume)
        spam_ask_volume.append(sum_ask_volume)
        bid_volume_change = spam_bid_volume[-1] - spam_bid_volume[0]
        ask_volume_change = spam_ask_volume[-1] - spam_ask_volume[0]
        bid_volume_change_array.append(bid_volume_change)
        ask_volume_change_array.append(ask_volume_change)
        if float(sum_bid_volume) / float(sum_ask_volume) > limit_order_volume_ratio:
            if min(ask_volume_change_array) > 0:
                print_line =instrument_id + ',' + trading_day + ',' + update_time + ',' + str(sum_bid_volume) + ',' + \
                            str(sum_ask_volume) + ',rise\n'
                result_file.write(print_line)
                break
        elif float(sum_ask_volume) / float(sum_bid_volume) > limit_order_volume_ratio:
            if min(bid_volume_change_array) > 0:
                print_line =instrument_id + ',' + trading_day + ',' + update_time + ',' + str(sum_bid_volume) + ',' + \
                            str(sum_ask_volume) + ',fall\n'
                result_file.write(print_line)
                break

    mbl_quote_file.close()


#主函数调用
if __name__ == '__main__':
    instrument_id = 'RB1710'
    trading_day_list = get_trading_day_list()
    result_file_name = 'bid_ask_volume_unbalance_speed.csv'
    result_file = open(result_file_name, 'wb')
    result_file.write('instrument_id, trading_day, update_time, sum_bid_volume, sum_ask_volume\n')
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day > '20170419':
            print trading_day
            find_high_speed_volume_change(instrument_id, trading_day)
    result_file.close()


    #########################
    end_time = time.clock()
    logging.info(u"end 共耗时: %s",end_time)
