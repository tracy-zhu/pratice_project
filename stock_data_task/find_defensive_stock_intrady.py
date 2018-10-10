# -*- coding: utf-8 -*-
"""

# 生成日内某段时间股票的涨幅排名

# 在大盘下跌的过程中显得比较重要

Thu 2018/03/15

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_tool.find_defensive_stock import *

out_file_folder = "D:\\strategy\\open_price_strategy\\stock_data\\defensive_stock_intrady\\"

now = datetime.now()
trading_day = now.strftime('%Y%m%d')

file_folder = out_file_folder + trading_day
isExists = os.path.exists(file_folder)
if not isExists:
    os.makedirs(file_folder)


def get_stock_yield_period(stock_code, trading_day, begin_time, end_time):
    """
    找出固定某只股票
    :param stock_code:
    :param trading_day:
    :param begin_time:
    :param end_time:
    :return:
    """
    stock_yield = -999
    stock_tick_data = read_stock_tick_data(stock_code, trading_day)
    if len(stock_tick_data) > 0 :
        slice_df = stock_tick_data[stock_tick_data.index>=begin_time]
        slice_df = slice_df[slice_df.index<=end_time]
        if len(slice_df) > 0:
            pre_close_price = slice_df.preClosePrice.values[0]
            begin_price = slice_df.lastPrice.values[0]
            end_price = slice_df.lastPrice.values[-1]
            stock_yield = (float(end_price - begin_price) / float(pre_close_price)) * 100
    return stock_yield


def find_defensive_stock_intrady(trading_day, begin_time, end_time):
    """
    找出当个交易日指定时间段排名涨幅排名靠前的股票
    :param trading_day: '20180320'
    :param start_time:133000
    :param end_time:150000
    :return:
    """
    stock_change_dict = defaultdict()
    trading_day_str = trading_day[:4] + '-' + trading_day[4:6] + '-' + trading_day[6:8]
    start_date = get_pre_trading_day_stock(trading_day_str)
    stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', start_date, start_date)
    raw_stock_code_list = stock_df.code.unique()
    stock_code_list = delete_new_stock(raw_stock_code_list, 60, start_date)
    for stock_code in stock_code_list:
        print stock_code
        stock_yield = get_stock_yield_period(stock_code, trading_day, begin_time, end_time)
        stock_change_dict[stock_code] = stock_yield
    stock_change_series = Series(stock_change_dict)
    stock_change_sort = stock_change_series.sort_values(ascending=False)
    select_code_list = stock_change_sort.index[:20]
    return select_code_list, stock_change_sort


def find_concept_num(select_code_list, trading_day):
    """
    找出每个股票对应的板块，并找出出现最多的板块
    :param select_code_list:
    :return:
    """
    concept_list = []
    trading_day_str = trading_day[:4] + '-' + trading_day[4:6] + '-' + trading_day[6:8]
    pre_trading_day = get_pre_trading_day_stock(trading_day_str)
    for select_code in select_code_list:
        concept_stock_list = find_stock_concept_ifind(select_code, pre_trading_day)
        concept_list = concept_list + concept_stock_list
    counts = dict()
    for concept_name in concept_list:
        if concept_name in counts:
            counts[concept_name] += 1
        else:
            counts[concept_name] = 1
    sort_counts = sorted(counts.items(), key=lambda  d:d[1], reverse=True)
    return sort_counts


if __name__ == '__main__':
    begin_time = 143000
    end_time = 150000
    out_file_name = file_folder + "\\defensive_stock_intrady.txt"
    f = open(out_file_name, 'wb')
    select_code_list, stock_change_sort = find_defensive_stock_intrady(trading_day, begin_time, end_time)
    for stock_code in select_code_list:
        yield_value = stock_change_sort.loc[stock_code]
        chi_name = find_stock_chi_name(stock_code)
        print>>f, stock_code, ",", chi_name, ',', str(yield_value)
    f.close()

    concept_out_file_name = file_folder + "\\concept_value_counts.txt"
    f2 = open(concept_out_file_name, 'wb')
    sort_counts = find_concept_num(select_code_list, trading_day)
    for concept_name, num in sort_counts:
        concept_str = concept_name.split(',')[1]
        print>>f2, concept_str, ',', num
    f2.close()
