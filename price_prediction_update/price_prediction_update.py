# -*- coding: utf-8 -*-
"""

# 脚本结合order imbalance based strategy in HFT这篇论文将原来的回归模型进行改进
# 主要改进以下几个方面，对于预测后面k个周期的价格变化，按照论文给定的公式来计算，为因变量的改变
# 对自变量也做改进，并且增加lag的自变量因素

Tue 2018/2/23

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


def get_dependent_varibale(instrument_id, trading_day, forecast_num):
    """
    根据预测的周期，生成因变量序列，采用的公式为论文中的P9的公式,采用的是未来几段的移动平均值
    由vwap序列生成
    """
    quote_data = read_data(instrument_id, trading_day)
    time_index = get_time_index(quote_data)
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    vwap_series = get_vwap_series(quote_data, unit)
    vwap_arr = np.array(vwap_series)
    vwap_diff_list = [np.nan] * forecast_num
    for i in range(len(vwap_arr) - forecast_num):
        vwap_diff = float(sum(vwap_arr[i+1: i+forecast_num+1])) / float(forecast_num) - vwap_arr[i]
        vwap_diff_list.append(vwap_diff)
    diff_series = Series(vwap_diff_list, index=time_index)
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


def get_independent_variable_ema(instrument_id, trading_day):
    """
    自变量选取该笔行情变化的前一笔作为自变量
    :param instrument_id:
    :param trading_day:
    :param lag_num:
    :return:
    """
    forecast_num = 20
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    time_index = get_time_index(quote_data)
    vwap_series = get_vwap_series(quote_data, unit)
    vwap_arr = np.array(vwap_series)
    vwap_diff_list = [np.nan] * forecast_num
    for i in range(len(vwap_arr) - forecast_num):
        vwap_diff = float(sum(vwap_arr[i+1: i+forecast_num+1])) / float(forecast_num) - vwap_arr[i]
        vwap_diff_list.append(vwap_diff)
    diff_series = Series(vwap_diff_list, index=time_index)
    return diff_series


def linear_model_update(instrument_id, trading_day, forecast_num):
    """
    根据改进过后生成的因变量，对预测模型进行回归，得出结论
    :param instrument_id:
    :param trading_day:
    :param forecast_num:
    :return:
    """
    dependent_variable = get_dependent_varibale(instrument_id, trading_day, forecast_num)
    independent_variable_df = get_independent_variable_update(instrument_id, trading_day, 1)
    independent_variable_df['dependent_variable'] = dependent_variable
    temp_df = independent_variable_df.dropna(how='any')
    Y = temp_df['dependent_variable']
    X = temp_df.drop('dependent_variable', 1)
    result = (sm.OLS(Y, X)).fit()
    print result.summary()
    return result.params


if __name__ == '__main__':
    trading_day = "20180423"
    out_file_folder = "..\\price_prediction_update\\params_folder\\"
    out_file_name = out_file_folder + "prediction.csv"
    f = open(out_file_name, 'wb')

    instrument_id_group = ["RB1805", "RB1810", "JM1809", "J1809"]
    for dependent_instrument_id in instrument_id_group:
        # dependent_instrument_id = "RB1805"
        print dependent_instrument_id
        forecast_num = 1
        # independent_instrument_list = get_independent_instrument(instrument_id_group, dependent_instrument_id)
        params_series = linear_model_update(dependent_instrument_id, trading_day, forecast_num)
        str_line = (',').join(params_series.astype('str')) + '\n'
        f.write(str_line)

    f.close()
