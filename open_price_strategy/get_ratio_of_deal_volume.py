# -*- coding: utf-8 -*-
"""

# 脚本遍历深度行情文件夹，得出三个值
# 得到开盘前最后一笔的三个值
# 成交买单数与报单总买单数之比
# 成交卖单数与报单总卖单数之比
# 平均卖单价格和买单价格之差


Tue 2017/4/18

@author: Tracy Zhu
"""
# 导入系统库
import sys
import logging

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *
sys.path.append("C:\\Users\\Tracy Zhu\\Desktop\\tool\\open_price_strategy")
from open_price_algorithm import *

source_file_folder = "E:\\quote_data\\depth_quote\\"

trading_day_list = []
for dirpath, dirnames, filenames in os. walk(source_file_folder):
    for trading_day in dirnames:
        trading_day_list.append(trading_day)

# 将深度行情文件转化为计算的行情文件
def transfer_depth_quote(to_deal_file, trading_day):
    mbl_quote_file = open(to_deal_file, "r")
    all_lines = mbl_quote_file.readlines()
    mbl_quote_file.close()
    line_total_count = len(all_lines)
    loop_total_count = int(line_total_count / 2)
    variety_id = file_name[:2]
    instrument_id = file_name[:6]
    tick, _, _, = get_variety_information(variety_id)

    logging.info("total line: %d", line_total_count)
    # 一次数据两行，买一行，卖一行
    for i in range(0, loop_total_count - 1):
        first_line = all_lines[i * 2]
        next_line = all_lines[i * 2 + 1]
        buy_price = first_line[:-1].split(",")[2]
        sell_price = next_line[:-1].split(",")[2]
        if buy_price < sell_price:
            buy_line = all_lines[i*2 - 2]
            sell_line = all_lines[i*2 - 1]
            bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(buy_line, sell_line)
            open_price, bid_volume, ask_volume, surplus_bid_volume, surplus_ask_volume = get_open_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
            if len(bid_price_dict.keys()) > 0 and len(ask_price_dict.keys()) > 0:
                average_buy_price = float(sum(bid_price_dict.keys())) / float(len(bid_price_dict.keys()))
                average_ask_price = float(sum(ask_price_dict.keys())) / float(len(ask_price_dict.keys()))
                spread_between_average_price = (average_ask_price - average_buy_price) / tick
                deal_ratio_bid = float(bid_volume) / (float(bid_volume) + float(surplus_bid_volume))
                deal_ratio_ask = float(ask_volume) / (float(ask_volume) + float(surplus_ask_volume))
                each_line = instrument_id + ',' + trading_day + "," + str(deal_ratio_bid) + "," + str(deal_ratio_ask) + "," + str(spread_between_average_price) + '\n'
                out_file.write(each_line)
                break


out_file_name = 'ratio_of_deal_volume.csv'
out_file = open(out_file_name, "wb")
first_line = "instrument_id, trading_day, deal_ratio_bid, deal_ratio_ask, ask_bid_average_spread\n"
out_file.write(first_line)
for trading_day in trading_day_list:
    day_file_folder = source_file_folder + trading_day + "\\"
    for son_dir_path, son_dir_names, son_filenames in os.walk(day_file_folder):
        for file_name in son_filenames:
            if 9 < len(file_name) < 13 and file_name[-4:] == '.txt':
                to_deal_file = day_file_folder + file_name
                print_line = file_name[:-4] + " in " + str(trading_day)
                print print_line
                transfer_depth_quote(to_deal_file, trading_day)

out_file.close()
