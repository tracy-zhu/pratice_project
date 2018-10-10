# -*- coding: utf-8 -*-
"""

# 生成日内某段时间股票的平均成交量大小排名，再结合涨跌幅

# 在大盘下跌的过程中显得比较重要

Thu 2018/03/15

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_data_task.find_defensive_stock_intrady import *
from stock_data_task.find_hot_block import *

out_file_folder = "D:\\strategy\\open_price_strategy\\stock_data\\defensive_stock_intrady\\"

now = datetime.now()
trading_day = now.strftime('%Y%m%d')
trading_day_list = get_trading_day_list()

file_folder = out_file_folder + trading_day
isExists = os.path.exists(file_folder)
if not isExists:
    os.makedirs(file_folder)


def get_stock_volume_para(stock_code, trading_day, begin_time, end_time):
    """
    找出固定一段时间的成交量的因子排名，目的是为了找出大盘下跌过程中，主力吸筹的股票
    :param stock_code:
    :param trading_day: '20180321'
    :param begin_time: 133000
    :param end_time: 150000
    :return:
    """
    period_volume = np.nan
    stock_tick_data = read_stock_tick_data(stock_code, trading_day)
    # trade_volume_series = stock_tick_data.volume.diff()
    # trade_volume_series = trade_volume_series.dropna()
    # fig, ax = plt.subplots()
    # ax.plot(trade_volume_series.values)
    if len(stock_tick_data) > 0:
        slice_df = stock_tick_data[stock_tick_data.index >= begin_time]
        slice_df = slice_df[slice_df.index <= end_time]
        if len(slice_df) > 0:
            period_volume = slice_df.volume.values[-1] - slice_df.volume.values[0]
    return period_volume


def get_stock_volume_period_minute(stock_code, trading_day, begin_time, end_time):
    """
    根据分钟数据得出某个时间段的成交量
    :param stock_code:
    :param trading_day: '2018-03-20'
    :param begin_time:'09:30'
    :param end_time:'15:00'
    :return:
    """
    begin_period = trading_day + ' ' + begin_time
    end_period = trading_day + ' ' + end_time
    stock_min_data = read_stock_minute_data(stock_code, trading_day)
    select_df = stock_min_data[stock_min_data.time >= begin_period]
    select_df = select_df[select_df.time <= end_period]
    period_volume = select_df.volume.sum()
    return period_volume


def get_pre_period_volume_series_minute(stock_code, start_date, end_date, begin_time, end_time):
    """
    根据分钟数据获得过去一段时间该成交量的比例
    :param stock_code:
    :param start_date: '2018-03-19'
    :param end_date: '2018-03-23'
    :param begin_time: '14:00'
    :param end_time:'15:00'
    :return:
    """
    period_volume_list = []
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        trading_day = trading_day[:4] + '-' + trading_day[4:6] + '-' + trading_day[6:]
        if start_date <= trading_day <= end_date:
            period_volume = get_stock_volume_period_minute(stock_code, trading_day, begin_time, end_time)
            period_volume_list.append(period_volume)
    period_volume_series = Series(period_volume_list)
    period_volume_series = period_volume_series.dropna()
    return period_volume_series


def get_pre_period_volume_series(stock_code, start_date, end_date, begin_time, end_time):
    """
    找出过去一段时间同个时间段，相同的股票的成交量序列
    :param stock_code:
    :param start_date:
    :param end_date:
    :param begin_time:
    :param end_time:
    :return:
    """
    period_volume_list = []
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if start_date <= trading_day <= end_date:
            period_volume = get_stock_volume_para(stock_code, trading_day, begin_time, end_time)
            period_volume_list.append(period_volume)
    period_volume_series = Series(period_volume_list)
    period_volume_series = period_volume_series.dropna()
    return period_volume_series


def find_stock_volume_ratio(trading_day, begin_time, end_time):
    """
    对于某一时间段，将该股票和过去N天该时段的平均成交量作一个比较，进行排序，得出一定的指标；
    :param trading_day:
    :param begin_time:
    :param end_time:
    :return:
    """
    start_date = '20180315'
    end_date = '20180321'
    stock_volume_ratio_dict = defaultdict()
    trading_day_str = trading_day[:4] + '-' + trading_day[4:6] + '-' + trading_day[6:8]
    pre_trading_day = get_pre_trading_day_stock(trading_day_str)
    stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', pre_trading_day, pre_trading_day)
    raw_stock_code_list = stock_df.code.unique()
    stock_code_list = delete_new_stock(raw_stock_code_list, 60, pre_trading_day)
    for stock_code in stock_code_list:
        print stock_code
        period_volume_series = get_pre_period_volume_series(stock_code, start_date, end_date, begin_time, end_time)
        period_volume_now = get_stock_volume_para(stock_code, trading_day, begin_time, end_time)
        if not np.isnan(period_volume_now) and len(period_volume_series) > 0 and period_volume_series.mean() != 0:
            stock_volume_ratio_dict[stock_code] = float(period_volume_now) / float(period_volume_series.mean())
    stock_volume_ratio_series = Series(stock_volume_ratio_dict)
    stock_volume_ratio_sort = stock_volume_ratio_series.sort_values(ascending=False)
    return stock_volume_ratio_sort


def find_stock_list_concept(stock_code_list, trading_day):
    """
    找出每个股票的对应的板块，形成个set
    :param stock_code_list:
    :param trading_day:
    :return:
    """
    concept_list = []
    trading_day_str = trading_day[:4] + '-' + trading_day[4:6] + '-' + trading_day[6:8]
    pre_trading_day = get_pre_trading_day_stock(trading_day_str)
    for select_code in stock_code_list:
        concept_stock_list = find_stock_concept_ifind(select_code, pre_trading_day)
        concept_list = concept_list + concept_stock_list
    concept_set = set(concept_list)
    return concept_set

def get_sort_concept_yiled(concept_set, trading_day,out_file_folder):
    """
    根据对应的板块代码，对板块的收益率进行排序，并输出到文件中
    :param concept_set:
    :param out_file_name:
    :return:
    """
    spot_time = '14:30'
    trading_day_str = trading_day[:4] + '-' + trading_day[4:6] + '-' + trading_day[6:8]
    pre_trading_day = get_pre_trading_day_stock(trading_day_str)
    block_default_dict = defaultdict()
    for block_code in concept_set:
        print block_code
        concept_code = block_code.split(',')[0]
        stock_code_list = find_concept_stock_ifind(concept_code, pre_trading_day)
        block_yield_mean, positive_ratio, positive_ratio_change = stock_list_description(stock_code_list, trading_day, spot_time)
        block_default_dict[block_code] = (block_yield_mean, positive_ratio)
    sorted_block_by_ratio = sorted(block_default_dict.items(), key=lambda d: d[1][0], reverse=True)

    file_name = out_file_folder + 'defensive_block_after_yield.txt'
    f = open(file_name, 'wb')
    for values in sorted_block_by_ratio:
        block_name = values[0].split(',')[1]
        positive_ratio = values[1][0]
        print >>f,  block_name, ',', positive_ratio
    f.close()


if __name__ == '__main__':
    trading_day = '20180322'
    out_file_folder = 'D:\\strategy\\open_price_strategy\\stock_data\\' + trading_day + "\\"
    isExists = os.path.exists(out_file_folder)
    if not isExists:
        os.makedirs(out_file_folder)
    begin_time = 143000
    end_time = 150000
    stock_volume_ratio_sort = find_stock_volume_ratio(trading_day, begin_time, end_time)
    select_code_list, stock_change_sort = find_defensive_stock_intrady(trading_day, begin_time, end_time)
    concat_df = pd.concat([stock_volume_ratio_sort, stock_change_sort], axis=1)
    concat_df.columns = ['volume_ratio', 'yield']
    sort_concat_df = concat_df.sort_values(by='yield', ascending=False)
    select_df = sort_concat_df.head(100)
    sort_select_df = select_df.sort_values(by='volume_ratio',ascending=False)
    stock_code_list = sort_select_df.head(50).index
    concept_set = find_stock_list_concept(stock_code_list, trading_day)
    get_sort_concept_yiled(concept_set, trading_day, out_file_folder)
    out_file_name = "..\\stock_data_task\\file_name.csv"
    sort_select_df.to_csv(out_file_name)




