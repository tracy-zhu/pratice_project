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

source_file_folder = "E:\\quote_data\\depth_quote\\"
out_file_folder = "E:\\quote_data\\depth_quote_change_each_order\\"
now = datetime.now()
#trading_day = now.strftime('%Y%m%d')

# 将深度行情文件转化为计算的行情文件
def get_last_10_sec_change_before_open_auction(variety_id, to_deal_file, out_file_name):
    mbl_quote_file = open(to_deal_file, "r")
    all_lines = mbl_quote_file.readlines()
    mbl_quote_file.close()
    line_total_count = len(all_lines)
    loop_total_count = int(line_total_count / 2)
    tick, _, _, = get_variety_information(variety_id)

    logging.info("total line: %d", line_total_count)
    # 一次数据两行，买一行，卖一行
    if line_total_count > 80:
        out_file = open(out_file_name, "wb")
        first_line = "update_time, open_price, bid_volume, ask_volume, surplus_bid_volume, surplus_ask_volume\n"
        out_file.write(first_line)
        for i in range(0, loop_total_count - 1):
            next_line = all_lines[i * 2 + 2]
            next_update_time = next_line[:-1].split(",")[1][:8]
            bid_price1 = int(all_lines[i * 2 + 2].split(",")[2])
            ask_price1 = int(all_lines[i * 2 + 3].split(",")[2])
            if bid_price1 < ask_price1:
                break
            if next_update_time > '20:58:49':
                print trading_day, next_update_time
                buy_line = all_lines[i * 2]
                sell_line = all_lines[i * 2 + 1]
                bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(buy_line, sell_line)
                open_price, bid_volume, ask_volume, surplus_bid_volume, surplus_ask_volume = \
                    get_open_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
                next_buy_line = all_lines[i * 2 + 2]
                next_sell_line = all_lines[i * 2 + 3]
                next_bid_price_dict, next_ask_price_dict, next_max_price, next_min_price = \
                    get_price_volume_dict(next_buy_line, next_sell_line)
                next_open_price, next_bid_volume, next_ask_volume, next_surplus_bid_volume, next_surplus_ask_volume =\
                    get_open_price(next_bid_price_dict, next_ask_price_dict, next_max_price, next_min_price, tick)
                logging.info(next_update_time)
                price_change = next_open_price - open_price
                bid_volume_change = next_bid_volume - bid_volume
                ask_volume_change = next_ask_volume - ask_volume
                total_bid_volume_change = next_bid_volume + next_surplus_bid_volume - (bid_volume + surplus_bid_volume)
                total_ask_volume_change = next_ask_volume + next_surplus_ask_volume - (ask_volume + surplus_ask_volume)
                each_line = next_update_time + "," + str(price_change) + "," + str(bid_volume_change) + "," + str(ask_volume_change) + \
                            "," + str(total_bid_volume_change) + "," + str(total_ask_volume_change) + "\n"
                out_file.write(each_line)
        out_file.close()

if __name__ == '__main__':
    trading_day_list = get_trading_day_list()
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day > '20170701':
            day_file_folder = source_file_folder + trading_day + "\\"
            for son_dir_path, son_dir_names, son_filenames in os.walk(day_file_folder):
                for file_name in son_filenames:
                    variety_id = file_name[:2]
                    if 9 < len(file_name) < 12 and file_name[-4:] == '.txt' and file_name[:6] == 'RB1801':
                        to_deal_file = day_file_folder + file_name
                        out_file_name = out_file_folder + file_name[:-4] + trading_day + ".csv"
                        print_line = file_name[:-4] + " in " + str(trading_day)
                        get_last_10_sec_change_before_open_auction(variety_id, to_deal_file, out_file_name)
