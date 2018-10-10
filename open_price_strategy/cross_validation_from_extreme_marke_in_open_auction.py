# -*- coding: utf-8 -*-
"""

# 本脚本读取两份文件，一份是开盘集合竞价1分钟有极端行情的文件
# 另外一份是集合竞价中满足某一条件的文件
# 为了得到一个结果，就是将同时在两个文件中的合约和交易日筛选出来

# 输出一个DataFrame到一个csv中

WED 2017/11/29

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：：
sys.path.append("..")
from python_base.open_price_algorithm import *
from python_base.get_open_volume_series_instrument import *

raw_file_one = "..\\open_price_strategy\\result\\extreme_change_in_1_minute_after_open_auction_without_wrong_order.csv"
raw_file_two = "..\\open_price_strategy\\result\\bid_suspend_order_before_call_auction.csv"
result_file_name = "..\\open_price_strategy\\result\\cross_validation_result.csv"
result_file = open(result_file_name, "wb")

result_file.write("instrument_id, trading_day, order_volume, open_volume, direction, order_price, open_price, spread_change_tick\n")
file_one_columns = ["main_instrument_id", "trading_day", "tick_change", "open_volume", "open_interest_change"]
extreme_change_df = pd.read_csv(raw_file_one, header=0, index_col=False, names=file_one_columns)

with open(raw_file_two, "r") as f:
    str_lines = f.readlines()
    for line in str_lines[1:]:
        line_list = line.split(",")
        instrument_id = line_list[0]
        trading_day = line_list[1]
        print instrument_id, trading_day
        slice_df_instrument = extreme_change_df[extreme_change_df.main_instrument_id == instrument_id]
        if len(slice_df_instrument) > 0:
            slice_df_instrument_trading_day = slice_df_instrument[slice_df_instrument.trading_day == int(trading_day)]
            if len(slice_df_instrument_trading_day) > 0:
                result_file.write(line)

result_file.close()



