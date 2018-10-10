# -*- coding: utf-8 -*-
"""

# 本脚本分析tick数据，几种特征，和价格变化，订单簿，久期，价差，成交量几个因素
# 按照银河证券IF_市场微观结构特征分析

Tue 2017/08/21

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math
import talib as ta
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *
out_file_folder = "..\\markt_maker\\"

now = datetime.now()
trading_day_list = get_trading_day_list()


def get_instrument_std(instrument_id, trading_day):
    quote_data = read_data(instrument_id, trading_day)
    middle_price = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    instrument_std = middle_price.std()
    return instrument_std


def order_book_analysis_from_tick_quote(quote_data):
    bid_volume_series = quote_data.Bid_Volume1
    ask_volume_series = quote_data.Ask_Volume1
    bid_ask_volume_spread_series = bid_volume_series - ask_volume_series
    price_change_series = quote_data.Last_Price.diff()
    order_volume_and_price_change_dict = dict()
    for index in range(len(bid_ask_volume_spread_series) - 1):
        bid_ask_volume_spread = bid_ask_volume_spread_series[index]
        price_change = price_change_series[index + 1]
        if order_volume_and_price_change_dict.has_key(bid_ask_volume_spread):
            pass
        else:
            order_volume_and_price_change_dict[bid_ask_volume_spread] = []
        order_volume_and_price_change_dict[bid_ask_volume_spread].append(price_change)


def order_book_analysis_from_depth_quote(instrument_id, trading_day, depth_level=5, duration=5):
    middle_price_list = []
    bid_volume_list = []
    ask_volume_list = []
    depth_quote_file_name = DEPTH_QUOTE_AFTER_AUCTION_FILE_ROOT_FILE_FOLDER + trading_day + '\\' + instrument_id + '.txt'
    mbl_quote_file = open(depth_quote_file_name, 'r')
    all_lines = mbl_quote_file.readlines()
    mbl_quote_file.close()
    loop_total_count = int(len(all_lines) / 2)

    for i in range(loop_total_count):
        buy_line = all_lines[i * 2]
        sell_line = all_lines[i * 2 + 1]
        incise_num = depth_level * 2 + 2
        buy_line_list = buy_line.split(',')
        sell_line_list = sell_line.split(',')
        buy_line_list = buy_line_list[:incise_num]
        sell_line_list = sell_line_list[:incise_num]
        bid_price1 = float(buy_line_list[2])
        ask_price1 = float(sell_line_list[2])
        middle_price_list.append((bid_price1 + ask_price1) / 2)
        total_bid_volume, total_ask_volume = get_total_match_volume(buy_line_list, sell_line_list, depth_level)
        bid_volume_list.append(total_bid_volume)
        ask_volume_list.append(total_ask_volume)

    price_change_series = Series(middle_price_list).diff(duration)
    bid_ask_volume_spread_series = Series(bid_volume_list) - Series(ask_volume_list)

    order_volume_and_price_change_dict = dict()
    for index in range(len(bid_ask_volume_spread_series) - duration):
        bid_ask_volume_spread = bid_ask_volume_spread_series[index]
        price_change = price_change_series[index + 1]
        if order_volume_and_price_change_dict.has_key(bid_ask_volume_spread):
            pass
        else:
            order_volume_and_price_change_dict[bid_ask_volume_spread] = []
        order_volume_and_price_change_dict[bid_ask_volume_spread].append(price_change)
    order_volume_and_price_change_series = order_volume_and_price_change_dict_analysis(order_volume_and_price_change_dict)
    return order_volume_and_price_change_series


def get_total_match_volume(buy_line_list, sell_line_list, depth_level):
    total_bid_volume = 0
    total_ask_volume = 0
    for i in range(depth_level):
        total_bid_volume += int(buy_line_list[2 * i + 3])
        total_ask_volume += int(sell_line_list[2 * i +3])
    return total_bid_volume, total_ask_volume


def order_volume_and_price_change_dict_analysis(order_volume_and_price_change_dict):
    sorted_dict = sorted(order_volume_and_price_change_dict.iteritems(), key=lambda d:d[0], reverse=True)
    new_dict = dict()
    for volume_key, list_value in sorted_dict:
        mean_value = np.array(list_value).mean()
        new_dict[volume_key] = mean_value
    order_volume_and_price_change_series = Series(new_dict)
    return order_volume_and_price_change_series


def trade_volume_series_analysis(quote_data):
    periods = 5
    last_price_series = quote_data.Last_Price
    total_trade_volume = quote_data.Total_Match_Volume
    trade_volume_series = total_trade_volume.diff(periods)
    last_price_change_series = last_price_series.diff(periods)
    trade_volume_price_dict = dict()
    for trade_volume, last_price_change in zip(trade_volume_series, last_price_change_series):
        if not math.isnan(trade_volume) and not math.isnan(last_price_change):
            if trade_volume_price_dict.has_key(trade_volume):
                break
            else:
                trade_volume_price_dict[trade_volume] = []
            trade_volume_price_dict[trade_volume].append(abs(last_price_change))
    trade_volume_price_series = order_volume_and_price_change_dict_analysis(trade_volume_price_dict)
    return trade_volume_price_series


def duration_of_price(quote_data, tick_range, tick):
    price_range = tick_range * tick
    last_price_series = quote_data.Last_Price
    last_price_change_series = last_price_series.diff()
    duration_list = []
    for i in range(len(last_price_change_series)):
        duration_num = 0
        cum_change_price = last_price_change_series[i]
        while cum_change_price <= price_range:
            duration_num += 1
            if (i + duration_num) >= (len(last_price_change_series) - 1):
                break
            else:
                cum_change_price = cum_change_price + last_price_change_series[i + duration_num]
        duration_list.append(duration_num)
    return duration_list


def duration_of_trade_volume(quote_data, volume_range):
    total_match_volume_series = quote_data.Total_Match_Volume
    trade_volume_series = total_match_volume_series.diff()
    duration_list = []
    for i in range(len(trade_volume_series)):
        duration_num = 0
        cum_trade_volume = trade_volume_series[i]
        while cum_trade_volume <= volume_range:
            duration_num += 1
            if (i + duration_num) >= (len(trade_volume_series) - 1):
                continue
            else:
                cum_trade_volume = cum_trade_volume + trade_volume_series[i + duration_num]
        duration_list.append(duration_num)
    return duration_list


def get_yield_series(instrument_id, trading_day, prediction_period):
    """
    返回三种序列的收益率， 最新价，中间价和成交均价
    :param instrument_id:
    :param trading_day:
    :param prediction_period: 预测区间，计算开始后多期的累计收益率
    :return:last_yield_series, middle_yield_series, deal_yield_series
    """
    quote_data = read_data(instrument_id, trading_day)
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    middle_yield_series = middle_price_series.diff(prediction_period) / middle_price_series.shift(prediction_period)
    last_yield_series = quote_data.Last_Price.diff(prediction_period) / quote_data.Last_Price.shift(prediction_period)
    trade_volume = quote_data.Total_Match_Volume.diff()
    turn_over = quote_data.Turnover.diff()
    deal_price = turn_over / trade_volume / unit
    deal_yield_series = deal_price.diff(prediction_period) / deal_price.shift(prediction_period)
    return last_yield_series, middle_yield_series, deal_yield_series


def get_absolute_tick_change(instrument_id, trading_day, prediction_period):
    quote_data = read_data(instrument_id, trading_day)
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    price_change_arr = np.array(middle_price_series.diff())
    abs_price_change_arr = np.abs(price_change_arr)
    offset_arr = ta.MA(price_change_arr, prediction_period) * prediction_period
    offset_series = Series(offset_arr)
    offset_series = offset_series.dropna() / tick
    distance_arr = ta.MA(abs_price_change_arr, prediction_period) * prediction_period
    distance_series = Series(distance_arr)
    distance_series = distance_series.dropna()
    distance_series = distance_series / tick
    return offset_series, distance_series


def get_kdj_index_array(middle_price_series):
    k, d = ta.STOCH(np.array(middle_price_series), np.array(middle_price_series), np.array(middle_price_series),
                    fastk_period=9, slowk_period=3, slowd_period=3)
    direction_list = [np.nan]
    for i in range(1, len(k)):
        # if k[i-1] < d[i-1] and k[i] > d[i]:
        #     direction = 1
        # elif k[i-1] > d[i-1] and k[i] < d[i]:
        #     direction = -1
        if k[i] < 20 and d[i] < 20:
            direction = -1
        elif k[i] > 80 and d[i] > 80:
            direction = 1
        else:
            direction = 0
        direction_list.append(direction)
    direction_array = np.array(direction_list)
    return direction_array


def get_ema_index_array(middle_price_series, short_period, long_period):
    middle_price_arr = np.array(middle_price_series)
    short_ema = ta.EMA(middle_price_arr, short_period)
    long_ema = ta.EMA(middle_price_arr, long_period)
    index_direction_list = [np.nan]
    for i in range(1, len(middle_price_arr)):
        if short_ema[i] < long_ema[i]:
            direction = 1
        elif short_ema[i] > long_ema[i]:
            direction = -1
        else:
            direction = 0
        index_direction_list.append(direction)
    direction_array = np.array(index_direction_list)
    return direction_array


def get_trade_volume_direction(instrument_id, trading_day, sample_period):
    """
    根据前面一段时期的sample period距离买卖价较近的比例确定方向变量
    统计距离卖价的的占比，占比越高，则代表买量实力越强，占比越低，卖量实力越强
    :param instrument_id:
    :param trading_day:
    :param sample_period: 在这个tick之前取得样本区间长度，10 - 100不等
    :return: 指标序列，代表该指标的涨跌
    """
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    trade_volume = quote_data.Total_Match_Volume.diff()
    turn_over = quote_data.Turnover.diff()
    deal_price = turn_over / trade_volume / unit
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    direction_list = [np.nan] * sample_period
    direction_raw_list = [np.nan] * sample_period
    for i in quote_data.index[sample_period:]:
        rate = 0
        for j in quote_data.index[i-sample_period : i]: # 这里可以到i+1,即最后的一笔行情
            if deal_price[j] > middle_price_series[j]:
                rate += 1
        direction_prob = float(rate) / float(sample_period)
        direction_raw_list.append(direction_prob)
        if direction_prob >= 0.7:
            direction = 1
        elif direction_prob <= 0.4:
            direction = -1
        else:
            direction = 0
        direction_list.append(direction)
    direction_array = np.array(direction_list)
    direction_raw_series = np.array(direction_raw_list)
    return direction_array, direction_raw_series


def get_middle_price_series(instrument_id, trading_day):
    quote_data = read_data(instrument_id, trading_day)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    return middle_price_series


def get_pfe_arr(price_series, period):
    """
    计算位移路程比，位移为变化值的累计求和，路程为变化绝对值的累计求和
    :param price_series:价格序列，是一个Series, 可以是分钟序列，也有可能是tick序列
    :param period:周期长短，可以定义为5,10等
    :return: pfe_arr, 是一个np.array, similar to result of talib
    """
    price_change_arr = np.array(price_series.diff())
    abs_price_change_arr = np.abs(price_change_arr)
    offset_arr = ta.MA(price_change_arr, period) * period
    distance_arr = ta.MA(abs_price_change_arr, period) * period
    pfe_arr = offset_arr / distance_arr
    pfe_arr = np.nan_to_num(pfe_arr)
    return pfe_arr


def get_momentum_index_array(instrument_id, trading_day, sample_period):
    """
    计算前面sample_period个tick的涨幅，如果是涨，则认为未来会涨，否则认为未来会跌
    :param price_series:
    :param sample_period: 回朔样本期
    :return: index_array, 每个tick对应的方向， 看多为1， 看空则为-1， 其余为0
    """
    quote_data = read_data(instrument_id, trading_day)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    price_change_series = middle_price_series.diff(sample_period)
    price_change_series = price_change_series.fillna(0)
    momentum_direction_raw_arr = np.array(price_change_series)
    momentum_direction_list = []
    for price_change in price_change_series:
        direction = 0
        if price_change > 0:
            direction = 1
        elif price_change < 0:
            direction = -1
        momentum_direction_list.append(direction)
    momentum_direction_arr = np.array(momentum_direction_list)
    return momentum_direction_arr, momentum_direction_raw_arr


def get_trade_pending_volume_ratio(instrument_id, trading_day, sample_period):
    """
    得到一个平均成交量除以买卖挂单量的序列，sample_period是取多长时间的平均成交量，取5,10个tick
    :param instrument_id:
    :param trading_day:
    :param sample_period:
    :return: 返回两个序列，一个是成交量比买量序列，一个是成交量比卖量序列
    """
    quote_data = read_data(instrument_id, trading_day)
    trade_volume_series = quote_data.Total_Match_Volume.diff(sample_period) / sample_period
    trade_bid_ratio = quote_data.Bid_Volume1 / trade_volume_series
    trade_ask_ratio = quote_data.Ask_Volume1 / trade_volume_series
    return trade_bid_ratio, trade_ask_ratio


def vix_factor_generation(instrument_id, trading_day, prediction_period, back_period):
    """
    得到收益率的波动率序列，便于研究波动率和行情大小的关系
    :param instrument_id:
    :param trading_day:
    :param prediction_period:
    :param back_period: 波动率的计算
    :return: vix_arr 波动率序列
    """
    # _, middle_yield_series, _ = get_yield_series(instrument_id, trading_day, prediction_period)
    # middle_yield_arr = np.array(middle_yield_series)
    offset_series = get_absolute_tick_change(instrument_id, trading_day, prediction_period)
    offset_arr = np.array(offset_series)
    std_list = [np.nan] * 10
    for i in range(len(offset_arr) - back_period):
        std_value = np.std(offset_arr[i:(i+back_period)])
        std_list.append(std_value)
    std_arr = np.array(std_list)
    return std_arr


def realized_volatility_generation(instrument_id, trading_day, back_period):
    """
    生成已实现波动率，采用tick级别的数据,
    :param instrument_id:
    :param trading_day:
    :param back_period: back_period是回溯周期
    :return: 返回的是一个实现波动率序列
    """
    quote_data = read_data(instrument_id, trading_day)
    last_price_series = quote_data.Last_Price
    yield_series = last_price_series.diff() / last_price_series
    yield_square_arr = np.array(yield_series ** 2)
    realized_volatility_arr = ta.MA(yield_square_arr, back_period)
    realized_volatility_series = Series(realized_volatility_arr)
    realized_volatility_series.plot()


def get_roc_arr(price_series, period):
    pass


def get_index_accuracy(yield_series, index_array, prediction_period):
    """
    将收益率序列都转化为+—1， 判断方向的指标也都转化为+-1
    分别计算两个序列相同的个数和不同的个数
    :param yield_series: 收益率序列, Series
    :param index_array: 指标值序列, 已转化为+-1，0, np.array
    :return: correction_prob, wrong_prob
    """
    yield_series = yield_series.fillna(0)
    yield_trend = []
    for yield_values in yield_series:
        if yield_values > 0:
            num_value = 1
        elif yield_values < 0:
            num_value = -1
        else:
            num_value = 0
        yield_trend.append(num_value)
    yield_trend = Series(yield_trend)
    direction_array = np.array(index_array[1:-prediction_period])
    yield_array = np.array(yield_trend.values[1+prediction_period:])
    cov_array = direction_array * yield_array
    correction_prob = float(len(cov_array[cov_array > 0])) / len(cov_array)
    wrong_prob = float(len(cov_array[cov_array < 0])) / len(cov_array)
    return correction_prob, wrong_prob


def get_index_accuracy_by_pearson(yield_series, index_series, prediction_period):
    """
    跟上一个函数不同，不对收益率序列和方向序列做0,1处理
    而是采用pearson相关系数的模式，相关系数越高，则代表指标的准确性越好
    :param yield_series:
    :param index_array:
    :return: 返回的是两个序列的pearson相关系数
    """
    direction_array = np.array(index_series[1:-prediction_period])
    yield_array = np.array(yield_series.values[1+prediction_period:])
    concat_data_dict = {'index_array': direction_array, 'yield_array': yield_array}
    concat_data_frame = DataFrame(concat_data_dict)
    concat_data_frame = concat_data_frame.dropna()
    direction_array_new = np.array(concat_data_frame.index_array)
    yield_array_new = np.array(concat_data_frame.yield_array)
    cor, pval = st.pearsonr(direction_array_new, yield_array_new)
    return cor


def plot_close_price_trade_volume_one_minute(instrument_id, trading_day):
    """
    画一张双坐标轴， 一边是close_price, 一边是分钟成交量
    :param instrument_id:
    :param trading_day:
    :return: 图形
    """
    minute_data = read_minute_data(instrument_id, trading_day)
    close_price = minute_data['close_price']
    trade_volume = minute_data['trade_volume']

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(close_price.values)
    ax1.set_ylabel('close price')

    ax2 = ax1.twinx()
    ax2.plot(trade_volume.values)
    ax2.set_ylabel('trade volume')
    plt.show()


def get_absolute_price_change_prob(quote_data, prediction_period):
    """
    计算未来几个tick中间价变化为0的概率，两种可能，中间价一直没变过与中间价变过但是又回复过来的
    :param quote_data:
    :param prediction_period:
    :return: constant_prob 中间价变化为0的概率， concat_constant_prob: 除了最后中间价变化为0，中间价格一直没变化的概率
    """
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    price_change_arr = np.array(middle_price_series.diff())
    abs_price_change_arr = np.abs(price_change_arr)
    offset_arr = ta.MA(price_change_arr, prediction_period) * prediction_period
    distance_arr = ta.MA(abs_price_change_arr, prediction_period) * prediction_period
    distance_series = Series(distance_arr)
    distance_series = distance_series.dropna()
    mean_distance = distance_series.mean()
    median_distance = distance_series.median()
    concat_zero_num = 0
    for group in zip(offset_arr, distance_arr):
        if group[0] == 0 and group[1] == 0:
            concat_zero_num += 1
    constant_prob = float(sum(offset_arr == 0)) / len(offset_arr)
    concat_constant_prob = float(concat_zero_num) / len(offset_arr)
    return constant_prob, concat_constant_prob, mean_distance, median_distance


def get_period_match_volume(quote_data, prediction_period):
    """
    计算固定周期的成交量
    """
    period_match_volume = quote_data.Total_Match_Volume.diff(prediction_period)
    period_match_volume = period_match_volume.dropna()
    return period_match_volume


def atr_calculator(instrument_id, trading_day, back_period):
    minute_data = read_minute_data(instrument_id, trading_day)
    minute_open_price = minute_data.open_price.values
    high_price_arr = minute_data.high_price.values
    low_price_arr = minute_data.low_price.values
    atr_arr = \
        ta.ATR(minute_data.high_price.values, low_price_arr, high_price_arr, timeperiod=back_period)
    return atr_arr


def get_atr_arr_five_days(instrument_id, back_period):
    atr_concat_list = []
    trade_volume_concat_list = []
    now = datetime.now()
    trading_day_now = now.strftime('%Y%m%d')
    pre_trading_day = get_pre_trading_day(trading_day_now)
    index_day_time = now - timedelta(days=8)
    index_day = index_day_time.strftime('%Y%m%d')
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if index_day <= trading_day <= pre_trading_day:
            atr_arr = atr_calculator(instrument_id, trading_day, back_period)
            minute_data = read_minute_data(instrument_id, trading_day)
            pfe_arr = get_pfe_arr(minute_data.close_price, back_period)
            trade_volume_list = list(pfe_arr)
            trade_volume_concat_list = trade_volume_concat_list + trade_volume_list
            atr_list = list(atr_arr)
            atr_concat_list = atr_concat_list + atr_list
    atr_concat_series = Series(atr_concat_list)
    atr_concat_series = atr_concat_series.dropna()
    atr_concat_series.describe()
    atr_concat_series.plot()
    concat_list = zip(atr_concat_list,trade_volume_concat_list)
    return concat_list


def atr_performance(instrument_id, trading_day, back_period):
    atr_arr = atr_calculator(instrument_id, trading_day, back_period)
    quote_data = read_minute_data(instrument_id, trading_day)
    price_series = Series(quote_data.close_price.values, index=quote_data.Update_Time)
    atr_series = Series(atr_arr, index=quote_data.Update_Time)
    #concat_series = pd.concat([price_series, atr_series], axis=1)
    out_file_folder = "..\\markt_maker\\picture\\atr_series\\"
    file_name = "atr_value of " + instrument_id + " " + trading_day + " .png"
    out_file_name = out_file_folder + file_name
    fig, ax0 = plt.subplots()
    fig.set_size_inches(23.2, 14.0)
    ax0.plot(price_series.values, color='r')
    ax2 = ax0.twinx()
    ax2.plot(atr_series.values, color='b')
    plt.savefig(out_file_name)


def period_change_analysis(instrument_id, trading_day):
    """
    测试未来几个tick, 行情中间价不变的概率，与中间时间段有变化但是后面有没有变的概率，包括未来几个tick价格变化值的平均距离
    :param instrument_id:
    :param trading_day:
    :return:返回的是一个csv文件，每一行是预测多少个tick，后面则是概率和平均变化值
    """
    trading_day = '20171017'
    instrument_id = 'AL1712'
    quote_data = read_data(instrument_id, trading_day)
    result_file_name2 = '.\\markt_maker\\result\\concat_prob_result.csv'
    result_file2 = open(result_file_name2, 'wb')
    for prediction_period in range(3, 120):
        print prediction_period
        last_yield_series, middle_yield_series, deal_yield_series = get_yield_series(instrument_id, trading_day, prediction_period)
        constant_prob = float(sum(middle_yield_series == 0)) / len(middle_yield_series)
        constant_prob2, concat_constant_prob, mean_distance, median_distance = get_absolute_price_change_prob(quote_data, prediction_period)
        print >> result_file2, prediction_period, ',', constant_prob2, ',', concat_constant_prob, ',', mean_distance, ',', median_distance
    result_file2.close()


def trade_volume_average_price(instrument_id, trading_day, back_period):
    """
    类似于均线的概念，不过计算的是过去一段时间的成交均价
    :param instrument_id:
    :param trading_day:
    :param back_period: 不确定，首先选取1分钟的回朔期，及120个tick, 用图形测试了一下，似乎120,240这个区间比较好。
    :return: vwap_arr
    """
    variety_id = get_variety_id(instrument_id)
    _ , unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    turnover_period = quote_data.Turnover.diff(back_period)
    match_volume_period = quote_data.Total_Match_Volume.diff(back_period)
    vwap_series = turnover_period / match_volume_period / unit
    vwap_arr = vwap_series.values
    return vwap_arr


def vwap_plot(instrument_id, trading_day):
    factor = 1.5
    picture_out_folder = "..\\markt_maker\\picture\\vwap_folder\\"
    quote_data = read_data(instrument_id, trading_day)
    atr_back_period = 14
    atr_arr = atr_calculator(instrument_id, trading_day, atr_back_period)
    minute_data = read_minute_data(instrument_id, trading_day)
    atr_index = []
    for index in minute_data.Update_Time:
        index = index + ":00"
        atr_index.append(index)
    atr_series = Series(atr_arr, index=atr_index)
    concat_dict = {'last_price': quote_data.Last_Price.values, "total_match_volume":quote_data.Total_Match_Volume.values}
    concat_df = DataFrame(concat_dict, index=quote_data.Update_Time)
    concat_df["atr"] = atr_series
    new_atr_series = concat_df["atr"]
    new_atr_series = new_atr_series.fillna(method="ffill")
    new_atr_arr = new_atr_series.values
    last_price_arr = quote_data.Last_Price.values
    vwap_back_period = 240
    vwap_arr = trade_volume_average_price(instrument_id, trading_day, vwap_back_period)
    vwap_upper_arr = vwap_arr + new_atr_arr * factor
    vwap_lower_arr = vwap_arr - new_atr_arr * factor
    fig, ax = plt.subplots()
    fig.set_size_inches(23.2, 14.0)
    ax.plot(last_price_arr, 'r', label="last_price_arr")
    ax.plot(vwap_arr, 'b', label='vwap_arr')
    ax.plot(vwap_upper_arr, 'g', label='vwap_upper_arr')
    ax.plot(vwap_lower_arr, 'y', label='vwap_lower_arr')
    ax.legend(loc="best")
    out_file_name = picture_out_folder + "vwap_arr_picture_of_" + str(back_period) + ".png"
    plt.savefig(out_file_name)


def convariance_of_trade_volume_analysis(instrument_id, trading_day):
    """
    计算价格变化的绝对距离和成交量之间的相关关系，不同tick变化之间
    :param instrument_id:
    :param trading_day:
    :return: 一个csv, 每一行是不同的tick
    """
    instrument_id = 'AL1712'
    trading_day = '20171017'
    quote_data = read_data(instrument_id, trading_day)
    result_file_name = '.\\markt_maker\\result\\convariance_of_trade_volume.csv'
    result_file = open(result_file_name, 'wb')
    for prediction_period in range(15, 120):
        print prediction_period
        period_match_volume = get_period_match_volume(quote_data, prediction_period)
        offset_series, distance_series = get_absolute_tick_change(instrument_id, trading_day, prediction_period)
        cor, pval = st.pearsonr(period_match_volume, distance_series)
        cor2, pval2 = st.pearsonr(period_match_volume, offset_series)
        print>>result_file, prediction_period, ',', distance_series.mean(), ',', cor, ',', offset_series.mean(), ',', cor2
    result_file.close()


def pfe_effect(sample_period, instrument_id, trading_day):
    """
    通过实盘发现，做市商模型比较适合位移较小，路程较大的行情
    换种说法，就是pfe比较小的行情，函数也将这样的函数画出来作比较
    :return:
    """
    quote_data = read_data(instrument_id, trading_day)
    quote_data = quote_data[quote_data.Update_Time >= "09:30:00"]
    quote_data = quote_data[quote_data.Update_Time <= "10:15:00"]
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    price_change_arr = np.array(middle_price_series.diff())
    abs_price_change_arr = np.abs(price_change_arr)
    distance_arr = ta.MA(abs_price_change_arr, sample_period) * sample_period
    pfe_arr = get_pfe_arr(middle_price_series, sample_period)
    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, ncols=1)
    fig.set_size_inches(23.2, 14.0)
    ax0.plot(pfe_arr)
    ax1.plot(middle_price_series)
    ax2.plot(distance_arr)
    path_name = out_file_folder + "picture\\" + trading_day + "\\"
    isExists = os.path.exists(path_name)
    if not isExists:
        os.makedirs(path_name)
    out_file_name = path_name + "pfe_arr_of_sample_period_" + str(sample_period) + ".png"
    plt.savefig(out_file_name)


def correlation_of_different_period():
    trading_day = '20171013'
    #instrument_id = 'SPD MA801&MA805'
    instrument_id = 'AL1712'
    # quote_data = read_data(instrument_id, trading_day)
    # price_series = quote_data.Last_Price
    # price_arr = np.array(price_series)
    # period = 120
    # total_period_num = 600
    # begin_period_num = 8000
    # end_period_num = 12000
    # pfe_arr = get_pfe_arr(price_series, period)
    #
    # # 绘制两张图
    # fig,  (ax0, ax1) = plt.subplots(nrows=2, ncols=1, figsize=(23.2, 14.0))
    # ax0.plot(price_arr[begin_period_num : end_period_num], label='Last Price', color='b')
    # ax1.plot(pfe_arr[begin_period_num : end_period_num], label='PFE_arr', color='r')
    # ax0.legend('upper left')
    # ax1.legend('upper left')
    #
    # # 绘制一张图，双坐标
    # fig, ax3  = plt.subplots()
    # ax3.plot(price_arr[:total_period_num], color='b')
    # ax4 = ax3.twinx()
    # ax4.plot(pfe_arr[:total_period_num], color='r')

    result_file_name = 'deal_price_index_deal_yield_momentum.csv'
    result_file_name2 = 'deal_price_index_last_yield_momentum.csv'
    result_file_name3 = 'pearson_result_deal_yield_momentum.csv'
    result_file_name4 = 'deal_price_index_middle_yield_momentum.csv'
    f = open(result_file_name, 'wb')
    f2 = open(result_file_name2, 'wb')
    f3 = open(result_file_name3, 'wb')
    f4 = open(result_file_name4, 'wb')
    f.write('sample_period, prediction_period, correction_prob\n')
    f2.write('sample_period, prediction_period, correction_prob\n')
    f3.write('sample_period, prediction_period, corrleation\n')
    f4.write('sample_period, prediction_period, correction_prob\n')
    for sample_period in range(3, 60):
        #direction_array, direction_raw_array = get_trade_volume_direction(instrument_id, trading_day, sample_period)
        direction_array, direction_raw_array = get_momentum_index_array(instrument_id, trading_day, sample_period)
        for prediction_period in range(3, 130):
            print sample_period, prediction_period
            last_yield_series, middle_yield_series, deal_yield_series = get_yield_series(instrument_id, trading_day, prediction_period)
            correction_prob, _ = get_index_accuracy(deal_yield_series, direction_array, prediction_period)
            correction_prob2, _ = get_index_accuracy(last_yield_series, direction_array, prediction_period)
            correction_prob3, _ = get_index_accuracy(middle_yield_series, direction_array, prediction_period)
            cor = get_index_accuracy_by_pearson(deal_yield_series, direction_raw_array, prediction_period)
            str_line = str(sample_period) + ',' + str(prediction_period) + ',' + str(correction_prob) + '\n'
            str_line2 = str(sample_period) + ',' + str(prediction_period) + ',' + str(correction_prob2) + '\n'
            str_line3 = str(sample_period) + ',' + str(prediction_period) + ',' + str(cor) + '\n'
            str_line4 = str(sample_period) + ',' + str(prediction_period) + ',' + str(correction_prob3) + '\n'
            f.write(str_line)
            f2.write(str_line2)
            f3.write(str_line3)
            f4.write(str_line4)
    f.close()
    f2.close()
    f3.close()
    f4.close()


def figure_demonstration(instrument_id, trading_day, prediction_period, back_period):
    quote_data = read_data(instrument_id, trading_day)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    std_arr = vix_factor_generation(instrument_id, trading_day, prediction_period, back_period)
    fig,  (ax0, ax1) = plt.subplots(nrows=2, ncols=1, figsize=(23.2, 14.0))
    ax0.plot(middle_price_series, label='spread_arr', color='b')
    ax1.plot(std_arr, label='info_arr', color='r')
    ax0.legend('upper left')
    ax1.legend('upper left')


if __name__ == '__main__':
    instrument_id = 'PB1801'
    back_period = 14
    now = datetime.now()
    trading_day_now = now.strftime('%Y%m%d')
    pre_trading_day = get_pre_trading_day(trading_day_now)
    index_day_time = now - timedelta(days=15)
    index_day = index_day_time.strftime('%Y%m%d')
    # for trade_day in trading_day_list:
    #     trading_day = trade_day[:-1]
    #     if index_day <= trading_day <= pre_trading_day:
    atr_performance(instrument_id, trading_day_now, back_period)

