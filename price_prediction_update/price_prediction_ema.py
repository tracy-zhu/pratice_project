# -*- coding: utf-8 -*-
"""

# 该脚本根据李老师的最新文档，首先计算单边MSP,然后根据MSP计算参数

MON 2018/5/7

@author: Tracy Zhu
"""
# 导入系统库
import sys
import itertools
import scipy.stats as st
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# 导入用户库：
sys.path.append("..")
from price_prediction.price_prediction_ols import *


def get_dependent_variable_ema(instrument_id, trading_day):
    """
    生成单笔的MSP的预测，因变量为MSP - mid_price
    MSP就是有下笔的vwap序列生成
    """
    quote_data = read_data(instrument_id, trading_day)
    time_index = get_time_index(quote_data)
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    vwap_series = get_vwap_series(quote_data, unit)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    diff_series = vwap_series - middle_price_series.shift()
    diff_series = Series(diff_series.values, index=time_index)
    dependent_variable = diff_series.shift(-1)
    return dependent_variable


def get_independent_variable_update(instrument_id, trading_day, lag_num):
    """
    更新之后的自变量列表，加入lag——num的因素
    :param instrument_id:
    :param trading_day:
    :param lag_num:
    :return:
    """
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    time_index = get_time_index(quote_data)
    trading_power_difference_arr, _ = lee_ready_algorithm_deform(instrument_id, trading_day)
    trading_power_difference_series = Series(trading_power_difference_arr)
    trading_power_difference_series = trading_power_difference_series.fillna(0)
    trading_power_difference_lag1 = trading_power_difference_series.shift()
    average_price_fillna = get_vwap_series(quote_data, unit)
    vwap_deviation_series = get_vwap_deviation_from_middle_price(quote_data, unit)
    vwap_deviation_lag1 = vwap_deviation_series.shift()
    order_imbalance_series = get_order_balance_series(quote_data)
    order_imbalance_lag1 = order_imbalance_series.shift()
    vwap_momentum_series = get_momentum_factor_vwap(quote_data, unit, 10)
    data = {# variety_id + "_vwap_deviation": vwap_deviation_series.values,
        # variety_id + '_vwap_deviation_lag1': vwap_deviation_lag1.values,
        # variety_id + "_volume_direction": trading_power_difference_series.values,
        variety_id + "_order_imbalance": order_imbalance_series.values,
        # variety_id + "_order_imbalance_lag1": order_imbalance_lag1.values,
        # variety_id + "_volume_direction_lag1": trading_power_difference_lag1.values,
        variety_id + "_vwap_momentum": vwap_momentum_series.values}
    independent_variable_df = DataFrame(data, index=time_index)
    return independent_variable_df


def linear_model_update_ema(instrument_id, trading_day):
    """
    根据改进过后生成的因变量，对预测模型进行回归，得出结论
    :param instrument_id:
    :param trading_day:
    :param forecast_num:
    :return:
    """
    dependent_variable = get_dependent_variable_ema(instrument_id, trading_day)
    independent_variable_df = get_independent_variable_update(instrument_id, trading_day, 1)
    independent_variable_df['dependent_variable'] = dependent_variable
    temp_df = independent_variable_df.dropna(how='any')
    Y = temp_df['dependent_variable']
    X = temp_df.drop('dependent_variable', 1)
    result = (sm.OLS(Y, X)).fit()
    delta_msp = (X * result.params).sum(axis=1)
    quote_data = read_data(instrument_id, trading_day)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    time_index = get_time_index(quote_data)
    middle_price_series = Series(middle_price_series.values, index=time_index)
    msp_series = middle_price_series + delta_msp
    msp_series = msp_series.dropna()
    print result.summary()
    return result.params, msp_series


if __name__ == '__main__':
    trading_date = datetime.now()
    trading_day = trading_date.strftime('%Y%m%d')
    # trading_day = "20180713"
    out_file_folder = "..\\price_prediction_update\\params_folder\\"
    out_file_name = out_file_folder + "prediction_beat1.csv"
    f = open(out_file_name, 'wb')

    instrument_id_group = ["J1809", "JM1809", "RB1810", "RB1901"]
    for dependent_instrument_id in instrument_id_group:
        # dependent_instrument_id = "RB1805"
        print dependent_instrument_id
        forecast_num = 1
        # independent_instrument_list = get_independent_instrument(instrument_id_group, dependent_instrument_id)
        params_series, msp_series = linear_model_update_ema(dependent_instrument_id, trading_day)
        str_line = (',').join(params_series.astype('str')) + '\n'
        f.write(str_line)

    f.close()
