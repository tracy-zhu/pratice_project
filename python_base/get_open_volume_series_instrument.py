# -*- coding: utf-8 -*-
"""

# 本脚本用于计算一个品种，及其前N天的集合竞价成交量


Tue 2016/12/21

@author: Tracy Zhu
"""
# 导入系统库
import sys
from datetime import timedelta,datetime

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *
trading_day_list = get_trading_day_list()
open_time = '20:59:00'

def get_open_volume(main_quote_data):
    optimal_volume = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0:
        optimal_volume = main_open_quote.Total_Match_Volume.values[0]
        optimal_volume = optimal_volume / 2
    return optimal_volume


def get_open_volume_series(instrument_id, trading_day):
    open_volume_list = []
    trading_day_time = datetime.strptime(trading_day, '%Y%m%d')
    pre_trading_day = trading_day_time - timedelta(days=14)
    for trade_day in pd.date_range(pre_trading_day, trading_day_time):
        trading_day_str = trade_day.strftime('%Y%m%d')
        if (trading_day_str + '\n') in trading_day_list:
            main_quote_data = read_data(instrument_id, trading_day_str)
            open_volume = get_open_volume(main_quote_data)
            if open_volume != 0:
                open_volume_list.append(open_volume)
            print trading_day_str, open_volume
    open_volume_arr = np.array(open_volume_list)
    if len(open_volume_arr) > 0:
        mean_volume = open_volume_arr[:-1].mean()
        last_open_volume = open_volume_list[-1]
    else:
        last_open_volume = 0
        mean_volume = 1
    return last_open_volume, mean_volume


if __name__ == '__main__':
    trading_day_list = get_trading_day_list()
    instrument_id = 'RB1710'
    trading_day = '20170502'
    get_open_volume_series(instrument_id, trading_day)
