# -*- coding: utf-8 -*-
"""

# 脚本对与不同频率的价格序列的有效性进行检验，
    市场越无效，则能够赚钱的机会越多
# 《高频交易》 chapter 不同频率下的市场无效和获利机会

Tue 2018/1/16

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math

# 导入用户库：
sys.path.append("..")
from price_prediction.lee_ready_algorithm import *


def get_run_num(price_series):
    """
    函数用来检验价差差分序列的游程，分别返回的是游程的个数,以及每个游程的长度
    单独一个不构成游程，大于等于2个正负号一样们才算一个游程
    :param price_arr: 价格序列
    :return: run_num 游程个数, run_series: 游程列表, 每个游程的连续次数
    """
    price_diff = np.array(price_series.diff())
    price_change_direction_list = []
    for price_change in price_diff[1:]:
        if price_change > 0:
            price_change_direction_list.append(1)
        elif price_change < 0:
            price_change_direction_list.append(-1)
        else:
            price_change_direction_list.append(0)
    price_change_direction_series = Series(price_change_direction_list)
    price_change_direction_diff = price_change_direction_series.diff()
    run_num = len(price_change_direction_diff[price_change_direction_diff!=0]) + 1
    return run_num


def efficient_by_run_num(price_series):
    """
    根据游程数检验不同价格序列的市场有效性检验
    :param price_series:价格序列，可以是tick级别，分钟级别或者日级别
    :return:
    """
    price_diff = price_series.diff()
    run_num = get_run_num(price_series)
    positive_num = len(price_diff[price_diff > 0])
    negative_num = len(price_diff[price_diff < 0])
    mean_value = float(2* positive_num * negative_num) / float(positive_num + negative_num) + 1
    std_value = math.sqrt(float(2 * positive_num * negative_num * (2 * positive_num * negative_num - positive_num - negative_num))
                          / float((positive_num + negative_num) ** 2 * (positive_num + negative_num - 1)))
    Z_value = float(abs(run_num - mean_value) - 0.5) / float(std_value)
    if Z_value > 1.645:
        print "the price series is inefficient!"
    else:
        print "there is no profit opportunity!"


def ratio_of_constant_price_change(instrument_id, trading_day):
    """
    对于不同阶的差分序列，计算之间间隔价格不变的比例
    :param instrument_id:
    :param trading_day:
    :param diff_num:
    :return:
    """
    #diff_num_list = [1, 30, 60, 120, 240, 360, 480, 600]
    diff_num_list = range(800)
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    constant_ratio_list = []
    for diff_num in diff_num_list:
        middle_price_change = middle_price_series.diff(diff_num)
        constant_price_change_num = len(middle_price_change[middle_price_change==0])
        constant_ratio = float(constant_price_change_num) / float(len(middle_price_change))
        constant_ratio_list.append(1-constant_ratio)
    fig, ax = plt.subplots()
    fig.set_size_inches(23.2, 14.0)
    ax.plot(diff_num_list, constant_ratio_list)

    frequency_list = ["5S", "10S", "15S", "30S", "60S", "90S", "120S"]
    for frequency in frequency_list:
        middle_price_series = get_vwap_price_series_frequency(instrument_id, trading_day, frequency)
        middle_price_change = middle_price_series.diff()
        constant_price_change_num = len(middle_price_change[middle_price_change==0])
        constant_ratio = float(constant_price_change_num) / float(len(middle_price_change))
        print frequency + " , " + str(constant_ratio)


def get_vwap_price_series_frequency(instrument_id, trading_day, frequency):
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    resample_data = get_low_dimension_data(instrument_id, trading_day, frequency)
    # middle_price_series = (resample_data.Bid_Price1 + resample_data.Ask_Price1) / 2
    vwap_series = resample_data.Turnover.diff() / resample_data.Total_Match_Volume.diff() / tick
    no_trading_num = len(vwap_series) - len(vwap_series.dropna())
    no_trading_ratio = float(no_trading_num) / float(len(vwap_series))
    print "no trading ratio is " + str(no_trading_ratio)
    vwap_series = vwap_series.fillna(method="ffill")
    return vwap_series


if __name__ == '__main__':
    instrument_id = "AL1803"
    trading_day = "20180117"
    # frequency = "15S"
    # price_series = get_vwap_price_series_frequency(instrument_id, trading_day, frequency)
    frequency_list = ["5S", "10S", "15S", "30S", "60S", "90S", "120S"]
    for frequency in frequency_list:
        print frequency
        vwap_price_series = get_vwap_price_series_frequency(instrument_id, trading_day, frequency)
        efficient_by_run_num(vwap_price_series)

