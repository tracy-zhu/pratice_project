# -*- coding: utf-8 -*-
"""

# 本脚本将深度行情文件的集合竞价计算出来，输出到一个csv文件夹中
# 上期所筛选深度行情数据， 郑商所得出前开盘价

Tue 2017/3/14

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

source_file_folder = "Q:\\open_auction_depth_quote\\"
out_file_folder = "E:\\quote_data\\depth_quote_transfer\\"
now = datetime.now()
trading_day = now.strftime('%Y%m%d')
#trading_day = '20171123'

# 将深度行情文件转化为计算的行情文件
def transfer_depth_quote(to_deal_file, out_file_name):
    mbl_quote_file = open(to_deal_file, "r")
    out_file = open(out_file_name, "wb")
    all_lines = mbl_quote_file.readlines()
    mbl_quote_file.close()
    line_total_count = len(all_lines)
    loop_total_count = int(line_total_count / 2)
    variety_id = file_name[:2]
    tick, _, _, = get_variety_information(variety_id)

    first_line = "update_time, open_price, bid_volume, ask_volume, surplus_bid_volume, surplus_ask_volume\n"
    out_file.write(first_line)
    logging.info("total line: %d", line_total_count)
    # 一次数据两行，买一行，卖一行
    for i in range(0, loop_total_count):
        next_line = all_lines[i * 2]
        next_update_time = next_line[:-1].split(",")[1][:8]
        if next_update_time <= '21:05:00':
            print next_update_time
            buy_line = all_lines[i * 2]
            sell_line = all_lines[i * 2 + 1]
            bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(buy_line, sell_line)
            open_price, bid_volume, ask_volume, surplus_bid_volume, surplus_ask_volume = get_open_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
            logging.info(next_update_time)
            each_line = next_update_time + "," + str(open_price) + "," + str(bid_volume) + "," + str(ask_volume) + \
                        "," + str(surplus_bid_volume) + "," + str(surplus_ask_volume) + "\n"
            out_file.write(each_line)
        if next_update_time > '21:05:00':
            break
    out_file.close()


if __name__ == '__main__':
    day_file_folder = source_file_folder + trading_day + "\\"
    day_out_file_folder = out_file_folder + trading_day + "\\"
    isExists = os.path.exists(day_out_file_folder)
    if not isExists:
        os.makedirs(day_out_file_folder)
    for son_dir_path, son_dir_names, son_filenames in os.walk(day_file_folder):
        for file_name in son_filenames:
            if 9 < len(file_name) < 12 and file_name[-4:] == '.txt' and file_name[:2] != 'AU':
                to_deal_file = day_file_folder + file_name
                out_file_name = day_out_file_folder + file_name[:-3] + "csv"
                print_line = file_name[:-4] + " in " + str(trading_day)
                print print_line
                transfer_depth_quote(to_deal_file, out_file_name)
