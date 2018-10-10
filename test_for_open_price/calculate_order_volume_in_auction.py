# -*- coding: utf-8 -*-
"""

# 本脚本扫描所有的深度行情文件的开盘行情的最后一笔行情
# 计算最后一笔行情买价和卖价在一段价格区间的总挂单量

Mon 2017/11/27

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：：
sys.path.append("..")
from python_base.open_price_algorithm import *
from python_base.get_open_volume_series_instrument import *


variety_id_list = ["RB", "BU", "HC", "RU", "NI"]
source_file_folder = "Q:\\open_auction_depth_quote\\"
limit_order_volume = 500
trading_day_list = get_trading_day_list()
result_file_name = "..\\open_price_strategy\\result\\bid_suspend_order_before_call_auction.csv"
f = open(result_file_name, 'wb')
f.write("instrument_id, trading_day, order_volume, open_volume, direction, order_price, open_price, spread_change_tick\n")


def get_last_line_before_auction(instrument_id, trading_day):
    buy_line = None
    sell_line = None
    to_deal_file = source_file_folder + trading_day + "\\" + instrument_id + '.txt'
    mbl_quote_file = open(to_deal_file, "r")
    all_lines = mbl_quote_file.readlines()
    mbl_quote_file.close()
    line_total_count = len(all_lines)
    loop_total_count = int(line_total_count / 2)
    initial_update_time = all_lines[0][:-1].split(",")[1][:8]
    variety_id = get_variety_id(instrument_id)
    tick, _, _, = get_variety_information(variety_id)
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
    else:
        buy_line = all_lines[-2]
        sell_line = all_lines[-1]
    return buy_line, sell_line


def calc_order_volume_during_period(buy_line, sell_line, start_price, end_price, direction):
    """
    函数计算出集合竞价前最后一笔行情中【start_price, end_price】之间所有的挂单量总和
    :param buy_line:
    :param sell_line:
    :param start_price: 最小价格
    :param end_price: 最大价格
    :param direction: 0 presents buy, 1 presents sell;
    :return: 这一段总共的挂单量
    """
    total_order_volume = 0
    if direction == 0:
        buy_line_list = buy_line.split(",")
        loop_count = len(buy_line_list) / 2
        for i in range(1, loop_count):
            bid_price = float(buy_line_list[2 * i])
            bid_volume = int(buy_line_list[2 * i + 1])
            if start_price <= bid_price <= end_price:
                total_order_volume += bid_volume
        str_line = "the total bid volume between " + str(start_price) + " and " + str(end_price) \
                   + " is " + str(total_order_volume)
        print str_line
    else:
        sell_line_list = sell_line.split(",")
        loop_count = len(sell_line_list) / 2
        for i in range(1, loop_count):
            ask_price = float(sell_line_list[2 * i])
            ask_volume = int(sell_line_list[2 * i + 1])
            if start_price <= ask_price <= end_price:
                total_order_volume += ask_volume
        str_line = "the total ask volume between " + str(start_price) + " and " + str(end_price) \
                   + " is " + str(total_order_volume)
        print str_line


if __name__ == '__main__':
    instrument_id = 'AL1712'
    trading_day = '20171128'
    direction = 1
    start_price = 14030
    end_price = 15640
    buy_line, sell_line = get_last_line_before_auction(instrument_id, trading_day)
    calc_order_volume_during_period(buy_line, sell_line, start_price, end_price, direction)
