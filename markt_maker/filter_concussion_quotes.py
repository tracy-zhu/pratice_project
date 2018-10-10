# -*- coding: utf-8 -*-
"""

# 脚本用于各种指标测试得到适合做做市商的震荡行情

Tue 2017/11/21

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
out_file_folder = "..\\markt_maker\\"

now = datetime.now()
trading_day_list = get_trading_day_list()
golden_fork_value = 10
death_fork_value = 20

result_file = "..\\markt_maker\\result\\duration_tick_of_extreme_price.csv"
f = open(result_file, 'wb')

def filter_concussion_quotes_by_atr(instrument_id, trading_day, back_period):
    """
    函数用于atr指定的规则筛选出行情，每段行情的开始和结束时间
    :param instrument_id:
    :param trading_day:
    :param back_period: 14(atr的默认数字）
    :return: list, 每一个元素是tuple, 分别为筛选出行情的开始时间和结束时间
    """
    atr_arr = atr_calculator(instrument_id, trading_day, back_period)
    minute_data = read_minute_data(instrument_id, trading_day)
    atr_series = Series(atr_arr, index=minute_data.Update_Time)
    atr_ma_arr = ta.MA(atr_arr, 5)
    atr_ma_series = Series(atr_ma_arr, index=minute_data.Update_Time)
    atr_diff_list = [np.nan] * 5
    for index in range(5, len(atr_arr)):
        atr_diff = atr_arr[index] - atr_ma_arr[index-5]
        atr_diff_list.append(atr_diff)

    start_time = 0
    round_time_list = []
    for index in range(len(atr_arr)):
        if atr_arr[index] < death_fork_value and atr_diff_list[index] < 0 and start_time == 0:
            start_time = minute_data.Update_Time[index]
        elif start_time != 0 and atr_diff_list[index] > 0 and atr_arr[index] > golden_fork_value:
            end_time = minute_data.Update_Time[index]
            round_time_list.append((start_time, end_time))
            start_time = 0
    return round_time_list


def find_extreme_value_first_appearance(instrument_id, trading_day, back_period):
    high_duration_tick = None
    low_duration_tick = None
    round_time_list = filter_concussion_quotes_by_atr(instrument_id, trading_day, back_period)
    quote_data = read_data(instrument_id, trading_day)
    for (start_time, end_time) in round_time_list:
        print start_time, end_time
        if start_time < end_time:
            slice_data = quote_data[quote_data.Update_Time >= start_time]
            slice_data = slice_data[slice_data.Update_Time <= end_time]
            high_duration_tick, low_duration_tick = extreme_value_first_appearance_time(slice_data)
        else:
            slice_data_night = quote_data[quote_data.Update_Time >= start_time]
            slice_data_day = quote_data[quote_data.Update_Time <= end_time]
            slice_data = pd.concat([slice_data_night, slice_data_day])
            high_duration_tick, low_duration_tick = extreme_value_first_appearance_time(slice_data)
        print>> f, high_duration_tick, ',', low_duration_tick


def extreme_value_first_appearance_time(slice_data):
    high_price = slice_data.Last_Price.max()
    low_price = slice_data.Last_Price.min()
    high_index = slice_data.index[slice_data.Last_Price == high_price][0]
    low_index = slice_data.index[slice_data.Last_Price == low_price][0]
    high_duration_tick = high_index - slice_data.index[0] + 1
    low_duration_tick = low_index - slice_data.index[0] + 1
    return high_duration_tick, low_duration_tick


if __name__ == '__main__':
    instrument_id = "PB1712"
    start_date = "20171101"
    back_period = 14
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day >= start_date and trading_day < now.strftime("%Y%m%d"):
            print trading_day
            find_extreme_value_first_appearance(instrument_id, trading_day, back_period)
    f.close()
