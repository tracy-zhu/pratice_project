# -*- coding: utf-8 -*-
"""

# 本脚本用来计算抢单品种9点那一刻的成交量

# 输出一个DataFrame到一个csv中

Tue 2016/12/21

@author: Tracy Zhu
"""
# 导入系统库
import sys
from datetime import timedelta

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *
trading_day_list = get_trading_day_list()

variety_id_list = ['RU', 'RB', 'CU', 'AL', 'ZN', 'BU', 'AG', 'M', 'P', 'Y',
                    'HC', 'AU', 'NI']
morning_open_time = '09:00:00'

index_day = datetime.now() - timedelta(days=8)
index_day_str = index_day.strftime('%Y%m%d')


def get_rob_volume(main_quote_data):
    rob_volume = 0
    open_index = main_quote_data.index[main_quote_data.Update_Time == morning_open_time]
    if len(open_index) > 0:
        open_index = open_index[0]
        rob_volume = main_quote_data.ix[open_index].Total_Match_Volume - main_quote_data.ix[open_index - 1].Total_Match_Volume
    return rob_volume


optimal_volume_list = dict()
trade_day_list = []
for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    if trading_day > index_day_str:
        print trading_day
        trade_day_list.append(trading_day)
        instrument_file_list = get_instrument_file_list(trading_day)
        for (variety_id, instrument_list) in instrument_file_list.items():
            if variety_id in variety_id_list:
                print variety_id
                if optimal_volume_list.has_key(variety_id):
                    pass
                else:
                    optimal_volume_list[variety_id] = []
                main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
                if main_instrument_id != None:
                    main_quote_data = read_data(main_instrument_id, trading_day)
                    optimal_volume = get_rob_volume(main_quote_data)
                    optimal_volume_list[variety_id].append(optimal_volume)

optimal_volume_frame = DataFrame(optimal_volume_list, index=trade_day_list)
out_file_folder = 'C:\\Users\\Tracy Zhu\\Desktop\\tool\\error_in_rob_order\\rob_volume_series.csv'
optimal_volume_frame.to_csv(out_file_folder)


# def main():
#     optimal_volume_sr_list = []
#     main_instrument_id = 'FG705'
#     sub_instrument_id = 'FG709'
#     for trade_day in trading_day_list:
#         trading_day = trade_day[:-1]
#         if trading_day > '20161204':
#             main_quote_data = read_data(main_instrument_id, trading_day)
#             sub_quote_data = read_data(sub_instrument_id, trading_day)
#             optimal_volume = get_optimal_volume(main_quote_data, sub_quote_data)
#             optimal_volume_sr_list.append(optimal_volume)
#
#
# if __name__ == '__main__':
#     main()

