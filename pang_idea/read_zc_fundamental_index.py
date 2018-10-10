# -*- coding: utf-8 -*-
"""

# 本脚本将庞总整理的基本面数据读入python

Tue 2017/08/21

@author: Tracy Zhu
"""
# 导入系统库
import sys
import matplotlib.pyplot as plt
import time

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *

data_file_folder = '..\\pang_idea\\data\\'
data_file_name = data_file_folder + 'zc_fundamental_index.xlsx'
xl = pd.ExcelFile(data_file_name)

def filter_raw_data(xl, sheet_index):
    df = xl.parse(xl.sheet_names[sheet_index], skiprows=10, index_col=0, header=None)
    return df
    # result_file_name = data_file_folder + xl.sheet_names[sheet_index] + '.csv'
    # df.to_csv(result_file_name)


def eliminate_seasonal_factor(df):
    pass


def normalization_data(series_data, period):
    series_sorted = series_data.sort_index()
    series_sorted = series_sorted.dropna()
    new_index = series_sorted.index[period - 1:]
    indicator_arr = series_sorted.values
    indicator_moving_average = moving_average(indicator_arr, period)
    indicator_moving_std = moving_std(indicator_arr, period)
    normalization_arr = indicator_moving_average / indicator_moving_std
    normalization_series = Series(normalization_arr, index=new_index)
    return normalization_series


def moving_average(arr, period):
    ret = np.cumsum(arr, dtype=float)
    ret[period:] = ret[period:] - ret[:-period]
    arr_moving_average = ret[period-1:] / period
    return arr_moving_average


def moving_std(arr, period):
    std_list = []
    for start_index in range(1, len(arr) - period + 2):
        moving_std_value = arr[start_index : start_index + period].std()
        std_list.append(moving_std_value)
    std_arr = np.array(std_list)
    return std_arr


def get_main_zc_data(xl):
    main_zc_price_dict = dict()
    sheet_index = 10
    zc_price_data = xl.parse(xl.sheet_names[sheet_index], skiprows=1, index_col=0, header=None)
    for time_index in zc_price_data.index:
        time_str = datetime.strftime(time_index, "%Y%m%d")
        month_str = time_str[4:6]
        if '04' <= month_str < '08':
            main_zc_price_dict[time_index] = zc_price_data.ix[time_index][3]
        elif '08' <= month_str < '12':
            main_zc_price_dict[time_index] = zc_price_data.ix[time_index][1]
        else:
            main_zc_price_dict[time_index] = zc_price_data.ix[time_index][2]
    main_zc_data = Series(main_zc_price_dict)
    main_zc_data = main_zc_data[main_zc_data.index > datetime(2013,9,28)] # exactly list time: 2013.9.26
    return main_zc_data


def stack_index_data(index_series):
    """
    将每个指标的转化为日期为行，年份为列的data_frame
    :param main_zc_data: 主力合约的series
    :return: 主力合约的data_frame, 列为年，行为交易日
    """
    first_year = index_series.index[0].year
    total_year_dict = defaultdict()
    year_dict = defaultdict(list)
    for i in range(1, len(index_series.index)):
        if index_series.index[i].year == first_year:
            datetime_index = index_series.index[i]
            day_index = str(datetime_index.month).zfill(2) + str(datetime_index.day).zfill(2)
            year_dict[day_index] = index_series[datetime_index]
        else:
            total_year_dict[first_year] = Series(year_dict)
            year_dict = defaultdict(list)
            first_year = index_series.index[i].year
    total_year_dict[first_year] = Series(year_dict)
    index_df = DataFrame(total_year_dict)
    """
        2013   2014   2015   2016   2017
    0102   NaN  566.0  491.6  312.0  503.4
    0103   NaN  562.4  484.0  306.2  503.4
    0104   NaN  562.4  484.0  306.2  503.4
    0105   NaN  563.2  484.0  306.2  503.4
    0106   NaN  559.0  484.0  306.2  495.6
    """
    return index_df


def get_change_ratio_mean(index_df):
    """
    计算2017年的值相对于前四年的变化值
    :param stack_df: stack_main_zc_data()得到的结果
    :return: change_ratio
    """
    stack_df = stack_index_data(index_df)
    pre_mean_stack_df = stack_df[[2013,2014,2015,2016]]
    pre_mean_series = pre_mean_stack_df.mean(axis=1, skipna=True)
    change_ratio = stack_df[2017] / pre_mean_series - 1
    change_ratio = change_ratio.dropna()
    return change_ratio


def get_basis_series(main_zc_data, zc_price_of_5500c):
    basis_series = zc_price_of_5500c - main_zc_data
    basis_series = basis_series.dropna()
    return basis_series


def data_definition(xl):
    # 5500卡煤炭现货价格，为期货交割品, start_date:2015.8.10
    zc_price_of_5500c = filter_raw_data(xl, sheet_index=1)[3]
    normalization_zc_price_of_5500c = normalization_data(zc_price_of_5500c, period=360)
    deviation_ratio_of_5500c_price = get_change_ratio_mean(zc_price_of_5500c)


    # 5000卡煤炭现货价格, start_date : 2015.8.10
    zc_price_of_5000c = filter_raw_data(xl, sheet_index=1)[4]
    normalization_zc_price_of_5000c = normalization_data(zc_price_of_5000c, period=360)
    deviation_ratio_of_5000c_price = get_change_ratio_mean(zc_price_of_5000c)

    # 宁波港5500卡煤炭现货价格, start_date: 2011.6.13
    zc_price_of_5500c_south = filter_raw_data(xl, sheet_index=1)[5]
    normalization_zc_price_of_5500c_south = normalization_data(zc_price_of_5500c_south, period=360)
    deviation_ratio_of_5500c_price_south = get_change_ratio_mean(zc_price_of_5500c_south)

    # 不同卡路里，每卡之间的价差, start_date: 根据现货价格
    price_spread_of_different_c = zc_price_of_5500c / 5500 - zc_price_of_5000c / 5000
    price_spread_of_different_c = price_spread_of_different_c.dropna()
    normalization_price_spread_of_c = normalization_data(price_spread_of_different_c, period=360)
    # price_spread_of_different_c.plot()
    deviation_of_price_spread_of_different_c = get_change_ratio_mean(price_spread_of_different_c)

    # 电厂总库存和煤炭日耗， 相除即得下游库销比, start_date: 2013.12.31
    power_total_inventory = filter_raw_data(xl, sheet_index=5)[7]
    normalization_power_total_inventory = normalization_data(power_total_inventory, period=360)
    daily_zc_consumption = filter_raw_data(xl, sheet_index=9)[1]
    downstream_inventory_consumption = power_total_inventory / daily_zc_consumption
    downstream_inventory_consumption = downstream_inventory_consumption.dropna()
    deviation_of_downstream_inventory_consumption = get_change_ratio_mean(downstream_inventory_consumption)

    # 港口库存和出库量， 相除即得到上游库销比, 上游库存单位为万吨, start_date: 2015.2.13
    upstream_inventory = filter_raw_data(xl, sheet_index=4)[1]
    for i in range(3, 6):
        upstream_inventory = upstream_inventory + filter_raw_data(xl, sheet_index=4)[i]
    upstream_inventory = upstream_inventory + filter_raw_data(xl, sheet_index=4)[8] / 10000
    upstream_inventory = upstream_inventory.dropna()

    # 获取基差序列, start_date: 2015.5.18
    main_zc_data = get_main_zc_data(xl)
    basis_series = get_basis_series(main_zc_data, zc_price_of_5500c)
    normalization_main_zc_data = normalization_data(main_zc_data, period=360)
    deviation_of_basis_series = get_change_ratio_mean(basis_series)
    deviation_of_main_zc_data = get_change_ratio_mean(main_zc_data)

    upstream_consumption = filter_raw_data(xl, sheet_index=3)[3]
    index_list = [5,14,16,22,25]
    for index in index_list:
        upstream_consumption = upstream_consumption + filter_raw_data(xl, sheet_index=3)[index]
    upstream_consumption.dropna()
    upstream_inventory_consumption = upstream_inventory / upstream_consumption
    upstream_inventory_consumption = upstream_inventory_consumption.dropna()
    deviation_of_upstream_inventory_consumption = get_change_ratio_mean(upstream_inventory_consumption)

    concat_data_frame = pd.concat([normalization_zc_price_of_5500c, normalization_zc_price_of_5000c,
                                   normalization_zc_price_of_5500c_south, normalization_price_spread_of_c,
                                   downstream_inventory_consumption, upstream_inventory_consumption,
                                   basis_series, normalization_main_zc_data], axis=1)
    concat_data_frame = concat_data_frame.dropna(how='any')
    concat_data_frame = DataFrame(concat_data_frame.values, columns=["normalization_zc_price_of_5500c",
                                                              "normalization_zc_price_of_5000c",
                                   "normalization_zc_price_of_5500c_south", "normalization_price_spread_of_c",
                                        "downstream_inventory_consumption", "upstream_inventory_consumption",
                                                                     "basis_series", "normalization_main_zc_data"],
                                  index=concat_data_frame.index)
    
    deviation_concat_data_frame = pd.concat([deviation_ratio_of_5500c_price, deviation_ratio_of_5000c_price,
                                             deviation_ratio_of_5500c_price_south, deviation_of_price_spread_of_different_c,
                                             deviation_of_downstream_inventory_consumption, deviation_of_upstream_inventory_consumption,
                                              deviation_of_main_zc_data], axis=1)
    index_list = []
    for index in deviation_concat_data_frame.index:
        index = '2017' + index
        index_time = datetime.strptime(index, '%Y%m%d')
        index_list.append(index_time)
    deviation_concat_data_frame = DataFrame(deviation_concat_data_frame.values, columns=['deviation_ratio_of_5500c_price', 'deviation_ratio_of_5000c_price',
                                             'deviation_ratio_of_5500c_price_south', 'deviation_of_price_spread_of_different_c',
                                             'deviation_of_downstream_inventory_consumption', 'deviation_of_upstream_inventory_consumption',
                                             'deviation_of_main_zc_data'], index=index_list)

    return concat_data_frame, deviation_concat_data_frame


if __name__ == '__main__':
    sheet_index_dict = {}
    sheet_index = 5
    period = 120
    raw_data = filter_raw_data(xl, sheet_index)
    indicator_series = raw_data[5]
    normalization_series = normalization_data(indicator_series, period)
    normalization_series.plot()

    main_zc_data = get_main_zc_data(xl)
    main_zc_df = stack_index_data(main_zc_data)
    change_of_2017 = get_change_ratio_mean(main_zc_data)
    concat_data_frame, deviation_concat_data_frame = data_definition(xl)
    num_periods = len(deviation_concat_data_frame)
    main_zc_data_series = Series(main_zc_df[2017].values[:num_periods], index=deviation_concat_data_frame.index)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    for column_names in deviation_concat_data_frame.columns:
        ax1.plot(deviation_concat_data_frame[column_names], label=column_names)
        ax1.legend(loc='best')


    ax2 = ax1.twinx()
    ax2.plot(main_zc_data_series,color='black', linewidth=4, label='main_zc_price')
    ax2.legend(loc='best')





