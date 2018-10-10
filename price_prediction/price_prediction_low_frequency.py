# -*- coding: utf-8 -*-
"""

# 根据市场有效理论，和没有交易占比比例，确定出数据的降频比例, 首先定为30s的频率级别进行预测；
# 本脚本对于降频数据进行预测，首先采用线性回归的方法

Thu 2018/01/18

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from price_prediction.price_prediction_ols import *
from price_prediction.efficient_market_theory import *


def get_independent_variable_df_low_frequency(instrument_id, trading_day, frequency):
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    resample_data = get_low_dimension_data(instrument_id, trading_day, frequency)
    trading_power_difference_series = trading_power_low_frequency(instrument_id, trading_day, frequency)
    vwap_deviation_series = get_vwap_deviation_from_middle_price(resample_data, unit)
    momentum_vwap = get_momentum_factor_vwap(resample_data, unit)
    order_balance_series = get_order_balance_series(resample_data)
    # data = {"vwap_deviation": vwap_deviation_series.values[3:-1],
    #         "volume_direction": trading_power_difference_series.values[3:-1],
    #         "order_balance": order_balance_series.values[3:-1],
    #         "vwap_momentum": momentum_vwap.values[3:-1]}
    data = {
            "volume_direction": trading_power_difference_series.values[3:-1],
            "vwap_momentum": momentum_vwap.values[3:-1]}
    independent_variable_df = DataFrame(data)
    return independent_variable_df


def condition_win_ratio(independent_variable, dependent_variable, condition_num):
    """
    R^2是整个方程的拟合程度，实际上只需要关注change大于某一个值的正确率，故写了此函数
    条件胜率可以为变化绝对值大于2.5的胜率，或者为变化绝对值大于5的胜率
    计算两种条件胜率，一种为因变量大于condition_num，预测正确的概率
    另外一种为预测值大于condition_num, 预测正确的概率
    :param independent_variable:
    :param dependent_variable:
    :parm condition_num: 代表预测变化的临界值大小
    :return:
    """
    Y = Series(dependent_variable.values[4:])
    X = independent_variable
    #X = sm.add_constant(x)
    result = (sm.OLS(Y, X)).fit()
    prediction_Y = (X * result.params).sum(axis=1)
    concat_data = pd.concat([Y, prediction_Y], axis=1)
    condition_data = concat_data[abs(concat_data[0]) >= condition_num]
    win_series = condition_data[0] * condition_data[1]
    win_ratio = float(sum(win_series>0)) / float(len(win_series))
    print "condition_independent win ratio is " + str(win_ratio)

    condition_data_prediction = concat_data[abs(concat_data[1]) >= condition_num]
    win_series = condition_data_prediction[0] * condition_data_prediction[1]
    win_ratio = float(sum(win_series>0)) / float(len(win_series))
    print "condition_prediction win ratio is " + str(win_ratio)

    win_num = 0
    for index in condition_data_prediction.index:
        value = condition_data_prediction.loc[index][0]
        prediction_value = condition_data_prediction.loc[index][1]
        if abs(prediction_value) > condition_num:
            if abs(value) > 1 and value * prediction_value > 0:
                win_num += 1
    win_ratio = float(win_num) / float(len(condition_data_prediction))
    print "condition_prediction profit win ratio is " + str(win_ratio)
    print "total trading num is " + str(len(condition_data_prediction))


def vwap_series_unchange_ratio(vwap_series_diff):
    unchange_num = len(vwap_series_diff[vwap_series_diff==0])
    unchange_ratio = float(unchange_num) / float(len(vwap_series_diff))
    print "no change ratio is " + str(unchange_ratio)


def correlation_of_last_price_vwap(resample_data, vwap_series):
    X = resample_data.Last_Price.diff().values
    Y = vwap_series.diff().values
    fig, ax = plt.subplots()
    ax.plot(X, Y, label="Last Price", color='r')


def main(instrument_id, trading_day, frequency):
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    resample_data = get_low_dimension_data(instrument_id, trading_day, frequency)
    vwap_series = get_vwap_series(resample_data, unit)
    # middle_price_series = (resample_data.Bid_Price1 + resample_data.Ask_Price1) / 2
    # dependent_variable = middle_price_series.diff()
    dependent_variable = vwap_series.diff()
    vwap_series_unchange_ratio(dependent_variable)
    independent_variable = get_independent_variable_df_low_frequency(instrument_id, trading_day, frequency)
    linear_model_main_prediction(dependent_variable, independent_variable)


if __name__ == '__main__':
    instrument_id = "RB1805"
    frequency = "30S"
    trading_day = "20180131"
    main(instrument_id, trading_day, frequency)

    # for trade_day in trading_day_list:
    #     trading_day = trade_day[:-1]
    #     if trading_day >= "20180110":
    #         print trading_day
    #         main(instrument_id, trading_day, frequency)
