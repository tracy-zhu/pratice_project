# -*- coding: utf-8 -*-
"""

# 本脚本分析tick数据, 验证高频交易模型中的lee&ready算法

Tue 2017/12/13

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *
trading_day_list = get_trading_day_list()


def tick_direction_stat_use_middle_price(instrument_id, trading_day):
    """
    函数统计tick_test算法，统计一天的tick行情中，有多少笔是在上一笔中间价之上（之下），
    有多少笔是在上一笔买卖价之外
    :param instrument_id:
    :param trading_day:
    :return:
    """
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    average_price = quote_data.Turnover.diff() / quote_data.Total_Match_Volume.diff() / unit
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    # average_tick_offset = (average_price - middle_price_series) / tick
    middle_price_shift = middle_price_series.shift(1)
    bid_price_shift = quote_data.Bid_Price1.shift(1)
    ask_price_shift = quote_data.Ask_Price1.shift(1)
    up_list = 0
    up_2_list = 0
    down_list = 0
    down_2_list = 0
    up_tick_list = []
    down_tick_list = []
    for index in average_price.index:
        if average_price[index] > middle_price_shift[index]:
            up_list += 1
            if average_price[index] > ask_price_shift[index]:
                up_2_list += 1
                up_tick = middle_price_series[index + 1] - middle_price_series[index]
                up_tick_list.append(up_tick/tick)
        elif average_price[index] < middle_price_shift[index]:
            down_list += 1
            if average_price[index] < bid_price_shift[index]:
                down_2_list += 1
                down_tick = middle_price_series[index + 1] - middle_price_series[index]
                down_tick_list.append(down_tick/tick)
    mean_up_tick = np.mean(up_tick_list)
    mean_down_tick = np.mean(down_tick_list)
    str_line = "the up tick num is " + str(up_list) + "\nthe up 2 tick num is " + str(up_2_list) + \
               "\nthe down tick num is " + str(down_list) + "\nthe down 2 tick num is " + str(down_2_list) +\
               "\nmean up tick is " + str(mean_up_tick) + "\nmean down tick is " + str(mean_down_tick)
    print str_line


def tick_direction_stat_use_trade_price(instrument_id, trading_day):
    """
    应用tick_test算法，采取的是应用trade_price, 并且相对于上一笔，相差超过一个
    tick才纳入统计
    :param instrument_id:
    :param trading_day:
    :return:
    """
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    average_price = quote_data.Turnover.diff() / quote_data.Total_Match_Volume.diff() / unit
    average_price_diff = average_price.diff() / tick
    up_tick_series = average_price_diff[average_price_diff > 1]
    down_tick_series = average_price_diff[average_price_diff < -1]
    str_line = "total trade tick num is " + str(len(quote_data)) + "\nup tick num is " + \
               str(len(up_tick_series)) + "\ndown tick num is " + str(len(down_tick_series))
    print str_line


def lee_ready_algorithm_deform(instrument_id, trading_day):
    """
    改进的lee_ready算法，当价格有波动的时候，则按照价格波动的方向确定成交量的方向
    如果价格没有波动，则按照方程解出成交在bid上的价格和成交在ask的价格
    成交量方向买为1， 卖为-1
    :param instrument_id:
    :param trading_day:
    :return: 每个tick得到一个Qt = direction * trade_volume, 返回的结果是Qt_list
    """
    tick_change_dict = defaultdict(list)
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    trading_power_difference_list = [np.nan]
    quote_data = read_data(instrument_id, trading_day)
    tick_match_volume = quote_data.Total_Match_Volume.diff() / 2
    tick_turnover = quote_data.Turnover.diff()
    # average_price = quote_data.Turnover.diff() / quote_data.Total_Match_Volume.diff() / unit
    # average_price_diff = average_price.diff() / tick
    for index in quote_data.index[:-1]:
        trading_power_difference = np.nan
        first_bid_price = quote_data.Bid_Price1[index]
        first_ask_price = quote_data.Ask_Price1[index]
        next_bid_price = quote_data.Bid_Price1[index + 1]
        next_ask_price = quote_data.Ask_Price1[index + 1]
        if first_bid_price == next_bid_price and first_ask_price == next_ask_price:
            volume_bid = (tick_turnover[index + 1] / unit - first_ask_price * tick_match_volume[index + 1] * 2) / \
                         (first_bid_price - first_ask_price) / 2
            volume_ask = (tick_turnover[index + 1] / unit - first_bid_price * tick_match_volume[index + 1] * 2) / \
                         (first_ask_price - first_bid_price) / 2
            trading_power_difference = 1 * volume_ask - 1 * volume_bid
        elif next_ask_price > first_ask_price:
            trading_power_difference = 1 * tick_match_volume[index + 1]
        elif next_bid_price < first_bid_price:
            trading_power_difference = -1 * tick_match_volume[index + 1]
        elif first_bid_price == next_bid_price and next_ask_price < first_ask_price:
            trading_power_difference = -1 * tick_match_volume[index + 1]
        elif first_ask_price == next_ask_price and next_bid_price > first_bid_price:
            trading_power_difference = 1 * tick_match_volume[index + 1]
        #tick_change_dict[trading_power_difference].append(average_price_diff[index+2])
        trading_power_difference_list.append(trading_power_difference)
    trading_power_difference_arr = np.array(trading_power_difference_list)
    return trading_power_difference_arr, tick_change_dict


def trading_power_low_frequency(instrument_id, trading_day, frequency):
    trading_power_difference_arr, _ = lee_ready_algorithm_deform(instrument_id, trading_day)
    pre_trading_day = get_pre_trading_day(trading_day)
    data = read_data(instrument_id, trading_day)
    Update_Millisec_str = []
    stamp_index = []
    trading_day_list = []
    data = data.dropna(subset=['Update_Time'], how='any')
    for values in data.Update_Millisec:
        str_values = str(values).zfill(3)
        Update_Millisec_str.append(str_values)
    for update_time in data.Update_Time:
        if int(update_time.split(":")[0]) > 15:
            trading_day_list.append(str(int(pre_trading_day)))
        else:
            trading_day_list.append(str(int(trading_day)))
    time_index = data.Update_Time + "." + Update_Millisec_str + " " + trading_day_list
    for temp_time in time_index:
        stamp = datetime.strptime(temp_time, '%H:%M:%S.%f %Y%m%d')
        stamp_index.append(stamp)
    trading_power_difference_series = Series(trading_power_difference_arr, index=stamp_index)
    trading_power_difference_series = trading_power_difference_series.fillna(0)
    down_sample_trading_power_difference = trading_power_difference_series.resample(frequency).sum()
    down_sample_trading_power_difference = down_sample_trading_power_difference.dropna()
    return down_sample_trading_power_difference


def get_data_frame_with_power_difference(data, trading_power_difference_arr):
    Update_Millisec_str = []
    stamp_index = []
    data = data.dropna(subset=['Update_Time'], how='any')
    for values in data.Update_Millisec:
        str_values = str(values).zfill(3)
        Update_Millisec_str.append(str_values)
    time_index = data.Update_Time + "." + Update_Millisec_str
    for temp_time in time_index:
        stamp = datetime.strptime(temp_time, '%H:%M:%S.%f')
        stamp_index.append(stamp)
    trading_power_difference_series = Series(trading_power_difference_arr, index=stamp_index)
    DF_data = DataFrame(data.values, index=stamp_index, columns=G_TICK_COLUMNS)
    night_resample_data = DF_data[DF_data.index >= datetime(1900,1,1,21,0,0)]
    day_resample_data = DF_data[DF_data.index < datetime(1900,1,1,21,0,0)]
    concat_resample_data = pd.concat([night_resample_data, day_resample_data])
    concat_resample_data["trading_power_difference"] = trading_power_difference_series
    return concat_resample_data


def trade_volume_classfication(instrument_id, trading_day):
    """
    创造出一种算法，将每个tick的成交者分成以下三种情况：
    1. 成交在ask上的成交量
    2. 成交在bid上的成交量
    3. 不能分清楚的成交量，上述两种成交量加起来不满当笔tick总成交量的量
    :param instrument_id:
    :param trading_day:
    :return: 三种成交量序列
    """
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    trade_bid_volume_list = []
    trade_ask_volume_list = []
    trade_undefined_volume_list = []
    tick_match_volume = quote_data.Total_Match_Volume.diff() / 2
    for index in quote_data.index[:-1]:
        trade_bid_volume = 0
        trade_ask_volume = 0
        trade_undefined_volume = 0
        first_bid_price = quote_data.Bid_Price1[index]
        first_ask_price = quote_data.Ask_Price1[index]
        next_bid_price = quote_data.Bid_Price1[index + 1]
        next_ask_price = quote_data.Ask_Price1[index + 1]
        first_bid_volume = quote_data.Bid_Volume1[index]
        first_ask_volume = quote_data.Ask_Volume1[index]
        next_bid_volume = quote_data.Bid_Volume1[index + 1]
        next_ask_volume = quote_data.Ask_Volume1[index + 1]
        if first_bid_price == next_bid_price and first_ask_price == next_ask_price:
            trade_bid_volume = first_bid_volume - next_bid_volume
            trade_ask_volume = first_ask_volume - next_ask_volume
            trade_undefined_volume = tick_match_volume[index + 1] - trade_bid_volume - trade_ask_volume
        elif next_bid_price == first_ask_price:
            trade_ask_volume = first_ask_volume - next_bid_volume
            trade_bid_volume = 0
            trade_undefined_volume = tick_match_volume[index + 1] - trade_bid_volume - trade_ask_volume
        elif next_ask_price == first_bid_price:
            trade_bid_volume = first_bid_volume - next_ask_volume
            trade_ask_volume = 0
            trade_undefined_volume = tick_match_volume[index + 1] - trade_bid_volume - trade_ask_volume
        elif next_bid_price > first_ask_price:
            trade_ask_volume = tick_match_volume[index + 1]
            trade_bid_volume = 0
            trade_undefined_volume = 0
        trade_bid_volume_list.append(trade_bid_volume)
        trade_ask_volume_list.append(trade_ask_volume)
        trade_undefined_volume_list.append(trade_undefined_volume)
    trade_bid_volume_series = Series(trade_bid_volume_list)
    trade_ask_volume_series = Series(trade_ask_volume_list)
    trade_undefined_volume_series = Series(trade_undefined_volume_list)
    return trade_ask_volume_series, trade_bid_volume_series, trade_undefined_volume_series


def find_tick_unchange_ratio(instrument_id, trading_day):
    """
    找出tick之间价格没有变化的比例，包括middle_price, last_price的变化
    :param instrument_id:
    :param trading_day:
    :return:
    """
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    last_price_diff = quote_data.Last_Price.diff()
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    middle_price_diff = middle_price_series.diff()
    last_price_unchange_ratio = float(len(last_price_diff[last_price_diff==0])) / len(last_price_diff)
    middle_price_unchange_ratio = float(len(middle_price_diff[middle_price_diff==0])) / len(last_price_diff)
    print "last price unchange ratio is " + str(last_price_unchange_ratio)
    print "middle price unchange ratio is " + str(middle_price_unchange_ratio)
    middle_price_unchange = middle_price_diff[middle_price_diff==0]
    return middle_price_unchange.index


if __name__ == '__main__':
    instrument_id = "AL1802"
    trading_day = "20171227"
    # tick_direction_stat_use_trade_price(instrument_id, trading_day)
    # trade_ask_series, trade_bid_series, trade_undefined_series = trade_volume_classfication(instrument_id, trading_day)
    trading_power_difference_arr, tick_change_dict = lee_ready_algorithm_deform(instrument_id, trading_day)
    trading_power_difference_series = Series(trading_power_difference_arr)
    # tick_change_sorted_list = [(x, tick_change_dict[x]) for x in sorted(tick_change_dict.keys())]
    # trading_power_list = []
    # tick_change_list = []
    # for tick_tuple in tick_change_sorted_list:
    #     trading_power_list.append(tick_tuple[0])
    #     tick_change_list.append(np.mean(tick_tuple[1]))
    # fig, ax1 = plt.subplots()
    # ax1.plot(trading_power_list, tick_change_list)
    quote_data = read_data(instrument_id, trading_day)
    concat_data_frame = get_data_frame_with_power_difference(quote_data, trading_power_difference_arr)
    fig, ax1 = plt.subplots()
    ax1.plot(trading_power_difference_arr, label="trading_power_difference", color='r')
    ax2 = ax1.twinx()
    ax2.plot(quote_data.Last_Price.values, label="last_price", color='b')
    ax1.legend(loc="best")
    ax2.legend(loc='best')

