# -*- coding: utf-8 -*-
"""

# 本脚本扫描所有的深度行情文件的开盘行情的最后一笔行情
# 将有效挂单大于一个手数的行情找出来
# 输出交易日和合约到一个文件中

# 输出一个DataFrame到一个csv中

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


def find_big_suspend_order_before_call_auction(to_deal_file, instrument_file_list):
    buy_line = None
    sell_line = None
    mbl_quote_file = open(to_deal_file, "r")
    trading_day = to_deal_file.split("\\")[2]
    all_lines = mbl_quote_file.readlines()
    mbl_quote_file.close()
    line_total_count = len(all_lines)
    loop_total_count = int(line_total_count / 2)
    initial_update_time = all_lines[0][:-1].split(",")[1][:8]
    instrument_id = all_lines[0][:-1].split(",")[0]
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

    instrument_list = instrument_file_list[variety_id]
    main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
    main_quote_data = read_data(main_instrument_id, trading_day)
    sub_quote_data = read_data(sub_instrument_id, trading_day)
    spread_change_price = get_open_price_change_from_close_price(main_quote_data, sub_quote_data)
    spread_change_tick = spread_change_price / tick

    bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(buy_line, sell_line)
    auction_open_price, vol_bid, vol_ask, _, _, = get_open_price(bid_price_dict,ask_price_dict,max_price, min_price,tick)
    deal_volume = min(vol_bid, vol_ask)
    if spread_change_tick <= 9:
        if vol_bid > limit_order_volume or vol_ask > limit_order_volume:
            for bid_price, bid_volume in bid_price_dict.items():
                if bid_price >= auction_open_price and bid_volume > limit_order_volume:
                    str_line = instrument_id + "," + trading_day + "," + str(bid_volume) + "," + str(deal_volume) +",buy," + str(bid_price) + ',' \
                               + str(auction_open_price) +  "," + str(spread_change_tick) + '\n'
                    f.write(str_line)

            for ask_price, ask_volume in ask_price_dict.items():
                if ask_price <= auction_open_price and ask_volume > limit_order_volume:
                    str_line = instrument_id + ',' + trading_day + "," + str(ask_volume) + "," + str(deal_volume) +",sell," + str(ask_price) + ',' \
                               + str(auction_open_price) + "," + str(spread_change_tick) + '\n'
                    f.write(str_line)


def get_open_price_change_from_close_price(main_quote_data, sub_quote_data):
    spread_change_price = 100
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    sub_open_quote = sub_quote_data[sub_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0 and len(sub_open_quote) > 0 :
        main_open_price = main_open_quote.Last_Price.values[0]
        sub_open_price = sub_open_quote.Last_Price.values[0]
        main_pre_close_price = main_open_quote.Pre_Close_Price.values[0]
        sub_pre_close_price = sub_open_quote.Pre_Close_Price.values[0]
        pre_close_spread = main_pre_close_price - sub_pre_close_price
        open_price = main_open_price - sub_open_price
        spread_change_price = abs(open_price - pre_close_spread)
    return spread_change_price


for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    if trading_day >= '20170305':
        instrument_file_list = get_instrument_file_list(trading_day)
        day_file_folder = source_file_folder + trading_day + "\\"
        if os.path.exists(day_file_folder):
            print trading_day
            for son_dir_path, son_dir_names, son_filenames in os.walk(day_file_folder):
                for file_name in son_filenames:
                    if 9 < len(file_name) < 12 and file_name[-4:] == '.txt':
                        print file_name
                        variety_id = file_name[:2]
                        if variety_id in variety_id_list:
                            to_deal_file = day_file_folder + file_name
                            find_big_suspend_order_before_call_auction(to_deal_file, instrument_file_list)
f.close()

