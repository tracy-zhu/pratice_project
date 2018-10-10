# -*- coding: utf-8 -*-
"""

# 计算每个品种的涨跌停板幅度

# 输出一个DataFrame到一个csv中

Tue 2017/3/14

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *
variety_id_array = ['RU', 'RB', 'NI', 'SR', 'CF', 'TA', 'RM', 'OI', 'CU', 'AL', 'ZN', 'BU', 'AG', 'FG', 'WH', 'MA', 'HC', 'ZC', 'PB', 'SN', 'AU', 'CY', "SM", "SF"]

trading_day = "20171206"
pre_trading_day = "20171205"

def get_limit_range_percent(instrument_id, trading_day):
    quote_data = read_data(main_instrument_id, trading_day)
    pre_settlement_price = quote_data.Pre_Settlement_Price.values[0]
    upper_limit_price = quote_data.Upper_Limit_Price.values[-5]
    upper_limit_range = float(upper_limit_price - pre_settlement_price) / float(pre_settlement_price)
    return upper_limit_range


for variety_id in variety_id_array:
    main_instrument_id, _ = get_variety_main(variety_id, trading_day)
    if main_instrument_id != None:
        upper_limit_range_today = get_limit_range_percent(main_instrument_id, trading_day)
        upper_limit_range_yesterday = get_limit_range_percent(main_instrument_id, pre_trading_day)
        print variety_id, upper_limit_range_today, upper_limit_range_yesterday


