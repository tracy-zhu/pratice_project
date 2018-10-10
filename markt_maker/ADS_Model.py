# -*- coding: utf-8 -*-
"""

# 脚本对ADS模型进行实践研究
# 金融时间序列分析P210-214

Tue 2018/1/15

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from price_prediction.price_prediction_ols import *


def price_change_continuity(instrument_id, trading_day):
    """
    函数计算前一笔价格无变化，下一笔价格变化的条件概率
    和前一笔价格有变化，下一笔价格变化的条件概率
    采取的是用中间价计算
    :param instrument_id:
    :param trading_day:
    :return:
    """
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    middle_price_change = middle_price_series.diff()
    middle_price_shift = middle_price_change.shift()
    consistent_num = 0
    discrete_num = 0
    for index in middle_price_change.index[2:]:
        if middle_price_change[index] != 0 and middle_price_shift[index] != 0:
            consistent_num += 1
        elif middle_price_change[index] != 0 and middle_price_shift[index] == 0:
            discrete_num += 1
    shift_change_num = len(middle_price_shift[middle_price_shift != 0])
    shift_unchange_num = len(middle_price_shift[middle_price_shift == 0])
    print "the probability of P(A=1|B=0) is " + str(float(discrete_num) / float(shift_unchange_num))
    print "the probability of P(A=1|B=1) is " + str(float(consistent_num) / float(shift_change_num))


def direction_change_probability(price_series):
    """
    函数统计上一笔价格变化为0， 变化为正，变化为负，当笔价格变化为正的条件概率
    : price_series 可以为中间价序列，也可以为vwap价格序列
    :return:
    """
    price_change = price_series.diff()
    price_change_shift = price_change.shift()
    pre_unchange_num = 0
    pre_above_num = 0
    pre_below_num = 0
    n = 0
    for index in price_change.index[2:]:
        if price_change[index] > 0 and price_change_shift[index] > 0:
            pre_above_num += 1
        elif price_change[index] > 0 and price_change_shift[index] == 0:
            pre_unchange_num += 1
        elif price_change[index] > 0 and price_change_shift[index] < 0:
            pre_below_num += 1
        elif price_change[index] < 0 and price_change_shift[index] < 0:
            n = n + 1
    unchange_num = len(price_change_shift[price_change_shift==0])
    above_num = len(price_change_shift[price_change_shift>0])
    below_num = len(price_change_shift[price_change_shift<0])
    print "the probability of P(D=1|D=0) is " + str(float(pre_unchange_num)/float(unchange_num))
    print "the probability of P(D=1|D=1) is " + str(float(pre_above_num)/float(above_num))
    print "the probability of P(D=1|D=-1) is " + str(float(pre_below_num)/float(below_num))


def no_trading_ratio_by_lag(instrument_id, trading_day):
    """
    计算不同的lag_num， 无交易占比的比例
    无交易占比有2种， 一种是无交易量，
    另外一种则是价格无变化
    :param instrument_id:
    :param trading_day:
    :return:
    """
    instrument_id = "AG1806"
    trading_day = "20180125"
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    lag_num_list = [1, 5, 10, 20, 30, 60, 120, 240, 360]
    quote_data = read_data(instrument_id, trading_day)
    total_match_volume = quote_data.Total_Match_Volume
    turnover = quote_data.Turnover
    for lag_num in lag_num_list:
        period_match_volume = total_match_volume.diff(lag_num)
        no_trading_num = sum(period_match_volume == 0)
        no_trading_ratio = float(no_trading_num) / float(len(period_match_volume.dropna()))
        print "lag num is " + str(lag_num) + " no trading ratio is " + str(no_trading_ratio)


if __name__ == '__main__':
    instrument_id = "AL1803"
    trading_day = '20180117'
    frequency = "30S"
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    resample_data = get_low_dimension_data(instrument_id, trading_day, frequency)
    vwap_series = get_vwap_series(resample_data, unit)
    direction_change_probability(vwap_series)
