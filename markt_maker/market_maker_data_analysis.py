# -*- coding: utf-8 -*-
"""

# 本脚本分析tick数据，用于做市策略能够更好的盈利

Tue 2017/09/22

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *
trading_day_list = get_trading_day_list()


def get_duration_between_interval(instrument_id, trading_day, interval):
    """
    用于统计在初始买卖价上下interval个tick内上下震动的时长分布
    :param instrument_id:
    :param trading_day:
    :param interval: 在初始买卖价上下多少个tick确定区间
    :return: 返回一个series, 是每个区间震荡的时长序列
    """
    quote_data = read_data(instrument_id, trading_day)
    variety_id = get_variety_id(instrument_id)
    tick, _, _ = get_variety_information(variety_id)
    interval_tick = tick * interval
    duration = 0
    duration_list = []
    lower_bound = 0
    upper_bond = 0
    for index in quote_data.index:
        if '21:05:00' <= quote_data.Update_Time[index] <= '23:59:00' or\
            '09:05:00' <= quote_data.Update_Time[index] <= '14:55:00':
            if lower_bound <= quote_data.Bid_Price1[index] and quote_data.Ask_Price1[index] <= upper_bond:
                duration += 1
            else:
                lower_bound = quote_data.Bid_Price1[index] - interval_tick
                upper_bond = quote_data.Ask_Price1[index] + interval_tick
                duration_list.append(duration)
                duration = 1
    duration_series = Series(duration_list[1:])
    return duration_series


def get_bounce_probability(instrument_id, trading_day, limit_duration, limit_tick):
    """
    统计行情在波动limit_tick下，在limit_duration时刻内回到原来的概率
    回复的定义是bid_price向下跳x个tick，在时长内重新回归到bid_price,ask_price同理
    不能回复的定义是波动方向超过了x个tick, 或者超过时长也不能回复
    :param instrument_id:
    :param trading_day:
    :param limit_duration: 给定能够回复的区间，一般为10个tick的时长
    :param limit_tick: 波动tick区间， 一般为1或者2个tick
    :return: 返回两个结果，10个tick能够回复的概率和回复所需要的时长序列
    """
    quote_data = read_data(instrument_id, trading_day)
    variety_id = get_variety_id(instrument_id)
    tick, _, _ = get_variety_information(variety_id)
    bid_price_diff = quote_data.Bid_Price1.diff() / tick
    index = quote_data.index[0]
    change_times = 0
    success_times = 0
    success_tick_list = []
    while index < quote_data.index[-1]:
        if '21:05:00' <= quote_data.Update_Time[index] <= '23:59:00' or \
                                '09:05:00' <= quote_data.Update_Time[index] <= '14:55:00':
            if bid_price_diff[index] < 0 and abs(bid_price_diff[index]) <= limit_tick:
                change_times += 1
                duration = 1
                initial_bid_price = quote_data.Bid_Price1[index-1]
                while duration <= limit_duration:
                    if quote_data.Bid_Price1[index] != initial_bid_price:
                        index += 1
                        duration += 1
                        if quote_data.Bid_Price1[index] - initial_bid_price < (-2 * tick):
                            break
                    elif quote_data.Bid_Price1[index] == initial_bid_price + tick:
                        index += 1
                        success_times += 1
                        success_tick_list.append(duration)
                        break
            else:
                index += 1
        else:
            index += 1
    bid_win_ratio = float(success_times) / float(change_times)
    bid_success_tick_series = Series(success_tick_list)

    # 计算价格往上走回弹的概率
    ask_price_diff = quote_data.Ask_Price1.diff() / tick
    index = quote_data.index[0]
    ask_change_times = 0
    ask_success_times = 0
    ask_success_tick_list = []
    while index < quote_data.index[-1]:
        if '21:05:00' <= quote_data.Update_Time[index] <= '23:59:00' or \
                                '09:05:00' <= quote_data.Update_Time[index] <= '14:55:00':
            if ask_price_diff[index] > 0 and  abs(bid_price_diff[index]) <= limit_tick:
                ask_change_times += 1
                duration = 1
                initial_ask_price = quote_data.Ask_Price1[index-1]
                while duration <= limit_duration:
                    if quote_data.Ask_Price1[index] != initial_ask_price - tick:
                        index += 1
                        duration += 1
                        if quote_data.Ask_Price1[index] - initial_ask_price > (2 * tick):
                            break
                    elif quote_data.Ask_Price1[index] == initial_ask_price:
                        index += 1
                        ask_success_times += 1
                        ask_success_tick_list.append(duration)
                        break
            else:
                index += 1
        else:
            index += 1
    ask_win_ratio = float(ask_success_times) / float(ask_change_times)
    ask_success_tick_series = Series(ask_success_tick_list)
    print bid_win_ratio, ask_win_ratio
    return bid_win_ratio, bid_success_tick_series, ask_win_ratio, ask_success_tick_series


def get_bounce_time(instrument_id, trading_day, limit_duration):
    """
    函数计算波动一个tick之后，在limit_duration之内多少个tick回归
    期间如果行情继续向不利方向运动， 则不纳入统计，重新计算
    :param instrument_id:
    :param trading_day:
    :param limit_duration: limit_duration是维持时长
    :return: 计算的是向上跳一格的维持时长序列
    """
    quote_data = read_data(instrument_id, trading_day)
    variety_id = get_variety_id(instrument_id)
    tick, _, _ = get_variety_information(variety_id)
    bid_price_diff = quote_data.Bid_Price1.diff() / tick
    index = quote_data.index[0]
    duration_list = []
    zero_duration = 8
    while index < quote_data.index[-1]:
        if '21:05:00' <= quote_data.Update_Time[index] <= '23:59:00' or \
                                '09:05:00' <= quote_data.Update_Time[index] <= '14:55:00':
            if bid_price_diff[index] == 1 and bid_price_diff[index - zero_duration : index - 1].sum() == 0:
                index += 1
                duration = 1
                while bid_price_diff[index] <= 0 and duration <= limit_duration:
                    index += 1
                    duration += 1
                    if bid_price_diff[index] == -1:
                        index += 1
                        duration_list.append(duration)
                        break
            elif bid_price_diff[index] == -1 and bid_price_diff[index - zero_duration : index - 1].sum() == 0:
                index += 1
                duration = 1
                while bid_price_diff[index] >= 0 and duration <= limit_duration:
                    index += 1
                    duration += 1
                    if bid_price_diff[index] == 1:
                        index += 1
                        duration_list.append(duration)
                        break
            else:
                index += 1
        else:
            index += 1
    duration_series = Series(duration_list)
    return duration_series


def plot_cdf_of_duration_tick(bid_success_tick_series, ask_success_tick_series):
    duration_list = range(10, 90)
    bid_cdf_list = []
    ask_cdf_list = []
    for duration in duration_list:
        bid_cdf = float(len(bid_success_tick_series[bid_success_tick_series < duration])) / float(len(bid_success_tick_series))
        ask_cdf = float(len(ask_success_tick_series[ask_success_tick_series < duration])) / float(len(ask_success_tick_series))
        bid_cdf_list.append(bid_cdf)
        ask_cdf_list.append(ask_cdf)
    Series(bid_cdf_list).plot()
    Series(ask_cdf_list).plot()


def pending_order_statistics(delete_variety_list):
    """
    将过去一周每天买卖单挂单量的中位数，形成10天，这10天的中位数,输出到一个csv中
    :param delete_variety_list: 不用考虑的合约列表
    :return: 一个csv
    """
    out_file_name = ".\\markt_maker\\result\\pending_order_statistics.csv"
    f = open(out_file_name, 'wb')
    f.write("variety_id, median_order_volume, mean_volume\n")
    delete_variety_list = ["IF", "IH", "IC", "TF", "T", "SN", "AU", "AG", "WR"]
    median_volume_dict = defaultdict(list)
    start_datetime = datetime.now() - timedelta(days=14)
    start_date = start_datetime.strftime("%Y%m%d")
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day >= start_date:
            instrument_file_list = get_instrument_file_list(trading_day)
            for variety_id, instrument_list in instrument_file_list.items():
                if variety_id not in delete_variety_list:
                    print trading_day, variety_id
                    main_instrument_id, _ = get_main_instrument_id(instrument_list)
                    if main_instrument_id != None:
                        quote_data = read_data(main_instrument_id, trading_day)
                        median_bid_volume = quote_data.Bid_Volume1.median()
                        median_ask_volume = quote_data.Ask_Volume1.median()
                        median_volume = (median_bid_volume + median_ask_volume) / 2
                        match_volume_series = quote_data.Total_Match_Volume.diff()
                        match_volume_series = match_volume_series.dropna()
                        median_match_volume = match_volume_series.mean()
                        median_volume_dict[variety_id].append((median_volume,median_match_volume))

    for variety_id, zip_median_volume_list in median_volume_dict.items():
        unzip_median_volume_list = zip(*zip_median_volume_list)
        median_order_volume = np.mean(unzip_median_volume_list[0])
        match_volume = np.mean(unzip_median_volume_list[1])
        str_line = variety_id + ',' + str(median_order_volume) + ',' + str(match_volume) + '\n'
        f.write(str_line)
    f.close()


if __name__ == '__main__':
    instrument_id = 'AL1711'
    trading_day = '20170921'
    limit_duration = 10
    limit_tick = 1
    # bid_win_ratio, bid_success_tick_series , ask_win_ratio, ask_success_tick_series = \
    #     get_bounce_probability(instrument_id, trading_day, limit_duration, limit_tick)
    # print bid_win_ratio, ask_win_ratio
    duration_list = get_bounce_time(instrument_id, trading_day, limit_duration)


