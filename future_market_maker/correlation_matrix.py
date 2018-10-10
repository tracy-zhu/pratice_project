# -*- coding: utf-8 -*-
"""

# 本脚本分析tick数据, 计算合约组之间的相关性；

Tue 2017/12/28

@author: Tracy Zhu
"""
# 导入系统库
import sys
import itertools
import scipy.stats as st


# 导入用户库：
sys.path.append("..")
from price_prediction.price_prediction_low_frequency import *

trading_day_list = get_trading_day_list()

def get_vwap_yield(instrument_id, trading_day, frequency):
    resample_data = get_low_dimension_data(instrument_id, trading_day, frequency)
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    vwap_series = get_vwap_series(resample_data, unit)
    log_vwap_series = np.log(vwap_series)
    vwap_yield = log_vwap_series.diff()
    return vwap_yield


def get_days_vwap_yield(instrument_id, end_date, frequency, period):
    """
    函数将end_date前10天的收益率序列结合在一起
    :param instrument_id:
    :param end_date: 代表选取样本的最后一个交易日
    :param frequency:
    :param period:period代表是过去是多少天，10个交易日，一般是14
    :return:
    """
    total_vwap_yield = Series()
    start_date = get_next_trading_day(end_date, -1 * period)
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if start_date <= trading_day <= end_date:
            vwap_yield = get_vwap_yield(instrument_id, trading_day, frequency)
            total_vwap_yield = pd.concat([total_vwap_yield, vwap_yield])
    total_vwap_yield = total_vwap_yield.dropna()
    return total_vwap_yield


if __name__ == '__main__':
    frequency = "5min"
    period = 10
    end_date = "20180815"
    yield_dict = defaultdict()
    # instrument_id_list = ["I1809", "I1901","J1809", "J1901", "JM1809", "JM1901", "RB1810", "RB1901", "RB1905"]
    instrument_id_list = ["AL1809", "AL1810", "AL1811", "CU1809", "CU1810", "CU1811", "NI1811", "NI1901" , "ZN1809", "ZN1810", "ZN1811"]
    for instrument_id in instrument_id_list:
        print instrument_id
        vwap_yield = get_days_vwap_yield(instrument_id, end_date, frequency, period)
        yield_dict[instrument_id] = vwap_yield

    yield_data_frame = DataFrame(yield_dict)
    yield_data_frame = yield_data_frame.dropna(how="all")
    result = yield_data_frame.corr()
    # variety_id_list = []
    # for instrument_id in result.index:
    #     variety_id_list.append(get_variety_id(instrument_id))
    # result = DataFrame(result.values, index=result.index, columns=result.index)
    # result = result[instrument_id_list]
    # result.reindex(instrument_id_list)

    out_file_name = "..\\future_market_maker\\result\\correlation_matrix.csv"
    result.to_csv(out_file_name)


    f, ax = plt.subplots(figsize = (10, 4))
    cmap = sns.cubehelix_palette(start = 1, rot = 3, gamma=0.8, as_cmap = True)
    #sns.heatmap(result, cmap = "rainbow", linewidths = 0.05, ax = ax)
    sns.heatmap(result, annot=True, ax=ax, annot_kws={'size':9,'weight':'bold', 'color':'blue'})