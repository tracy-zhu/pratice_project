# -*- coding: utf-8 -*-
"""

# 该脚本主要针对论文上的改进，对跨品种的预测进行改进

Tue 2018/2/26

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from price_prediction_update import *


def get_independent_instrument(instrument_id_group, dependent_instrument_id):
    independent_instrument_list = instrument_id_group[:]
    independent_instrument_list.remove(dependent_instrument_id)
    return independent_instrument_list


def independent_variable_df_generation_update(instrument_id_group, trading_day):
    instrument_id = instrument_id_group[0]
    instrument_dict = get_independent_dict_instrument(instrument_id, trading_day)
    independent_df = DataFrame(instrument_dict)
    for instrument_id in instrument_id_group[1:]:
        print instrument_id
        instrument_dict = get_independent_dict_instrument(instrument_id, trading_day)
        for independent_name, independent_value in instrument_dict.items():
            print independent_name
            new_independent_value = drop_duplicate_index(independent_value)
            independent_df[independent_name] = new_independent_value
    return independent_df


def get_independent_dict_instrument(instrument_id, trading_day):
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    time_index = get_time_index(quote_data)
    trading_power_difference_arr, _ = lee_ready_algorithm_deform(instrument_id, trading_day)
    trading_power_difference_series_temp = Series(trading_power_difference_arr)
    trading_power_difference_series_temp = trading_power_difference_series_temp.fillna(0)
    trading_power_difference_series = Series(trading_power_difference_series_temp.values, index=time_index)
    trading_power_difference_lag1 = trading_power_difference_series.shift()
    vwap_deviation_series_temp = get_vwap_deviation_from_middle_price(quote_data, unit)
    vwap_deviation_series = Series(vwap_deviation_series_temp.values, index=time_index)
    order_imbalance_temp = get_order_balance_series(quote_data)
    order_imbalance_series = Series(order_imbalance_temp.values, index=time_index)
    order_imbalance_lag1 = order_imbalance_series.shift()
    vwap_momentum_temp = get_momentum_factor_vwap(quote_data, unit, 10)
    vwap_momentum_series = Series(vwap_momentum_temp.values, index=time_index)
    independent_dict = {#instrument_id + "_vwap_deviation": vwap_deviation_series,
            #instrument_id + "_volume_direction": trading_power_difference_series,
            instrument_id + "_order_imbalance": order_imbalance_series,
            instrument_id + "_order_imbalance_lag1": order_imbalance_lag1,
            #instrument_id + "_volume_direction_lag1": trading_power_difference_lag1,
            instrument_id + "_vwap_momentum": vwap_momentum_series}
    # independent_df = DataFrame(independent_dict)
    return independent_dict


def drop_duplicate_index(independent_value):
    """
    将具有重复index的series去掉
    :param independent_value:
    :return:
    """
    duplicate_value = independent_value[independent_value.index.duplicated()]
    new_independent_value = independent_value.drop(duplicate_value.index)
    return new_independent_value


def intercommodity_prediction_update(dependent_instrument_id, instrument_id_group, trading_day, forecast_num):
    dependent_variable = get_dependent_varibale(dependent_instrument_id, trading_day, forecast_num)
    dependent_variable = drop_duplicate_index(dependent_variable)
    independent_df = independent_variable_df_generation_update(instrument_id_group, trading_day)
    independent_df["dependent_variable"] = dependent_variable
    independent_dropna = independent_df.dropna(how='any')
    Y = independent_dropna["dependent_variable"]
    X = independent_dropna.drop('dependent_variable', 1)
    result = (sm.OLS(Y, X)).fit()
    print result.summary()
    return result.params
    # out_file_name = "..\\price_prediction_update\\" + dependent_instrument_id + "_params.csv"
    # f = open(out_file_name, 'wb')
    # print result.params
    # for params_value in result.params:
    #     print>>f, params_value
    # f.close()


if __name__ == '__main__':
    # instrument_id_group = ['AL1805', 'AL1806', 'CU1805', 'CU1806', 'NI1807']
    # dependent_instrument_id = 'AL1805'
    instrument_id_group = ["RB1805", "RB1810", "JM1809", "J1809"]
    for dependent_instrument_id in instrument_id_group:
        # dependent_instrument_id = "RB1805"
        print dependent_instrument_id
        lag_num = 1
        forecast_num = 20
        # independent_instrument_list = get_independent_instrument(instrument_id_group, dependent_instrument_id)
        trading_day = "20180423"
        params_series = intercommodity_prediction_update(dependent_instrument_id, instrument_id_group, trading_day, forecast_num)