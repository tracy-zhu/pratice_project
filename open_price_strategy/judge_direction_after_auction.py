# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 该脚本用于根据集合竞价信息判断开盘之后的方向
# 其中总买卖量的比值要大于一定的比例，并且当前成交量

@author: Tracy Zhu
"""

### 导入系统库
import sys, time
import logging
from collections import deque

### 导入用户库
sys.path.append("C:\\Users\\Tracy Zhu\\Desktop\\tool\\open_price_strategy")
from plot_depth_quote import *
from get_open_minute_info import *
from python_base.get_open_volume_series_instrument import *

### 设置日志文件
log_file_name = "mbl_quote.log"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s  %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    filename=log_file_name,
                    filemode='w')
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
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
source_file_folder = 'Q:\\open_auction_depth_quote\\'
span_num = 1000
TOTAL_VOLUME_LIMIT_RATIO = 1.5
OPEN_VOLUME_MA_LIMIT_RATIO = 2.5
LIMIT_AVERAGE_CHANGE = 2
LIMIT_INTENSITY_DISTANCE = 8
output_file_map = {}


def judge_direction_after_auction(instrument_id, trading_day):
    to_deal_file_folder = source_file_folder + trading_day + '\\'
    total_bid_volume = 0
    total_ask_volume = 0
    max_intensity_bid_price = 0
    max_intensity_ask_price = 0
    mbl_quote_file_name = to_deal_file_folder + '\\' + instrument_id + '.txt'
    mbl_quote_file = open(mbl_quote_file_name, "r")
    all_lines = mbl_quote_file.readlines()
    line_total_count = len(all_lines)
    loop_total_count = int(line_total_count / 2)
    initial_update_time = all_lines[0][:-1].split(",")[1][:8]
    variety_id = get_variety_id(instrument_id)
    tick, unit, _, = get_variety_information(variety_id)

    logging.info("total line: %d", line_total_count)
    if loop_total_count > 30 and initial_update_time > '20:54:00':
        # 一次数据两行，买一行，卖一行
        for i in range(1, loop_total_count):
            first_line = all_lines[i * 2]
            next_line = all_lines[i * 2 + 1]
            buy_price = first_line[:-1].split(",")[2]
            sell_price = next_line[:-1].split(",")[2]
            if buy_price < sell_price:
                buy_line = all_lines[i * 2 - 2]
                sell_line = all_lines[i * 2 - 1]
                update_time = get_update_time(buy_line)
                logging.info("plot time: %s", update_time)
                bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(buy_line, sell_line)
                auction_open_price, _, _, _, _, = get_open_price(bid_price_dict,
                                                                                               ask_price_dict,
                                                                                               max_price, min_price,
                                                                                               tick)
                total_bid_volume, total_ask_volume = get_accumulative_volume_by_index_price(bid_price_dict, ask_price_dict, auction_open_price, tick, span_num)
                max_intensity_bid_price, max_intensity_ask_price = get_max_intensity_price(bid_price_dict, ask_price_dict)
                break

        last_open_volume, mean_volume = get_open_volume_series(instrument_id, trading_day)
        ma_volume_ratio = float(last_open_volume) / float(mean_volume)

        main_quote_data = read_data(instrument_id, trading_day)
        main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
        if len(main_open_quote) > 0:
            open_price = main_open_quote.Last_Price.values[0]
            pre_close_price = main_open_quote.Pre_Close_Price.values[0]
            change_ratio = get_outer_data_change(instrument_id, trading_day)
            target_open_price = pre_close_price * float(1 + change_ratio / float(100))
            # short_profit, long_profit, _ = get_open_minute_change(main_quote_data)
            # short_profit = short_profit / tick
            # long_profit = long_profit / tick
            if total_ask_volume != 0 and total_bid_volume != 0:
                # if float(total_bid_volume) / float(
                #         total_ask_volume) > TOTAL_VOLUME_LIMIT_RATIO and ma_volume_ratio > OPEN_VOLUME_MA_LIMIT_RATIO and \
                #                 max_intensity_ask_price > (open_price + LIMIT_INTENSITY_DISTANCE * tick):
                if total_bid_volume - total_ask_volume > 7000:
                    direction = 0
                    close_price = get_close_point(main_quote_data, direction, unit, tick)
                    if close_price != None:
                        long_profit = (close_price - open_price) / tick
                        str_line = instrument_id + ',' + trading_day + ',' + str(total_bid_volume) + ',' + str(
                            total_ask_volume) + ',' + str(ma_volume_ratio) + ',' + str(mean_volume) + ',long,' + str(long_profit) + ',' + str(pre_close_price) + \
                                    "," + str(open_price) + ',' + str(change_ratio) + ',' + str(target_open_price)\
                                   + ',' + str(max_intensity_bid_price) + ',' + str(max_intensity_ask_price) + '\n'
                        f.write(str_line)
                # elif float(total_ask_volume) / float(
                #         total_bid_volume) > TOTAL_VOLUME_LIMIT_RATIO and ma_volume_ratio > OPEN_VOLUME_MA_LIMIT_RATIO and \
                #         max_intensity_bid_price < (open_price - LIMIT_INTENSITY_DISTANCE * tick):
                elif total_ask_volume - total_bid_volume > 7000:
                    direction = 1
                    close_price = get_close_point(main_quote_data, direction, unit, tick)
                    if close_price != None:
                        short_profit = (open_price - close_price) / tick
                        str_line = instrument_id + ',' + trading_day + ',' + str(total_bid_volume) + ',' + str(
                            total_ask_volume) + ',' + str(ma_volume_ratio) + ',' + str(mean_volume) + ',short,' + str(short_profit) + ',' + str(pre_close_price) + \
                        "," + str(open_price) + ',' + str(change_ratio) + ',' + str(target_open_price) \
                                   + ',' + str(max_intensity_bid_price) + ',' + str(max_intensity_ask_price) + '\n'
                        f.write(str_line)
        mbl_quote_file.close()

# 根据成交均价计算的回撤计算平仓点，direction=0代表买，1代表卖
def get_close_point(main_quote_data,direction, unit, tick):
    close_price = None
    turnover_change = main_quote_data.Turnover.diff()
    total_match_volume_change = main_quote_data.Total_Match_Volume.diff()
    average_volume_series = turnover_change / total_match_volume_change / unit / tick
    close_index = 0
    for average_change in average_volume_series.diff():
        if direction == 0:
            if  -20 < average_change < -LIMIT_AVERAGE_CHANGE:
                close_price = main_quote_data.Bid_Price1[close_index]
                break
            else:
                close_index += 1
        elif direction == 1:
            if LIMIT_AVERAGE_CHANGE < average_change < 20:
                close_price = main_quote_data.Ask_Price1[close_index]
                break
            else:
                close_index += 1
    return close_price


def get_accumulative_volume_by_index_price(bid_price_dict, ask_price_dict, open_price, tick, span_num):
    min_bid_price = open_price - span_num * tick
    max_ask_price = open_price + span_num * tick

    accumulativ_bid_volume = 0
    accumulativ_ask_volume = 0

    for price, bid_volume in bid_price_dict.items():
        if price > min_bid_price:
            accumulativ_bid_volume = accumulativ_bid_volume + bid_volume

    for price, ask_volume in ask_price_dict.items():
        if price < max_ask_price:
            accumulativ_ask_volume = accumulativ_ask_volume + ask_volume

    return accumulativ_bid_volume, accumulativ_ask_volume


def get_max_intensity_price(bid_price_dict, ask_price_dict):
    sorted_bid_price_dict = sorted(bid_price_dict.iteritems(), key=lambda d:d[0])
    sorted_ask_price_dict = sorted(ask_price_dict.iteritems(), key=lambda d:d[0])
    max_bid_volume = 0
    max_ask_volume = 0
    max_intensity_bid_price = 0
    max_intensity_ask_price = 0
    arr_len = 10
    bid_price_arr = deque(maxlen=arr_len)
    bid_volume_arr = deque(maxlen=arr_len)
    ask_price_arr = deque(maxlen=arr_len)
    ask_volume_arr = deque(maxlen=arr_len)

    for bid_price, bid_price_volume in sorted_bid_price_dict:
        bid_volume_arr.append(bid_price_volume)
        total_bid_volume = sum(bid_volume_arr)
        bid_price_arr.append(bid_price)
        if total_bid_volume > max_bid_volume:
            average_bid_price = float(sum(list(map(lambda x:x[0]*x[1], zip(bid_volume_arr, bid_price_arr))))) \
                                / float(sum(bid_volume_arr))
            max_intensity_bid_price = average_bid_price
            max_bid_volume = total_bid_volume

    for ask_price, ask_price_volume in sorted_ask_price_dict:
        ask_volume_arr.append(ask_price_volume)
        total_ask_volume = sum(ask_volume_arr)
        ask_price_arr.append(ask_price)
        if total_ask_volume > max_ask_volume:
            average_ask_price = float(sum(list(map(lambda x:x[0]*x[1], zip(ask_volume_arr, ask_price_arr))))) / float(sum(ask_volume_arr))
            max_intensity_ask_price = average_ask_price
            max_ask_volume = total_ask_volume

    return max_intensity_bid_price, max_intensity_ask_price


if __name__ == '__main__':
    result_file_name = "judge_direction_after_auction_total_sep.csv"
    f = open(result_file_name, "wb")
    f.write('instrument_id, trading_day, total_bid_volume, total_ask_volume, ma_volume_ratio, mean_volume, direction, profit,'
             'pre_close_price, open_price, change_ratio, target_open_price, max_intensity_bid_price, max_intensity_ask_price\n')

    trading_day_list = []
    for dirpath, dirnames, filenames in os.walk(source_file_folder):
        for trading_day in dirnames:
            trading_day_list.append(trading_day)

    for trading_day in trading_day_list:
        if  trading_day > "20170901" and trading_day < '20171103':
            day_file_folder = source_file_folder + trading_day + "\\"
            instrument_file_list = get_instrument_file_list(trading_day)
            for son_dir_path, son_dir_names, son_filenames in os.walk(day_file_folder):
                for file_name in son_filenames:
                    if len(file_name) == 10 and file_name[-4:] == '.txt':
                        to_deal_file = day_file_folder + file_name
                        instrument_id = file_name[:-4]
                        variety_id = get_variety_id(instrument_id)
                        print variety_id
                        if variety_id != 'AU':
                            instrument_list = instrument_file_list[variety_id]
                            main_instrument_id, _ = get_main_instrument_id(instrument_list)
                            if instrument_id == main_instrument_id:
                                print_line = file_name[:-4] + " in " + str(trading_day)
                                print print_line
                                judge_direction_after_auction(instrument_id, trading_day)

    f.close()


