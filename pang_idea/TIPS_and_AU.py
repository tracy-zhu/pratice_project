# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 分析黄金和TIPS之间的相关关系
# 采取的数据有1分钟的数据和5分钟的数据

@author: Tracy Zhu
"""

# 导入系统库
import sys, time, os
import statsmodels.formula.api as smf
import scipy.stats as st
import logging
import shutil
from math import log

# 导入用户库
sys.path.append("..")
from python_base.plot_method import *
total_num = 280500

data_file_name = "E:\\quote_data\\pang_data\\tips_au_1min.csv"
result_data = pd.read_csv(data_file_name)
result_data = result_data[:total_num]
result_data = result_data.dropna(how='any')


def linear_model_main_without_intercept(price_series_1, price_series_2):
    X = price_series_2
    result = (sm.OLS(price_series_1, X)).fit()
    # constant_para = result.params.const
    coef_para = result.params.X_data
    Z_data = price_series_1 - price_series_2 * coef_para  # - constant_para
    print(result.summary())
    return Z_data


def get_yield_series(price_series):
    yield_series = price_series.diff() / price_series
    return yield_series


def linear_model_main_with_intercept(price_series_1, price_series_2):
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
    linear_model_dict = {"delta_x_t": delta_x_data.values[(1 + lag_num):duration_num + lag_num],
                         "delta_x_pre_t": delta_x_data.values[1:duration_num],
                         "delta_y_t": delta_y_data.values[(1 + lag_num):duration_num + lag_num],
                         "delta_y_pre_t": delta_y_data.values[1:duration_num],
                         "delta_z_pre_t": delta_z_data.values[1:duration_num]}
    linear_model_dataframe = DataFrame(linear_model_dict)
    mod_x = smf.ols(formula='delta_x_t~delta_x_pre_t + delta_y_pre_t + delta_z_pre_t', data=linear_model_dataframe)
    mod_y = smf.ols(formula='delta_y_t~delta_x_pre_t + delta_y_pre_t + delta_z_pre_t', data=linear_model_dataframe)
    result_x = mod_x.fit()
    result_y = mod_y.fit()
    print(result_x.summary())
    print(result_y.summary())


yield_series_au = get_yield_series(result_data.au)
yield_series_tips = get_yield_series(result_data.TIPS)
yield_series_au = yield_series_au.dropna(how='any')
yield_series_tips = yield_series_tips.dropna(how='any')
price_series_1 = Series(yield_series_au, name='Y_data')
price_series_2 = Series(yield_series_tips, name='X_data')



if __name__ == '__main__':
    price_series_au = result_data.au
    price_series_tips = result_data.bond_yield
    price_series_au = price_series_au.dropna(how='any')
    price_series_tips = price_series_tips.dropna(how='any')
    price_series_1 = Series(price_series_au, name='Y_data')
    price_series_2 = Series(price_series_tips, name='X_data')
    price_series_1 = zscore(price_series_1)
    price_series_2 = zscore(price_series_2)
    Z_data = linear_model_main_with_intercept(price_series_1, price_series_2)