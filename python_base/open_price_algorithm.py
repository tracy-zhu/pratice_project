# coding: utf-8

import sys
import copy

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *

# 接受买卖量的字典，和最大最小价格，由get_price_volume_dict获得
def get_open_price(volume_bid_list_pas, volume_ask_list_pas, max_price, min_price, tick):
    flag_pass = -1
    volume_bid_list_pass = copy.copy(volume_bid_list_pas)
    volume_ask_list_pass = copy.copy(volume_ask_list_pas)
    if len(volume_ask_list_pass.keys()) == 0 or len(volume_bid_list_pass.keys()) == 0:
        price_open = 0
        vo_bid = 1
        vo_ask = 1
        surplus_vol_bid = 0
        surplus_vol_ask = 0
    else:
        max_bid_price = max(volume_bid_list_pass.keys())
        min_ask_price = min(volume_ask_list_pass.keys())
        if max(volume_bid_list_pass.keys()) < min(volume_ask_list_pass.keys()):
            price_open = (max(volume_bid_list_pass.keys()) + min(volume_ask_list_pass.keys())) / 2
            vo_bid = volume_bid_list_pass[max_bid_price]
            vo_ask = volume_ask_list_pass[min_ask_price]
            surplus_vol_bid = 0
            surplus_vol_ask = 0
        else:
            # 计算开盘价
            price_all = range(int(min_price), int(max_price) + int(tick), int(tick))
            # 补全价格和量的对应
            for price in price_all:
                if volume_bid_list_pass.has_key(price) == False:
                    volume_bid_list_pass[price] = 0
                if volume_ask_list_pass.has_key(price) == False:
                    volume_ask_list_pass[price] = 0

            volume_bid_tot_list = {}
            volume_ask_tot_list = {}
            # 计算买量的合计
            price_all.reverse()
            bid_volume_tot = 0
            for price in price_all:
                bid_volume = volume_bid_list_pass[price]
                bid_volume_tot += bid_volume
                volume_bid_tot_list[price] = bid_volume_tot
            # print volume_bid_tot_list
            # 计算卖量的合计
            price_all.reverse()
            ask_volume_tot = 0
            # print volume_ask_list_pass[3706]
            for price in price_all:
                ask_volume = volume_ask_list_pass[price]
                ask_volume_tot += ask_volume
                volume_ask_tot_list[price] = ask_volume_tot
            # print volume_ask_tot_list

            volume_tot = 0
            price_open = 0
            volume_max_dict = {}
            price_min_volume = {}
            for price in price_all:
                volume_bid_tot = volume_bid_tot_list[price]
                volume_ask_tot = volume_ask_tot_list[price]
                # 取得最大成交量
                volume_tot_jud = min(volume_bid_tot, volume_ask_tot)
                # 卖价买量
                volume_bid = volume_bid_tot_list[price]
                # 买价卖量
                volume_ask = volume_ask_tot_list[price]
                # 最小剩余量
                volume_min = abs(volume_bid - volume_ask)
                price_min_volume[price] = volume_min
                # 最大报单量
                volume_bid_org = volume_bid_list_pass[price]
                volume_ask_org = volume_ask_list_pass[price]
                volume_max = max(volume_bid_org, volume_ask_org)
                volume_max_dict[price] = volume_max
                if volume_tot_jud > volume_tot:
                    volume_tot = volume_tot_jud
                    price_open = price
                elif volume_tot_jud == volume_tot:
                    if volume_tot_jud == 0:
                        continue
                    if volume_min < price_min_volume[price_open]:
                        price_open = price
                    elif volume_min == price_min_volume[price_open]:
                        if volume_max > volume_max_dict[price_open]:
                            price_open = price

            if volume_bid_tot_list.has_key(price_open) and volume_ask_tot_list.has_key(price_open):
                vo_bid = volume_bid_tot_list[price_open]
                vo_ask = volume_ask_tot_list[price_open]
            else:
                vo_bid = 1
                vo_ask = 1

            # 买量逆排序
            volume_bid_tot_list = sorted(volume_bid_tot_list.iteritems(), key=lambda d: d[1], reverse=True)

            # 卖量正排序
            volume_ask_tot_list = sorted(volume_ask_tot_list.iteritems(), key=lambda d: d[1], reverse=False)
            # print u"买价买量"
            # print volume_bid_tot_list
            # print u"卖价卖量"
            # print volume_ask_tot_list
            # print volume_bid_list_pass[price_open]
            # print volume_ask_list_pass[price_open]

            surplus_vol_bid = volume_bid_tot_list[0][1] - vo_bid

            surplus_vol_ask = volume_ask_tot_list[-1][1] - vo_ask

            if flag_pass == 1 and vo_ask > vo_bid:
                for item in volume_ask_tot_list:
                    if item[1] == vo_ask:
                        price_open = item[0]
                        break
            elif flag_pass == 0 and vo_ask < vo_bid:
                for item in volume_bid_tot_list:
                    if item[1] == vo_bid:
                        price_open = item[0]
                        break

        print u"开盘价: %s" % str(price_open), u"买量: %s" % str(vo_bid), u"卖量: %s" % str(vo_ask)
    return price_open, vo_bid, vo_ask, surplus_vol_bid, surplus_vol_ask

# 接受两行字符串，返回get_open_price所需要的字典和最大最小价格
def get_price_volume_dict(buy_line, sell_line):
    buy_item_list = buy_line[:-1].split(",")[2:]
    sell_item_list = sell_line[:-1].split(",")[2:]

    max_price = 0
    min_price = 9999999

    bid_price_dict = dict()
    ask_price_dict = dict()

    for bid_index in range(len(buy_item_list) / 2):
        bid_price = float(buy_item_list[bid_index * 2])
        bid_volume = int(buy_item_list[bid_index * 2 + 1])
        bid_price_dict[bid_price] = bid_volume

        if bid_price > max_price:
            max_price = bid_price
        if bid_price < min_price:
            min_price = bid_price

    for ask_index in range(len(sell_item_list) / 2):
        ask_price = float(sell_item_list[ask_index * 2])
        ask_volume = int(sell_item_list[ask_index * 2 + 1])
        ask_price_dict[ask_price] = ask_volume

        if ask_price > max_price:
            max_price = ask_price
        if ask_price < min_price:
            min_price = ask_price

    return bid_price_dict, ask_price_dict, max_price, min_price

# 接受买行和卖行，得到open_price
def get_open_price_from_str_line(buy_line, sell_line):
    instrument_id = buy_line.split(",")[0]
    variety_id = get_variety_id(instrument_id)
    tick, _, _ = get_variety_information(variety_id)
    bid_price_dict, ask_price_dict, max_price, min_price = get_price_volume_dict(buy_line, sell_line)
    price_open, _, _, _, _ = get_open_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
    return price_open


# 接受一行数据和价格，计算得到优于这个价格总买量和总卖量
def get_accumulative_volume_by_price(buy_line, sell_line, price):
    bid_price_dict, ask_price_dict, _, _ = get_price_volume_dict(buy_line, sell_line)

    accumulative_bid_volume = 0
    accumulative_ask_volume = 0
    for bid_price, bid_volume in bid_price_dict.items():
        if bid_price >= price:
            accumulative_bid_volume += bid_volume

    for ask_price, ask_volume in ask_price_dict.items():
        if ask_price <= price:
            accumulative_ask_volume += ask_volume

    print 'accumulative_bid_volume: ', str(accumulative_bid_volume), 'accumulative_ask_volume: ', str(accumulative_ask_volume)

