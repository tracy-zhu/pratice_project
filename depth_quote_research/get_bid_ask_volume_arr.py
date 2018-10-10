# encoding: utf-8
"""
Created on Mon Apr 10 14:49:45 2017

# 本脚本将深度行情买卖量序列通过深度行情文件转出来

@author: Tracy Zhu
"""

### 导入系统库
import sys, time
import logging

reload(sys)

### 导入用户库
sys.path.append("..")
from python_base.open_price_algorithm import *

g_direction = 0
open_price = 0
depth_level_2 = 5
depth_level_3 = 20

now = datetime.now()
trading_day = now.strftime('%Y%m%d')
limit_order_volume_ratio = 1.5
depth_quote_after_auction_file_folder = 'E:\\quote_data\\depth_quote_after_auction\\'
to_deal_file_folder = 'E:\\quote_data\\depth_quote_after_auction\\' + trading_day + '\\'
out_file_folder = 'E:\\quote_data\\bid_ask_volume_arr\\' + trading_day + '\\'
isExists = os.path.exists(out_file_folder)
if not isExists:
    os.makedirs(out_file_folder)


# 根据深度买卖挂单量判断短时间走势
def get_bid_ask_volume(buy_line,sell_line, depth_level):
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

    for bid_index in range(1, depth_level + 1):
        bid_price = float(buy_item_list[bid_index*2])
        bid_volume = int(buy_item_list[bid_index*2+1])
        bid_price_dict[bid_price] = bid_volume
        sum_bid_volume = sum_bid_volume + bid_volume

    for ask_index in range(1, depth_level + 1):
        ask_price = float(sell_item_list[ask_index*2])
        ask_volume = int(sell_item_list[ask_index*2+1])
        ask_price_dict[ask_price] = ask_volume
        sum_ask_volume = sum_ask_volume + ask_volume

    return sum_bid_volume, sum_ask_volume, last_middle_price

# 查找出现大单极值的时间和价格
def find_extreme_large_order(buy_line, sell_line, depth_level):
    support_price = None
    resistance_price = None
    buy_item_list = buy_line[:-1].split(",")
    sell_item_list = sell_line[:-1].split(",")

    update_time = get_update_time(buy_line)
    sum_bid_volume = 0
    sum_ask_volume = 0

    bid_price_dict = dict()
    ask_price_dict = dict()
    bid_volume_arr = []
    ask_volume_arr = []

    for bid_index in range(1, depth_level + 1):
        bid_price = float(buy_item_list[bid_index*2])
        bid_volume = int(buy_item_list[bid_index*2+1])
        bid_price_dict[bid_price] = bid_volume
        bid_volume_arr.append(bid_volume)
        sum_bid_volume = sum_bid_volume + bid_volume

    for ask_index in range(1, depth_level + 1):
        ask_price = float(sell_item_list[ask_index*2])
        ask_volume = int(sell_item_list[ask_index*2+1])
        ask_price_dict[ask_price] = ask_volume
        ask_volume_arr.append(ask_volume)
        sum_ask_volume = sum_ask_volume + ask_volume

    bid_volume_series = Series(bid_volume_arr)
    ask_volume_series = Series(ask_volume_arr)
    extreme_bid_volume = bid_volume_series.quantile(0.75) + \
                         1.5 * (bid_volume_series.quantile(0.75) - bid_volume_series.quantile(0.25))
    extreme_ask_volume = ask_volume_series.quantile(0.75) + \
                         1.5 * (ask_volume_series.quantile(0.75) - ask_volume_series.quantile(0.25))

    max_bid_volume, key_bid_price = max((bid_volume, bid_price) for (bid_price, bid_volume) in bid_price_dict.items())
    max_ask_volume, key_ask_price = max((ask_volume, ask_price) for (ask_price, ask_volume) in ask_price_dict.items())

    if max_bid_volume > extreme_bid_volume:
        support_price = key_bid_price
    if max_ask_volume > extreme_ask_volume:
        resistance_price = key_ask_price

    return update_time, support_price, resistance_price


def get_update_time(buy_line):
    buy_item_list = buy_line[:-1].split(",")
    update_time = buy_item_list[1]
    return update_time


# 找出当天该合约所有出现大单的时间
def large_order_occurrence_stat(instrument_id):
    mbl_quote_file_name = to_deal_file_folder + '\\' + instrument_id + '.txt'
    result_file_name = out_file_folder + '\\' + instrument_id + '_large_order_occurrence.csv'
    mbl_quote_file = open(mbl_quote_file_name,"r")
    result_file = open(result_file_name, 'wb')
    all_lines = mbl_quote_file.readlines()
    line_total_count = len(all_lines)
    loop_total_count = int(line_total_count / 2)
    result_file.write('instrument_id, update_time, support_price, resistance_price\n')

    logging.info("total line: %d",line_total_count)
    # 一次数据两行，买一行，卖一行
    for i in range(1, loop_total_count):
        buy_line = all_lines[i * 2]
        sell_line = all_lines[i * 2 + 1]
        update_time = get_update_time(buy_line)
        logging.info("plot time: %s", update_time)
        print update_time
        update_time, support_price, resistance_price = find_extreme_large_order(buy_line, sell_line, depth_level_3)
        if support_price != None or resistance_price != None:
            str_line = instrument_id + ',' + update_time + ',' + str(support_price) + ',' + str(resistance_price) + '\n'
            result_file.write(str_line)

    mbl_quote_file.close()
    result_file.close()


#主函数，参数 mbl 原始文件
def main_deal_func(instrument_id):
    mbl_quote_file_name = to_deal_file_folder + '\\' + instrument_id + '.txt'
    result_file_name = out_file_folder + '\\' + instrument_id + '_bid_ask_volume_arr.csv'
    mbl_quote_file = open(mbl_quote_file_name,"r")
    result_file = open(result_file_name, 'wb')
    all_lines = mbl_quote_file.readlines()
    line_total_count = len(all_lines)
    loop_total_count = int(line_total_count / 2)
    result_file.write('instrument_id, update_time, sum_bid_volume, sum_ask_volume, last_middle_price\n')

    logging.info("total line: %d",line_total_count)
    # 一次数据两行，买一行，卖一行
    for i in range(1, loop_total_count):
        buy_line = all_lines[i * 2]
        sell_line = all_lines[i * 2 + 1]
        update_time = get_update_time(buy_line)
        logging.info("plot time: %s", update_time)
        print update_time
        sum_bid_volume_level_2, sum_ask_volume_level_2, last_middle_price = get_bid_ask_volume(buy_line, sell_line, depth_level_2)
        sum_bid_volume_level_3, sum_ask_volume_level_3, _ = get_bid_ask_volume(buy_line, sell_line, depth_level_3)
        print_line = instrument_id + ',' + update_time + ',' + str(sum_bid_volume_level_2) + ',' + str(sum_ask_volume_level_2) + ',' \
                    + str(last_middle_price) + '\n'
        result_file.write(print_line)

    mbl_quote_file.close()
    result_file.close()


def find_unbalance_order_volume(instrument_id, trading_day):
    mbl_quote_file_name = depth_quote_after_auction_file_folder + trading_day + '\\' + instrument_id + '.txt'
    mbl_quote_file = open(mbl_quote_file_name,"r")
    all_lines = mbl_quote_file.readlines()
    line_total_count = len(all_lines)
    loop_total_count = int(line_total_count / 2)

    logging.info("total line: %d",line_total_count)
    # 一次数据两行，买一行，卖一行
    for i in range(1, loop_total_count):
        buy_line = all_lines[i * 2]
        sell_line = all_lines[i * 2 + 1]
        update_time = get_update_time(buy_line)
        logging.info("plot time: %s", update_time)
        print update_time
        sum_bid_volume, sum_ask_volume, _= get_bid_ask_volume(buy_line, sell_line, 5)
        if float(sum_bid_volume) / float(sum_ask_volume) > limit_order_volume_ratio or \
                                float(sum_ask_volume) / float(sum_bid_volume) > limit_order_volume_ratio:
            print_line =instrument_id + ',' + trading_day + ',' + update_time + ',' + str(sum_bid_volume) + ',' +\
                        str(sum_ask_volume) + '\n'
            result_file.write(print_line)
            break

    mbl_quote_file.close()


#主函数调用
if __name__ == '__main__':
    # instrument_id = 'RB1710'
    # trading_day_list = get_trading_day_list()
    # result_file_name = 'bid_ask_volume_unbalance_list.csv'
    # result_file = open(result_file_name, 'wb')
    # result_file.write('instrument_id, trading_day, update_time, sum_bid_volume, sum_ask_volume\n')
    # for trade_day in trading_day_list:
    #     trading_day = trade_day[:-1]
    #     if trading_day > '20170419':
    #         find_unbalance_order_volume(instrument_id, trading_day)
    # result_file.close()

    instrument_id = 'RB1710'
    trading_day = '20170420'
    main_deal_func(instrument_id)
    large_order_occurrence_stat(instrument_id)


    #########################
    end_time = time.clock()
    logging.info(u"end 共耗时: %s",end_time)
