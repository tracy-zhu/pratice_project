# -*- coding: utf-8 -*-
"""

# 本脚本用于计算开盘一分钟比较特殊的情况

# 输出一个DataFrame到一个csv中

Tue 2017/3/14

@author: Tracy Zhu
"""
# 导入系统库
import sys
# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *

frequency = '1s'
trading_day = '20170703'
beta = 1.2682928696
std = 1
G_TICK_QUOTE_FILE_ROOT_FOLDER = 'Z:\\night_data\\'

def read_data(instrument_id, trading_day):
    file_name = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + trading_day + "\\" + instrument_id + ".csv"
    quote_data = pd.read_csv(file_name, header=0, index_col=False, names=G_TICK_COLUMNS)
    return quote_data

rm_quote_data = read_data('RM801', trading_day)
m_quote_data = read_data('M1801', trading_day)
rm_data_frame = get_dataframe(rm_quote_data, frequency)
m_data_frame = get_dataframe(m_quote_data, frequency)

sell_price_spread = m_data_frame.Bid_Price1 - beta * rm_data_frame.Ask_Price1
buy_price_spread = m_data_frame.Ask_Price1 - beta * rm_data_frame.Bid_Price1

sell_open_point = sell_price_spread[sell_price_spread > std]
buy_open_point = buy_price_spread[buy_price_spread < -std]


