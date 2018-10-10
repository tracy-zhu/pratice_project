# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# ，beta和std

@author: Tracy Zhu
"""

# 导入系统库
import sys, time, os
import logging
import shutil

# 导入用户库
sys.path.append("..")
from python_base.plot_method import *

result_file_name = "E:\\rm_m_pairs_trading\\return-1709-5s.xlsx"

result_data = pd.read_excel(result_file_name)

result_positive_return = result_data[result_data["return"] > 0]
result_negative_return = result_data[result_data["return"] < 0]


def get_max_lost_series(result_data):
    max_lost_list = []
    for index in result_data.index:
        max_lost = 0
        trade = result_data.trade[index]
        if trade[-1] == 't':
            max_lost = 1 - result_data['max'][index]
        elif trade[-1] == 'g':
            max_lost = result_data['min'][index] + 1
        max_lost_list.append(max_lost)
    max_lost_series = Series(max_lost_list)
    return max_lost_series

total_max_lost_series = get_max_lost_series(result_negative_return)
total_max_lost_series.hist()
total_max_lost_series.describe()
total_max_lost_series.quantile(0.05)


