# -*- coding: utf-8 -*-
"""

# 本脚本根据筛选出开盘一分钟后的情况，将对应的数据文件筛选出来
# 统一放入copy_file_folder文件夹中
# 上期所筛选深度行情数据， 郑商所得出前开盘价


Tue 2017/3/14

@author: Tracy Zhu
"""
# 导入系统库
import sys
import shutil
import os

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *
trading_day_list = get_trading_day_list()

DEPTH_QUOTE_FILE = "E:\\quote_data\\depth_quote\\"
RESULT_FILE_NAME = "F:\\open_price_strategy\\open_volume_series\\open_minute_info.csv"
column_name = ["instrument_id", "trading_day", "percent_change"]
copy_file_folder = "E:\\copy_file_folder\\"
open_time = '20:59:00'
duration_time = '21:05:00'
result_file = pd.read_csv(RESULT_FILE_NAME, names=column_name)

for index in range(len(result_file)):
    instrument_id = result_file.instrument_id[index].split()[0]
    trading_day = str(result_file.trading_day[index])
    percent_change = result_file.percent_change[index].split()[0]
    if percent_change != 'None':
        print trading_day
        out_file_folder = copy_file_folder + trading_day + "\\"
        if not os.path.exists(out_file_folder):
            os.makedirs(out_file_folder)
        if len(instrument_id) == 6:
            source_file = DEPTH_QUOTE_FILE + trading_day + "\\" + instrument_id + '.txt'
            if os.path.exists(source_file):
                shutil.copy(source_file, out_file_folder)
        elif len(instrument_id) == 5:
            quote_data = read_data(instrument_id, trading_day)
            open_index = quote_data.index[quote_data.Update_Time == duration_time][0]
            out_file_name = out_file_folder + instrument_id + '.csv'
            out_DF = quote_data.head(open_index + 2)
            out_DF.to_csv(out_file_name)

