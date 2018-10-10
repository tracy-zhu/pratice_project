# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 该脚本用于外盘的变化对集合竞价的影响
# 选取一个合约和交易日期，能对其开盘价的变化和外盘价格的变化做比较

@author: Tracy Zhu
"""

### 导入系统库
import sys, time
import logging

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *

out_change_data = pd.read_csv(OUTER_DATA_CHANGE_FILE_NAME, header=0, index_col=False, names=DATA_CHANGE_COLUMNS)


def get_outer_data_change(instrument_id, trading_day):
    change_ratio = 0
    variety_id = get_variety_id(instrument_id)
    out_change_data_by_day = out_change_data[out_change_data.Quote_Day == int(trading_day)]
    if variety_id in out_change_data_by_day.Influence_Variety_Name.values:
        out_change_data_by_variety = out_change_data_by_day[out_change_data_by_day.Influence_Variety_Name == variety_id]
        change_ratio = out_change_data_by_variety.Change_Ratio.values[0]
        return change_ratio


if __name__ == '__main__':
    instrument_id = 'NI1709'
    trading_day = 20170509
    change_ratio = get_outer_data_change(instrument_id, trading_day)
    print change_ratio

