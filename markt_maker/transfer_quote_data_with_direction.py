# -*- coding: utf-8 -*-
"""

# 本脚本将原始行情文件截取出对于分析有用的数据列，并将判断方向的n列加入
# 判断方向的函数根据high_frequency_data_pattern_analysis得到

Tue 2017/10/16

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math
import talib as ta
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *
from markt_maker.high_frequency_data_pattern_analysis import *

now = datetime.now()

#trading_day = now.strftime('%Y%m%d')
trading_day = '20171013'
#instrument_id = 'SPD MA801&MA805'
instrument_id = 'AL1712'
sample_period = 10
quote_data = read_data(instrument_id, trading_day)
slice_quote = quote_data.loc[:, ['Instrument_ID', 'Update_Time', 'Turnover', 'Total_Match_Volume', 'Bid_Price1',
                                 'Bid_Volume1', 'Ask_Price1', 'Ask_Volume1']]

direction_array, direction_raw_array = get_trade_volume_direction(instrument_id, trading_day, sample_period)
slice_quote['trade_volume_direction'] = direction_array
slice_quote['trade_volume_prob'] = direction_raw_array

result_file_folder = "..\\markt_maker\\transfer_depth_quote\\"
isExists = os.path.exists(result_file_folder)
if not isExists:
    os.makedirs(result_file_folder)
result_file_name = result_file_folder + instrument_id + ".csv"
slice_quote.to_csv(result_file_name)
