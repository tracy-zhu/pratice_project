# -*- coding: utf-8 -*-
"""

# 根据之前定位频率30S的预测模型，根据预测大小进行回测
# 回测规则确定如下，按照预测的tick数向下取整，以30s的开始为开仓价，确定是否能够按照预测变化对价平仓出场，否则区间最后阶段平仓出场
# 本脚本还需要确定一个问题，需要多久的回测区间确定参数

Thu 2018/01/23

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from price_prediction.price_prediction_low_frequency import *


def get_prediction_series(instrument_id, trading_day, frequency):
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    resample_data = get_low_dimension_data(instrument_id, trading_day, frequency)
    vwap_series = get_vwap_series(resample_data, unit)
    independent_variable = get_independent_variable_df_low_frequency(instrument_id, trading_day, frequency)
    dependent_variable = vwap_series.diff()
    Y = Series(dependent_variable.values[4:])
    X = independent_variable
    #X = sm.add_constant(x)
    result = (sm.OLS(Y, X)).fit()
    prediction_Y = (X * result.params).sum(axis=1)
    prediction_series = Series(prediction_Y.values, index=resample_data.index[4:])
    return prediction_series


def back_test(instrument_id, trading_day, frequency):
    profit_list = []
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    prediction_series = get_prediction_series(instrument_id, trading_day, frequency)
    quote_data = read_data(instrument_id, trading_day)
    for i in range(len(prediction_series.index)-1):
        index = prediction_series.index[i]
        next_index = prediction_series.index[i+1]
        open_time = str(index).split(" ")[1]
        close_time = str(next_index).split(" ")[1]
        slice_quote = quote_data[quote_data.Update_Time >= open_time]
        slice_quote = slice_quote[slice_quote.Update_Time <= close_time]
        prediction_value = prediction_series[index]
        if abs(prediction_value) > float(tick) * 1.5 :
            prediction_tick = int(prediction_value)
            if prediction_value > 0:
                profit = get_profit(slice_quote, prediction_tick, 1)
            else:
                profit = get_profit(slice_quote, prediction_tick, -1)
            profit_list.append(profit)
    profit_series = Series(profit_list)
    return profit_series


def get_profit(slice_quote, prediction_tick, flag):
    """
    计算在指定区间的盈利利润，由每个区间的开始价格对价开仓，
    若能盈利超过prediction_tick, 盈利平仓，否则在区间的最后阶段平仓
    :param open_price:
    :param prediction_tick: 预期盈利利润
    :param flag: flag = 1, long, flag = -1 short
    :return:
    """
    profit = 0
    if flag == 1:
        open_price = slice_quote.Ask_Price1.values[0]
        for bid_price in slice_quote.Bid_Price1:
            if bid_price >= open_price + prediction_tick:
                profit = bid_price - open_price
                break
        if profit == 0:
            profit  = slice_quote.Bid_Price1.values[-1] - open_price
    elif flag == -1:
        open_price = slice_quote.Bid_Price1.values[0]
        for ask_price in slice_quote.Ask_Price1:
            if ask_price <= open_price - prediction_tick:
                profit = open_price - ask_price
                break
        if profit == 0:
            profit = open_price - slice_quote.Ask_Price1.values[-1]
    return profit

