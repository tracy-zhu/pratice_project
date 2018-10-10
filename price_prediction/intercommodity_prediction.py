# -*- coding: utf-8 -*-
"""

# 本脚本实现跨合约的预测，以一个合约的价格变化为因变量，其他的合约的变化因素为自变量
# 进行回归

Tue 2018/02/01

@author: Tracy Zhu
"""
# 导入系统库
import sys
import itertools
import scipy.stats as st
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# 导入用户库：
sys.path.append("..")
from price_prediction.price_prediction_low_frequency import *

# instrument_id_group = ["AL1803", "AL1804", "ZN1803", "ZN1804", "CU1803", "CU1804"]


def get_independent_instrument(instrument_id_group, dependent_instrument_id):
    independent_instrument_list = instrument_id_group[:]
    independent_instrument_list.remove(dependent_instrument_id)
    return independent_instrument_list


def independent_variable_df_generation(instrument_id_group, trading_day, frequency):
    "这个函数有个问题，没有按照时间戳对齐"
    independent_df = None
    independent_dict = defaultdict()
    for instrument_id in instrument_id_group:
        print instrument_id
        variety_id = get_variety_id(instrument_id)
        tick, unit, _ = get_variety_information(variety_id)
        trading_power_difference_series = trading_power_low_frequency(instrument_id, trading_day, frequency)
        dict_key = instrument_id + "_trading_power"
        independent_dict[dict_key] = trading_power_difference_series
        independent_df = DataFrame(independent_dict)
    return independent_df


def dependent_variable_df(instrument_id, trading_day, frequency):
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    resample_data = get_low_dimension_data(instrument_id, trading_day, frequency)
    vwap_series = get_vwap_series(resample_data, unit)
    dependent_variable = vwap_series.diff().shift(-1)
    return dependent_variable


def intercommodity_prediction(dependent_instrument_id, instrument_id_group, trading_day, frequency):
    dependent_variable = dependent_variable_df(dependent_instrument_id, trading_day, frequency)
    independent_df = independent_variable_df_generation(instrument_id_group, trading_day, frequency)
    independent_df["dependent_variable"] = dependent_variable
    independent_dropna = independent_df.dropna(how='any')
    Y = independent_dropna["dependent_variable"]
    X = independent_dropna.drop('dependent_variable', 1)
    ols_prediction_model(Y, X)


def ols_prediction_model(Y, X):
    result = (sm.OLS(Y, X)).fit()
    print result.summary()


if __name__ == '__main__':
    instrument_id_group = ["RB1805", "HC1805", "I1805", "JM1805", "J1805"]
    dependent_instrument_id = "RB1805"
    frequency = "30S"
    independent_instrument_list = get_independent_instrument(instrument_id_group, dependent_instrument_id)
    trading_day = "20180131"
    intercommodity_prediction(dependent_instrument_id, instrument_id_group, trading_day, frequency)