# -*- coding: utf-8 -*-
"""

# 本脚本用来计算不同品种集合竞价最优成交量

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

# variety_id_list = ['RU', 'RB', 'NI', 'SR', 'CF', 'TA', 'RM', 'OI', 'CU', 'AL', 'ZN', 'BU', 'AG', 'FG',  'MA',
#                    'HC', 'ZC']
variety_id_list = ['RU', 'RB', 'NI', 'SR', 'CF', 'TA', 'RM', 'CU', 'AL', 'ZN', 'BU', 'AG', 'FG', 'MA', 'HC', 'ZC']
open_time = '20:59:00'

index_day = datetime.now() - timedelta(days=14)
index_day_str = index_day.strftime('%Y%m%d')


def get_optimal_volume(main_quote_data, sub_quote_data):
    optimal_volume = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    sub_open_quote = sub_quote_data[sub_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0 and len(sub_open_quote) > 0:
        # optimal_volume = min(main_open_quote.Total_Match_Volume.values[0], sub_open_quote.Total_Match_Volume.values[0])
        optimal_volume = main_open_quote.Total_Match_Volume.values[0]
        optimal_volume = optimal_volume / 2
    return optimal_volume


def get_open_volume(main_quote_data):
    optimal_volume = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0:
        optimal_volume = main_open_quote.Total_Match_Volume.values[0]
        optimal_volume = optimal_volume / 2
    return optimal_volume


def get_open_volume_series(instrument_id, trading_day):
    trading_day_time = datetime.strptime(trading_day, '%Y%m%d')
    pre_trading_day = trading_day_time - timedelta(days=14)
    for trade_day in pd.date_range(pre_trading_day, trading_day_time):
        trading_day_str = trade_day.strftime('%Y%m%d')
        if trading_day_str in trade_day_list:
            main_quote_data = read_data(instrument_id, trading_day_str)
            open_volume = get_open_volume(main_quote_data)
            print trading_day_str, open_volume


optimal_volume_list = dict()
main_instrument_dict = dict()
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
                    sub_quote_data = read_data(sub_instrument_id, trading_day)
                    # optimal_volume = get_optimal_volume(main_quote_data, sub_quote_data)
                    optimal_volume = get_open_volume(main_quote_data)
                    optimal_volume_list[variety_id].append(optimal_volume)
                    main_instrument_dict[variety_id] = main_instrument_id


optimal_volume_frame = DataFrame(optimal_volume_list, index=trade_day_list)
out_file_folder = 'F:\\open_price_strategy\\open_volume_series\\main_open_volume_series.csv'
optimal_volume_frame.to_csv(out_file_folder)


ma_volume_file = 'F:\\open_price_strategy\\open_volume_series\\ma_volume.csv'
f = open(ma_volume_file, 'wb')
for variety_id, optimal_volume in optimal_volume_list.items():
    main_instrument_id = main_instrument_dict[variety_id]
    ma_volume = float(sum(optimal_volume)) / len(optimal_volume)
    str_line = main_instrument_id + ',' + str(ma_volume) + '\n'
    f.write(str_line)
f.close()


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

