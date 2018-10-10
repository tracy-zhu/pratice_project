# -*- coding: utf-8 -*-
"""

# 本脚本用于计算开盘一分钟比较特殊的情况
# 并计算反方向持有到两个时间节点的利润
# 要将主力和次主力发生错单的情况筛选出去

# 输出一个DataFrame到一个csv中

Tue 2017/3/14

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：：
sys.path.append("..")
from python_base.open_price_algorithm import *
from python_base.get_open_volume_series_instrument import *
open_time = '20:59:00'
duration_time = '21:00:20'
node_1 = '21:05:00'
node_2 = '21:10:00'
limit_change = 0.005
limit_tick_change = 12
limit_spread_tick_change = 8


def get_open_minute_info(main_quote_data):
    node_1_change = 0
    node_2_change = 0
    percent_change = 0
    direction = ''
    open_price = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    duration_quote = main_quote_data[main_quote_data.Update_Time >= open_time]
    duration_quote = duration_quote[duration_quote.Update_Time <= duration_time]
    if len(main_open_quote) > 0:
        open_price = main_open_quote.Last_Price.values[0]
        max_price = duration_quote.Last_Price.max()
        min_price = duration_quote.Last_Price.min()
        percent_change = float(max_price - min_price) / min_price
        node_1_series = main_quote_data[main_quote_data.Update_Time == node_1]
        node_1_price = open_price
        node_2_price = open_price
        if len(node_1_series) > 0:
            node_1_price = node_1_series.Last_Price.values[0]
        else:
            for i in range(1, 10):
                node_12 = node_1[:-1] + str(i)
                if len(main_quote_data[main_quote_data.Update_Time == node_12]) > 0:
                    node_1_price = main_quote_data[main_quote_data.Update_Time == node_12].Last_Price.values[0]
                    break

        node_2_series = main_quote_data[main_quote_data.Update_Time == node_2]
        if len(node_2_series) > 0:
            node_2_price = node_2_series.Last_Price.values[0]
        else:
            for i in range(1, 10):
                node_22 = node_2[:-1] + str(i)
                if len(main_quote_data[main_quote_data.Update_Time == node_22]) > 0:
                    node_2_price = main_quote_data[main_quote_data.Update_Time == node_22].Last_Price.values[0]
                    break
        one_minute_close_price = duration_quote.Last_Price.values[-1]
        if percent_change > limit_change:
            if open_price == max_price:
                direction = 'Fall'
                node_1_change = node_1_price - one_minute_close_price
                node_2_change = node_2_price - one_minute_close_price
            elif open_price == min_price:
                direction = 'Rise'
                node_1_change = one_minute_close_price - node_1_price
                node_2_change = one_minute_close_price - node_2_price
            elif open_price > one_minute_close_price:
                direction = "Fall"
            elif open_price < one_minute_close_price:
                direction = "Rise"

    return percent_change, direction, open_price, node_1_change, node_2_change


def get_open_minute_change(main_quote_data):
    short_profit = 0
    long_profit = 0
    open_price = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    duration_quote = main_quote_data[main_quote_data.Update_Time >= open_time]
    duration_quote = duration_quote[duration_quote.Update_Time <= duration_time]
    if len(main_open_quote) > 0:
        open_price = main_open_quote.Last_Price.values[0]
        max_price = duration_quote.Last_Price.max()
        min_price = duration_quote.Last_Price.min()
        short_profit = open_price - min_price
        long_profit = max_price - open_price
    return short_profit, long_profit, open_price


def get_open_minute_change_except_wrong_order(main_quote_data, sub_quote_data):
    main_open_price = 0
    sub_open_price = 0
    main_node_price = 0
    sub_node_price = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    main_duration_quote = main_quote_data[main_quote_data.Update_Time >= open_time]
    main_duration_quote = main_duration_quote[main_duration_quote.Update_Time <= duration_time]
    if len(main_open_quote) > 0:
        main_open_price = main_duration_quote.Last_Price.values[0]
        main_node_price = main_duration_quote.Last_Price.values[-1]
    sub_open_quote = sub_quote_data[sub_quote_data.Update_Time == open_time]
    sub_duration_quote = sub_quote_data[sub_quote_data.Update_Time >= open_time]
    sub_duration_quote = sub_duration_quote[sub_duration_quote.Update_Time <= duration_time]
    if len(sub_open_quote) > 0:
        sub_open_price = sub_duration_quote.Last_Price.values[0]
        sub_node_price = sub_duration_quote.Last_Price.values[-1]
    main_price_change = abs(main_node_price - main_open_price)
    spread_price_change = abs((main_node_price - sub_node_price) - (main_open_price - sub_open_price))
    return main_price_change, spread_price_change


# 获取集合竞价前查询的最后一笔的变化情况
def get_last_price_change_before_auction(instrument_id, trading_day):
    price_change = 'None'
    last_buy_line = ''
    last_sell_line = ''
    variety_id = get_variety_id(instrument_id)
    tick, _, _ = get_variety_information(variety_id)
    depth_file_root = DEPTH_QUOTE_FILE_ROOT_FILE_FOLDER + trading_day + '\\' + instrument_id + '.txt'
    if os.path.isfile(depth_file_root):
        mbl_quote_file = open(depth_file_root, "r")
        all_lines = mbl_quote_file.readlines()
        line_total_count = len(all_lines)
        loop_total_count = int(line_total_count / 2)
        if line_total_count > 88:
            # 一次数据两行，买一行，卖一行
            for i in range(0, loop_total_count - 1):
                first_line = all_lines[i * 2]
                next_line = all_lines[i * 2 + 1]
                update_time = first_line[:-1].split(",")[1]
                buy_price = float(first_line[:-1].split(",")[2])
                sell_price = float(next_line[:-1].split(",")[2])
                if update_time[:-4] < "20:58:40":
                    last_buy_line = first_line
                    last_sell_line = next_line
                if buy_price < sell_price:
                    buy_line = all_lines[i * 2 - 2]
                    sell_line = all_lines[i * 2 - 1]
                    last_open_price = get_open_price_from_str_line(last_buy_line, last_sell_line)
                    open_price = get_open_price_from_str_line(buy_line, sell_line)
                    price_change = (open_price - last_open_price) / tick
                    break
        mbl_quote_file.close()
        return price_change

# 获取集合竞价比例的三个值1.成交买单数和总买单数之比；2.成交卖单数和总卖单数之比； 3.两个比倍数的较大值
def get_ratio_of_deal_volume(instrument_id, trading_day):
    deal_ratio_bid = 0
    deal_ratio_ask = 0
    ratio_of_bid_ask = 0

    depth_file_root = DEPTH_QUOTE_FILE_ROOT_FILE_FOLDER + trading_day + '\\' + instrument_id + '.txt'
    if os.path.isfile(depth_file_root):
        mbl_quote_file = open(depth_file_root, "r")
        all_lines = mbl_quote_file.readlines()
        mbl_quote_file.close()
        line_total_count = len(all_lines)
        loop_total_count = int(line_total_count / 2)
        variety_id = get_variety_id(instrument_id)
        tick, _, _, = get_variety_information(variety_id)

        # 一次数据两行，买一行，卖一行
        for i in range(0, loop_total_count - 1):
            first_line = all_lines[i * 2]
            next_line = all_lines[i * 2 + 1]
            buy_price = first_line[:-1].split(",")[2]
            sell_price = next_line[:-1].split(",")[2]
            if buy_price < sell_price:
                buy_line = all_lines[i * 2 - 2]
                sell_line = all_lines[i * 2 - 1]
                bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(buy_line, sell_line)
                open_price, bid_volume, ask_volume, surplus_bid_volume, surplus_ask_volume = get_open_price(
                    bid_price_dict, ask_price_dict, max_price, min_price, tick)
                if len(bid_price_dict.keys()) > 0 and len(ask_price_dict.keys()) > 0:
                    average_buy_price = float(sum(bid_price_dict.keys())) / float(len(bid_price_dict.keys()))
                    average_ask_price = float(sum(ask_price_dict.keys())) / float(len(ask_price_dict.keys()))
                    spread_between_average_price = (average_ask_price - average_buy_price) / tick
                    deal_ratio_bid = float(bid_volume) / (float(bid_volume) + float(surplus_bid_volume))
                    deal_ratio_ask = float(ask_volume) / (float(ask_volume) + float(surplus_ask_volume))
                    # ratio_of_bid_ask = max(float(deal_ratio_bid) / float(deal_ratio_ask), float(deal_ratio_ask) / float(deal_ratio_bid))
                    ratio_of_bid_ask = (float(bid_volume) + float(surplus_bid_volume)) / \
                                       (float(ask_volume) + float(surplus_ask_volume))
                    ratio_of_bid_ask_trade_volume = float(bid_volume) / float(ask_volume)
                    break
    return deal_ratio_bid, deal_ratio_ask, ratio_of_bid_ask


def get_open_1minute_info():
    trading_day_list = get_trading_day_list()

    # variety_id_list = ['RU', 'RB', 'NI', 'CU', 'AL', 'ZN', 'BU', 'AG', 'HC', 'MA', 'ZC', 'OI', 'SR']
    variety_id_list = ['RB']

    limit_change = 0.005

    out_file_name = 'F:\\open_price_strategy\\open_volume_series\\open_1minute_info_after_0601_min_close_price.csv'
    f = open(out_file_name, "wb")
    print>>f, "main_instrument_id, trading_day, percent_change, direction, price_change, deal_ratio_bid, deal_ratio_ask, ratio_of_bid_ask_total_volume, open_volume, ma_open_volume, node_1_tick_change, node_2_tick_change"
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day > '20170601':
            print trading_day
            instrument_file_list = get_instrument_file_list(trading_day)
            for (variety_id, instrument_list) in instrument_file_list.items():
                if variety_id in variety_id_list:
                    print variety_id
                    tick, unit, _ = get_variety_information(variety_id)
                    main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
                    if main_instrument_id != None:
                        main_quote_data = read_data(main_instrument_id, trading_day)
                        percent_change, direction, _ , node_1_change, node_2_change = get_open_minute_info(main_quote_data)
                        node_1_tick_change = node_1_change / tick
                        node_2_tick_change = node_2_change / tick
                        if percent_change != 0 and percent_change > limit_change:
                            last_open_volume, mean_volume = get_open_volume_series(main_instrument_id, trading_day)
                            price_change = get_last_price_change_before_auction(main_instrument_id, trading_day)
                            deal_ratio_bid, deal_ratio_ask, ratio_of_bid_ask = get_ratio_of_deal_volume(main_instrument_id, trading_day)
                            print>> f, main_instrument_id, ',', trading_day, ',', percent_change, ',', direction, ",", \
                                price_change, ",", deal_ratio_bid, ",", deal_ratio_ask, ",", ratio_of_bid_ask, ",", \
                                last_open_volume, ',', mean_volume, ',', node_1_tick_change, ',', node_2_tick_change

    f.close()


def out_put_minute_info_to_csv():
    trading_day_list = get_trading_day_list()

    variety_id_list = ['RU', 'RB', 'NI', 'CU', 'AL', 'ZN', 'BU', 'AG', 'HC', "PB" ]
    #variety_id_list = ['RB']

    limit_change = 0.005

    out_file_name = '..\\open_price_strategy\\result\\extreme_change_in_1_5minute_after_open_auction.csv'
    f = open(out_file_name, "wb")
    print>>f, "main_instrument_id, trading_day, tick_change, open_volume, mean_volume"
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day > '20170701':
            print trading_day
            instrument_file_list = get_instrument_file_list(trading_day)
            for (variety_id, instrument_list) in instrument_file_list.items():
                if variety_id in variety_id_list:
                    print variety_id
                    tick, unit, _ = get_variety_information(variety_id)
                    main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
                    if main_instrument_id != None:
                        main_quote_data = read_data(main_instrument_id, trading_day)
                        sub_quote_data = read_data(sub_instrument_id, trading_day)
                        open_volume, mean_volume = get_open_volume_series(main_instrument_id, trading_day)
                        main_price_change, spread_price_change = \
                            get_open_minute_change_except_wrong_order(main_quote_data, sub_quote_data)
                        main_tick_change = main_price_change / tick
                        spread_tick_change = spread_price_change / tick
                        if main_tick_change > limit_tick_change and spread_tick_change < limit_spread_tick_change:
                            str_line = main_instrument_id + ',' + trading_day + ',' + str(main_tick_change) + ','\
                                       + str(open_volume) + "," + str(mean_volume) +"\n"
                            f.write(str_line)
    f.close()


if __name__ == '__main__':
    out_put_minute_info_to_csv()
