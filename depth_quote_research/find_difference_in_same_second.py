# -*- coding: utf-8 -*-
"""

# 脚本用于查询深度行情，同1秒中，报单的变化情况

# 可以选取只比较最优档，或者多档行情

Tue 2017/3/14

@author: Tracy Zhu
"""
# 导入系统库
import sys
import logging

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *

Level = 1
DEPTH_QUOTE_FILE_FOLDER = 'E:\\quote_data\\depth_quote_after_auction\\'
DIFFERENT_OUT_FILE_FOLDER = 'E:\\quote_data\\different_depth_quote\\'

def get_update_time(buy_line):
    buy_item_list = buy_line[:-1].split(",")
    update_time = buy_item_list[1]
    return update_time

#主函数，参数 mbl 原始文件
def main_deal_func(instrument_id, trading_day):
    mbl_quote_file_name = DEPTH_QUOTE_FILE_FOLDER + trading_day + "\\" + instrument_id + '.txt'
    out_file_folder = DIFFERENT_OUT_FILE_FOLDER + trading_day + "\\"
    isExists = os.path.exists(out_file_folder)
    if not isExists:
        os.makedirs(out_file_folder)
    out_file_name = out_file_folder + instrument_id + '.txt'
    mbl_quote_file = open(mbl_quote_file_name,"r")
    out_file = open(out_file_name, "wb")
    all_lines = mbl_quote_file.readlines()
    line_total_count = len(all_lines)
    loop_total_count = int (line_total_count / 2)

    logging.info("total line: %d",line_total_count)
    # 一次数据两行，买一行，卖一行
    for i in range(loop_total_count - 1):
        first_bid_line = all_lines[i * 2].split(",")
        first_ask_line = all_lines[i * 2 + 1].split(",")
        next_bid_line = all_lines[i * 2 + 2].split(",")
        next_ask_line = all_lines[i * 2 + 3].split(",")
        update_time = first_bid_line[:-1][1][:8]
        next_update_time = all_lines[i * 2 + 2].split(",")[1][:8]
        print update_time
        if update_time == next_update_time:
            for i in range(Level):
                first_bid_price = first_bid_line[i * 2 + 2]
                first_bid_volume = first_bid_line[i * 2 + 3]
                next_bid_price = next_bid_line[i * 2 + 2]
                next_bid_volume = next_bid_line[i * 2 + 3]
                first_ask_price = first_ask_line[i * 2 + 2]
                first_ask_volume = first_ask_line[i * 2 + 3]
                next_ask_price = next_ask_line[i * 2 + 2]
                next_ask_volume = next_ask_line[i * 2 + 3]
                if first_bid_price != next_bid_price or first_bid_volume != next_bid_volume or\
                    first_ask_price != next_ask_price or first_ask_volume != next_ask_volume:
                    out_file.write(",".join(first_bid_line))
                    out_file.write(",".join(first_ask_line))
                    break

    out_file.close()
    mbl_quote_file.close()

if __name__ == '__main__':
    instrument_id = 'RB1710'
    trading_day = '20170406'
    main_deal_func(instrument_id, trading_day)
