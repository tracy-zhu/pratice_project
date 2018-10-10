# -*- coding: utf-8 -*-
"""

# 找出当天涨停的股票数据中，上一个交易日的统计特征

# 同样是在大盘大跌中要有效

Thu 2018/03/26

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_file_api import *
from stock_data_task.find_defensive_stock_intrady_by_volume import *

trading_day = '2018-03-26'
pre_trading_day = '2018-03-23'
start_date = '2018-03-19'
index_code = '000300.SH'
begin_time = '14:30'
end_time = '15:00'
spot_time = '14:30'



def get_volume_ratio_stock(stock_code, start_date, end_date, begin_time, end_time):
    period_volume_series = get_pre_period_volume_series_minute(stock_code, start_date, end_date, begin_time, end_time)
    mean_volume = np.mean(period_volume_series.values[:-1])
    last_volume = period_volume_series.values[-1]
    try:
        volume_ratio = float(last_volume) / float(mean_volume)
    except:
        print "something is wrong!"
        return 1
    else:
        return volume_ratio


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


def block_describtion(stock_code_list, trading_day, spot_time):
    """
    根据股票代码和交易日找出当天这个股票池的涨跌幅比例，平均涨跌幅
    :param stock_code_list:
    :param trading_day:'2018-03-23"
    spot_time : '14:30'
    :return:
    """
    block_yield_mean = -999
    spot_positive_ratio = -999
    percent_chg_list = []
    spot_positive_num = 0
    for stock_code in stock_code_list:
        print stock_code
        spot_yield_value = get_stock_period_yield_minute(stock_code, trading_day, spot_time, '15:00')
        percent_chg_list.append(spot_yield_value)
        if spot_yield_value > 0:
            spot_positive_num += 1
        if len(percent_chg_list) > 0:
            block_yield_mean = Series(percent_chg_list).mean()
            spot_positive_ratio = float(spot_positive_num)/ float(len(percent_chg_list))
    return block_yield_mean, spot_positive_ratio

up_limit_stock_list = find_stock_up_limit(trading_day, 1)
yield_list = []
yield_list_open = []
trade_volume_ratio_list = []
period_yield_list = []
period_yield_index = get_index_period_yield(index_code, pre_trading_day, begin_time, end_time)

volume_ratio_dict = defaultdict()

sort_counts = find_concept_num(up_limit_stock_list, '20180323')

concept_code_list = []
for concept_name, num in sort_counts[:10]:
    concept_code = concept_name.split(',')[0]
    concept_code_list.append(concept_code)
    concept_str = concept_name.split(',')[1]
    print concept_code, ',', concept_str, ',', num

block_mean_yield_dict = defaultdict()
block_yield_list = []
positive_ratio_list = []
for concept_code in concept_code_list:
    stock_code_list = find_concept_stock_ifind(concept_code, pre_trading_day)
    block_yield_mean, positive_ratio = block_describtion(stock_code_list, trading_day, spot_time)
    block_yield_list.append(block_yield_mean)
    positive_ratio_list.append(positive_ratio)
    block_mean_yield_dict[concept_code] = block_yield_mean
block_yield_series = Series(block_yield_list)
block_yield_series.hist()
positive_ratio_series = Series(positive_ratio_list)
positive_ratio_series.hist()

for block_code, values in block_mean_yield_dict.items():
    block_name = concept_name_dict[block_code]
    block_yield_mean = values
    # positive_ratio = values[1]
    print block_name, block_yield_mean, positive_ratio

for stock_code in up_limit_stock_list:
    stock_df = get_stock_df(stock_code, pre_trading_day, pre_trading_day)
    open_price, close_price = get_stock_open_close_price(stock_code, pre_trading_day)
    pct_chg_open = float(close_price) / float(open_price) - 1
    pct_chg = stock_df.PCT_CHG.values[0]
    stock_period_yield = get_stock_period_yield_minute(stock_code, trading_day, begin_time, end_time)
    relative_yield = stock_period_yield - period_yield_index
    volume_ratio = get_volume_ratio_stock(stock_code, start_date, pre_trading_day, begin_time, end_time)
    if pct_chg > -10:
        yield_list.append(pct_chg)
        yield_list_open.append(pct_chg_open)
        period_yield_list.append(relative_yield)
        trade_volume_ratio_list.append(volume_ratio)
        volume_ratio_dict[stock_code] = volume_ratio

sort_dict = sorted(volume_ratio_dict.items(), key=lambda d:d[1], reverse=True)

yield_series = Series(yield_list)
yield_series.hist()

yield_open_series = Series(yield_list_open)
yield_open_series.hist()

period_yield_series =Series(period_yield_list)
period_yield_series.hist()

trade_volume_ratio_series = Series(trade_volume_ratio_list)
trade_volume_ratio_series.hist()