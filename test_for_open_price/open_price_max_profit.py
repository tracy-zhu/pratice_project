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


def get_caculater_result(price, times_pass, v_bid_list, v_ask_list, price_re, flag):
    earn = 0
    price_ = 0
    # 挂买单
    if flag == 0:
        volume_bid_list_reason = copy.copy(v_bid_list)
        if volume_bid_list_reason.has_key(price) == True:
            volume_bid_list_reason[price] += times_pass
        else:
            volume_bid_list_reason[price] = times_pass

        # 得到开盘价格
        price_, bid_volume_, ask_volume_, _ , _ = get_open_price(volume_bid_list_reason, v_ask_list, max_price, min_price, tick)

        initial_bid_volume = 0
        for bid_price, bid_volume in v_bid_list.items():
            if bid_price >= price_:
                initial_bid_volume += bid_volume

        volume_delta = ask_volume_ - initial_bid_volume
        if price > price_:
            earn = (price_re - price_) * times_pass
        else:
            if volume_delta >= times_pass:
                max_volume_trade = times_pass
            elif times_pass > volume_delta > 0:
                max_volume_trade = volume_delta
            else:
                max_volume_trade = 0
            earn = (price_re - price_) * max_volume_trade

    # 挂卖单
    elif flag == 1:
        volume_ask_list_reason = copy.copy(v_ask_list)
        if volume_ask_list_reason.has_key(price) == True:
            volume_ask_list_reason[price] += times_pass
        else:
            volume_ask_list_reason[price] = times_pass

        # 得到开盘价格
        price_, bid_volume_, ask_volume_ , _, _= get_open_price(v_bid_list, volume_ask_list_reason, max_price, min_price, tick)

        initial_ask_volume = 0
        for ask_price, ask_volume in v_ask_list.items():
            if ask_price <= price_:
                initial_ask_volume += ask_volume

        volume_delta = bid_volume_ - initial_ask_volume
        if price_pass < price_:
            earn = (price_ - price_re) * times_pass
        else:
            if volume_delta >= times_pass:
                max_volume_trade = times_pass
            elif times_pass > volume_delta > 0:
                max_volume_trade = volume_delta
            else:
                max_volume_trade = 0
            earn = (price_ - price_re) * max_volume_trade

    print earn, price_, times_pass
    return earn, price_, times_pass


if __name__ == '__main__':
    volume_bid_list = {}
    volume_ask_list = {}

    path = os.getcwd()
    instrument_id = "NI1809"

    file_path_name = path + "\\" + instrument_id + ".txt"
    variety_id = get_variety_id(instrument_id)
    tick, _, _ = get_variety_information(variety_id)

    f = open(file_path_name, 'r')

    # 最后一笔集合竞价
    all_lines = f.readlines()

    line_total_count = len(all_lines)
    loop_total_count = int (line_total_count / 2)
    

    # 一次数据两行，买一行，卖一行
    for i in range(0, loop_total_count - 1):
        first_line = all_lines[i * 2]
        next_line = all_lines[i * 2 + 1]
        buy_price = float(first_line[:-1].split(",")[2])
        sell_price = float(next_line[:-1].split(",")[2])
        if buy_price < sell_price:
            data_bid = all_lines[i*2 - 2]
            data_ask = all_lines[i*2 - 1]
            break


    # 得到集合竞价撮合成交那笔行情index
    # print index
    # data_bid = lines[index-2]
    # data_ask = lines[index-1]
    # print data_bid
    # print data_ask

    data_bid_list = data_bid[:-1].split(',')[2:]
    data_ask_list = data_ask[:-1].split(',')[2:]

    len_data_bid = len(data_bid_list)
    bid_price_times = len_data_bid/2
    len_data_ask = len(data_ask_list)
    ask_price_times = len_data_ask/2

    max_price = 0
    min_price = 999999

    for bid_index in range(bid_price_times):
        bid_price  = float(data_bid_list[bid_index*2])
        bid_volume = int(data_bid_list[bid_index*2+1])
        volume_bid_list[bid_price] = bid_volume

        # bid_volume_tot += bid_volume
        # volume_bid_tot_list[bid_price] = bid_volume_tot

        if bid_price > max_price:
            max_price = bid_price
        if bid_price < min_price:
            min_price = bid_price


    # ask_volume_tot = 0
    for ask_index in range(ask_price_times):
        ask_price = float(data_ask_list[ask_index*2])
        ask_volume = int(data_ask_list[ask_index*2+1])
        volume_ask_list[ask_price] = ask_volume

        # ask_volume_tot += ask_volume
        # volume_ask_tot_list[ask_price] = ask_volume_tot

        if ask_price > max_price:
            max_price = ask_price
        if ask_price < min_price:
            min_price = ask_price


    """
    参数修改位置
    """
    # 得到开盘价格
    price_open_reason = get_open_price(volume_bid_list, volume_ask_list, max_price, min_price, tick)[0]
    print '-' * 50
    print u"开盘价格: %s" % str(price_open_reason)

    # 预估合理价格
    price_reason = 107740

    # 最大承载量
    max_volume = 500

    # 间隔
    delta = 10

    ###
    ### 打的手数(两种方式保持一致)
    # times = 100

    # 买卖标志( 0 买, 1 卖)
    flag_ = 1

    # 进场价格
    price_pass = 107740

    volume_bid_list_pass_tot = copy.copy(volume_bid_list)
    volume_ask_list_pass_tot = copy.copy(volume_ask_list)

    max_list = []
    for times in range(1, max_volume, delta):
        earn_, open_price_, volume_ = get_caculater_result(price_pass, times, volume_bid_list_pass_tot, volume_ask_list_pass_tot, price_reason, flag_)

        if len(max_list) == 0:
            max_list.append([price_pass, times, earn_, open_price_])
        elif earn_ > max_list[0][2]:
            max_list[0] = [price_pass, times, earn_, open_price_]

    price_in   = max_list[0][0]
    # 最优的量
    volume_in  = max_list[0][1] - 1
    # 最后开盘价
    open_price_last = max_list[0][3]
    # 最优利润
    earn_last  = max_list[0][2] - abs(open_price_last-price_in)

    print '-' * 50
    print u"盈利状况大的组合为:"
    print u"打入价格: %s, 打入手数: %s手, 打入价格后的开盘价格: %s" %(str(price_in), str(volume_in), str(open_price_last))
    print u"盈利: %s 点" % str(earn_last)


    ###
    ### 按合理价计打价格计算利润
    ###

    # for times in range(1, 200):
    #     # 打的价格
    #     price_pass = 3607
    #     print u"打 %s 手,价格为 %s" % (str(times), str(price_pass))
    #
    #     volume_bid_list_pass_tot = copy.copy(volume_bid_list)
    #     volume_ask_list_pass_tot = copy.copy(volume_ask_list)
    #     earn_, volume_trade, open_price_after = get_caculater_result(price_pass, times, volume_bid_list_pass_tot, volume_ask_list_pass_tot, price_reason,  price_open_reason, flag_)
    #     print '-' * 50
    #
    #     if len(max_list) == 0:
    #         max_list.append([price_pass, times, volume_trade, earn_, open_price_after])
    #     elif earn_ > max_list[0][3]:
    #         max_list[0] = [price_pass, times, volume_trade, earn_, open_price_after]
    #
    #     # 打的价格
    #     price_pass = price_open_reason - point
    #     print u"打 %s 手,价格为 %s" % (str(times), str(price_pass))
    #
    #     earn_, volume_trade, open_price_after = get_caculater_result(price_pass, times, volume_bid_list_pass_tot, volume_ask_list_pass_tot, price_reason, price_open_reason, flag_)
    #
    #     if earn_ > max_list[0][3]:
    #         max_list[0] = [price_pass, times, volume_trade, earn_, open_price_after]
    #
    # price_in   = max_list[0][0]
    # volume_in  = max_list[0][1]
    # volume_tra = max_list[0][2]
    # earn_last  = max_list[0][3]
    # open_price_last = max_list[0][4]
    #
    # print '-' * 50
    # print u"盈利状况大的组合为:"
    # print u"打入价格: %s, 打入手数: %s手, 打入价格后的开盘价格: %s, 成交手数: %s手" %(str(price_in), str(volume_in), str(open_price_last), str(volume_tra))
    # print u"盈利: %s 点" % str(earn_last)
