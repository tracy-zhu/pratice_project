# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 10:27:52 2016

# 脚本用于对两个合约进行回归分析，并且建立误差修正模型

@author: Tracy Zhu
"""

import os, sys
import logging
import statsmodels.formula.api as smf

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *

# 日志文件
log_file_name = "variety_relation_analyse.log"

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    filename=log_file_name,
                    filemode='w')

# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def get_minute_data(first_instrument_id, second_instrument_id, trading_day):
    first_quote_data = read_minute_data(first_instrument_id, trading_day)
    second_quote_data = read_minute_data(second_instrument_id, trading_day)
    first_last_price_series = Series(first_quote_data.close_price, name='Y_data')
    second_last_price_series = Series(second_quote_data.close_price, name='X_data')
    concat_data_frame = pd.concat([first_last_price_series, second_last_price_series], axis=1)
    concat_data_frame = concat_data_frame.dropna()
    price_series_1 = concat_data_frame.Y_data
    price_series_2 = concat_data_frame.X_data
    return price_series_1, price_series_2


def get_sec_data(first_instrument_id, second_instrument_id, trading_day):
    frequency = '1s'
    first_data = read_data(first_instrument_id, trading_day)
    second_data = read_data(second_instrument_id, trading_day)
    first_resample_data = get_dataframe(first_data, frequency)
    second_resample_data = get_dataframe(second_data, frequency)
    price_series_1 = Series(first_resample_data.Last_Price, name='Y_data')
    price_series_2 = Series(second_resample_data.Last_Price, name='X_data')
    concat_data_frame = pd.concat([price_series_1, price_series_2], axis=1)
    concat_data_frame = concat_data_frame.dropna()
    price_series_1 = concat_data_frame.Y_data
    price_series_2 = concat_data_frame.X_data
    return price_series_1, price_series_2


def linear_model_main(price_series_1, price_series_2):
    X = sm.add_constant(price_series_2)
    result = (sm.OLS(price_series_1, X)).fit()
    constant_para = result.params.const
    coef_para = result.params.X_data
    Z_data = price_series_1 - price_series_2 * coef_para - constant_para
    print(result.summary())
    return Z_data


def ecm_model_main(price_series_1, price_series_2, Z_data, lag_num):
    duration_num = len(price_series_1) - lag_num
    delta_y_data = price_series_1.diff()
    delta_x_data = price_series_2.diff()
    delta_z_data = Z_data.diff()
    linear_model_dict = {}
    linear_model_dict = {"delta_x_t":delta_x_data.values[(1+lag_num):duration_num+lag_num], "delta_x_pre_t":delta_x_data.values[1:duration_num],
                         "delta_y_t":delta_y_data.values[(1+lag_num):duration_num+lag_num], "delta_y_pre_t":delta_y_data.values[1:duration_num],
                         "delta_z_pre_t":delta_z_data.values[1:duration_num]}
    linear_model_dataframe = DataFrame(linear_model_dict)
    mod_x = smf.ols(formula='delta_x_t~delta_x_pre_t + delta_y_pre_t + delta_z_pre_t', data=linear_model_dataframe)
    mod_y = smf.ols(formula='delta_y_t~delta_x_pre_t + delta_y_pre_t + delta_z_pre_t', data=linear_model_dataframe)
    result_x = mod_x.fit()
    result_y = mod_y.fit()
    print(result_x.summary())
    print(result_y.summary())


def judge_if_cointegrated(price_series_1, price_series_2):
    result = sm.tsa.stattools.coint(price_series_1, price_series_2)
    p_value = result[1]
    if p_value < 0.05:
        print "is cointegrated! and p_value is " + str(p_value)
    else:
        print "not cointegrated! and p_value is" + str(p_value)


def plot_price_array(price_series_1, price_series_2):
    plt.plot(price_series_1.values); plt.plot(price_series_2.values)
    plt.ylabel('price')
    plt.legend(['HC1710', 'RB1710'], loc='best')


if __name__ == '__main__':
    trading_day = '20170503'
    first_instrument_id = 'HC1710'
    second_instrument_id = 'RB1710'
    price_series_1, price_series_2 = get_sec_data(first_instrument_id, second_instrument_id, trading_day)
    judge_if_cointegrated(price_series_1, price_series_2)
    Z_data = linear_model_main(price_series_1, price_series_2)
    for lag_num in range(1,10):
        print "lag_num is " + str(lag_num)
        ecm_model_main(price_series_1, price_series_2, Z_data, lag_num)
        
    fig = plt.figure()
    fig.set_size_inches(23.2, 14.0)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(Z_data.values)


