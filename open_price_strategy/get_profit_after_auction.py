# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 该脚本用于根据集合竞价信息判断开盘之后的利润
#

@author: Tracy Zhu
"""

### 导入系统库
import sys, time
import logging

### 导入用户库
sys.path.append("C:\\Users\\Tracy Zhu\\Desktop\\tool\\open_price_strategy")
from plot_depth_quote import *
from get_open_minute_info import *


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
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.info(u"开始 mbl quote analyse...")
time.clock()
#########################

# 定义 环境变量
now = datetime.now()
# trading_day = now.strftime('%Y%m%d')
source_file_folder = 'E:\\quote_data\\depth_quote\\'
span_num = 10
LIMIT_RATIO = 1.2
open_time = '20:59:00'
duration_time = '21:01:00'
limit_profit = 8
draw_down_tick = 3
output_file_map={}

def judge_direction_after_auction(instrument_id, trading_day):
    to_deal_file_folder = source_file_folder + trading_day + '\\'
    minute_open_price = 0
    auction_open_price = 0
    total_bid_volume = 0
    total_ask_volume = 0
    direction = None
    delta_list = []
    mbl_quote_file_name = to_deal_file_folder + '\\' + instrument_id + '.txt'
    mbl_quote_file = open(mbl_quote_file_name,"r")
    all_lines = mbl_quote_file.readlines()
    line_total_count = len(all_lines)
    loop_total_count = int (line_total_count / 2)
    initial_update_time = all_lines[0][:-1].split(",")[1][:8]
    variety_id = get_variety_id(instrument_id)
    tick, _, _, = get_variety_information(variety_id)

    logging.info("total line: %d",line_total_count)
    if loop_total_count > 30 and initial_update_time > '20:54:00':
        # 一次数据两行，买一行，卖一行
        for i in range(1, loop_total_count):
            first_line = all_lines[i * 2]
            next_line = all_lines[i * 2 + 1]
            buy_price = first_line[:-1].split(",")[2]
            sell_price = next_line[:-1].split(",")[2]
            update_time = first_line[:-1].split(",")[1][:8]
            if update_time < '20:58:00':
                buy_line = first_line
                sell_line = next_line
                bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(buy_line, sell_line)
                minute_open_price, _, _, _, _, = get_open_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
            if update_time > '20:58:00' and buy_price > sell_price:
                buy_line = first_line
                sell_line = next_line
                bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(buy_line, sell_line)
                previous_open_price, _, _, _, _, = get_open_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
                next_buy_line = all_lines[i * 2 + 2]
                next_sell_line = all_lines[i * 2 + 3]
                bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(next_buy_line, next_sell_line)
                next_open_price, _, _, _, _, = get_open_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
                price_delta = next_open_price - previous_open_price
                if price_delta == None:
                    price_delta = 0
                delta_list.append(price_delta)
            if buy_price < sell_price:
                buy_line = all_lines[i*2 - 2]
                sell_line = all_lines[i*2 - 1]
                update_time = get_update_time(buy_line)
                logging.info("plot time: %s", update_time)
                bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(buy_line, sell_line)
                auction_open_price, total_bid_volume, total_ask_volume, _, _, = get_open_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
                # bid_volume_arr, ask_volume_arr, price_arr = unify_bid_ask_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
                # total_bid_volume = sum(bid_volume_arr)
                # total_ask_volume = sum(ask_volume_arr)
                break

        if total_ask_volume != 0 and total_bid_volume != 0 and len(delta_list) > 0:
            if float(total_bid_volume) / float(total_ask_volume) > LIMIT_RATIO:
                direction = 1
            elif float(total_ask_volume) / float(total_bid_volume) > LIMIT_RATIO:
                direction = 0
        else:
            direction = None
    else:
        direction = None
        total_bid_volume = 0
        total_ask_volume = 0

    mbl_quote_file.close()
    return direction, total_bid_volume, total_ask_volume


def verification_correction(instrument_id, trading_day):
    profit = 0
    main_quote_data = read_data(instrument_id, trading_day)
    _, _, open_price  = get_open_minute_change(main_quote_data)
    direction, total_bid_volume, total_ask_volume = judge_direction_after_auction(instrument_id, trading_day)

    variety_id = get_variety_id(instrument_id)
    tick, _, _, = get_variety_information(variety_id)

    max_price = open_price
    min_price = open_price
    if direction == 1:
        for price_index in main_quote_data.index:
            price = main_quote_data.Last_Price[price_index]
            update_time = main_quote_data.Update_Time[price_index]
            if update_time > '20:59:00':
                if max_price - price > (draw_down_tick) * tick:
                    profit = price - open_price
                    break
                if max_price < price:
                    max_price = price

    elif direction == 0:
        for price_index in main_quote_data.index:
            price = main_quote_data.Last_Price[price_index]
            update_time = main_quote_data.Update_Time[price_index]
            if update_time > '20:59:00':
                if price - min_price > (draw_down_tick) * tick:
                    profit = open_price - price
                    break
                if min_price > price:
                    min_price = price
    else:
        profit = 'undefined'

    str_line = str(trading_day) + "," + instrument_id + "," + str(total_bid_volume) + "," \
               + str(total_ask_volume) + "," + str(profit) + "\n"
    f.write(str_line)

if __name__ == '__main__':
    result_file_name = "get_profit_after_auction_one_condition.csv"
    f = open(result_file_name, "wb")
    f.write("trading_day, instrument_id, total_bid_volume, total_ask_volume, profit\n")

    trading_day_list = []
    for dirpath, dirnames, filenames in os. walk(source_file_folder):
        for trading_day in dirnames:
            trading_day_list.append(trading_day)


    for trading_day in trading_day_list:
        day_file_folder = source_file_folder + trading_day + "\\"
        instrument_file_list = get_instrument_file_list(trading_day)
        for son_dir_path, son_dir_names, son_filenames in os.walk(day_file_folder):
            for file_name in son_filenames:
                if len(file_name) == 10 and file_name[-4:] == '.txt':
                    to_deal_file = day_file_folder + file_name
                    instrument_id = file_name[:-4]
                    variety_id = get_variety_id(instrument_id)
                    instrument_list = instrument_file_list[variety_id]
                    main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
                    if instrument_id == main_instrument_id:
                        print_line = file_name[:-4] + " in " + str(trading_day)
                        print print_line
                        verification_correction(instrument_id, str(trading_day))

    f.close()



