# -*- coding: utf-8 -*-
"""

# 本脚本分析日内行情的变化特征，旨在能够分辨出什么是趋势行情，什么是日内震荡行情
# 分辨出什么样的品种适合做市商行情，挂单比较
# 日内是单边趋势行情还是带均值回复行情
# 定义一个函数，判断出在一段日内行情中，什么样的算作是趋势，什么样的算作是震荡行情。

Tue 2017/11/03

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
trading_day_list = get_trading_day_list()


def get_market_change_intrday(instrument_id, trading_day):
    """
    获取一天中，最高，最低，收盘价相对于开盘价的变化幅度
    :param instrument_id:
    :param trading_day:
    :return: 返回分别是三个变化幅度, 还有成交量
    """
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    close_quote = quote_data.tail(1)
    high_price = close_quote.Highest_Price.values[0]
    low_price = close_quote.Lowest_Price.values[0]
    open_price = close_quote.Open_Price.values[0]
    close_price = close_quote.Close_Price.values[0]
    total_match_volume = close_quote.Total_Match_Volume.values[0]
    initial_open_interest = quote_data.Open_Interest.values[0]
    final_open_interest = close_quote.Open_Interest.values[0]
    interest_change = final_open_interest - initial_open_interest
    high_tick_change = (high_price - open_price) / tick
    low_tick_change = (low_price - open_price) / tick
    close_tick_change = (close_price - open_price) / tick
    return high_tick_change, low_tick_change, close_tick_change, total_match_volume, interest_change


def get_unit_time_change(instrument_id, trading_day):
    """
    获取一个合约一天中价格的波动程度，价格绝对变化除以笔数，价格的变化采取的是middle_price, total_match_volume也算是一个指标
    每天的收盘价和开盘价之差也算一个指标
    :param instrument_id:
    :param trading_day:
    :return: abs_middle_price_change, mean_match_volume, close_tick_change
    """
    _, _, close_tick_change, total_match_volume, _ = get_market_change_intrday(instrument_id, trading_day)
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    middle_price_series =  (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    price_change_arr = np.array(middle_price_series.diff().dropna())
    abs_price_change_arr = np.abs(price_change_arr) / tick
    abs_middle_price_change = np.sum(abs_price_change_arr) / len(quote_data)
    mean_match_volume = total_match_volume / len(quote_data)
    return abs_middle_price_change, mean_match_volume, close_tick_change


def output_intrady_change(instrument_id, start_date, end_date):
    out_file_name = "..\\markt_maker\\result\\intrday_change.csv"
    f = open(out_file_name, 'wb')
    f.write("trading_day, high_tick_change, low_tick_change, close_tick_change, total_match_volume,interest_change\n")
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        print trading_day
        if start_date <= trading_day <= end_date:
            result_list = get_market_change_intrday(instrument_id, trading_day)
            str_line = trading_day + ',' + str(result_list[0]) + "," + str(result_list[1]) + "," + str(result_list[2]) + ','\
                       + str(result_list[3]) + "," + str(result_list[4]) + '\n'
            f.write(str_line)
    f.close()


def out_put_unit_change_for_all_instruments(variety_id_list):
    out_file_name = "..\\markt_maker\\result\\activity_for_all_instruments.csv"
    f = open(out_file_name, 'wb')
    f.write("instrument_id, abs_middle_price_change, mean_match_volume, close_tick_change\n")
    instrument_id_dict = defaultdict(list)
    datetime_now = datetime.now()
    index_day = datetime_now - timedelta(days=14)
    start_date = index_day.strftime('%Y%m%d')
    end_date = datetime_now.strftime("%Y%m%d")
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if start_date <= trading_day <= end_date:
            for variety_id in variety_id_list:
                print variety_id, trading_day
                main_instrument_id, _ = get_variety_main(variety_id, trading_day)
                if main_instrument_id != None:
                    result_list = get_unit_time_change(main_instrument_id, trading_day)
                    instrument_id_dict[main_instrument_id].append(result_list)
    for instrument_id, result_list in instrument_id_dict.items():
        unzip_result_list = zip(*result_list)
        abs_middle_price_change = np.mean(unzip_result_list[0])
        mean_match_volume = np.mean(unzip_result_list[1])
        close_tick_change = np.mean(unzip_result_list[2])
        str_line = instrument_id + "," + str(abs_middle_price_change) + "," + str(mean_match_volume) \
                   + "," + str(close_tick_change) + "\n"
        f.write(str_line)
    f.close()



if __name__ == '__main__':
    variety_id_list = ['RU', 'RB', 'NI', 'SR', 'CF', 'TA', 'RM', 'OI', 'CU', 'AL', 'ZN', 'BU', 'AG', 'FG', 'MA', 'HC', 'ZC', 'PB', 'SN', 'AU']


