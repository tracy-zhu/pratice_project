# -*- coding: utf-8 -*-
"""

# 本脚本分析tick数据, 计算每个合约的波动率，得到波动率向量；

Tue 2018/4/11

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
    # variety_id = get_variety_id(instrument_id)
    # tick, unit, _ = get_variety_information(variety_id)
    # vwap_series = get_vwap_series(resample_data, unit)
    # log_vwap_series = np.log(vwap_series)
    log_vwap_series = np.log(resample_data.Last_Price)
    vwap_yield = log_vwap_series.diff()
    return vwap_yield


def get_days_vwap_yield(instrument_id, end_date, frequency, period):
    """
    函数将end_date前10天的收益率序列结合在一起
    :param instrument_id:
    :param end_date: 代表选取样本的最后一个交易日
    :param frequency:
    :param period:period代表是过去是多少天，10个交易日
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


def get_realized_volatility(vwap_yield, period):
    """
    根据计算出的收益率序列计算已实现波动率
    :param vwap_yield:
    :return:
    """
    rv = math.sqrt(sum([i*i for i in vwap_yield]))
    annualized_volatility = rv / math.sqrt(period) * math.sqrt(252)
    # annualized_volatility = math.sqrt(annualized_volatility)
    return annualized_volatility


if __name__ == '__main__':
    volatility_dict = defaultdict()
    frequency = "5min"
    period = 10
    # instrument_id = "AL1805"

    instrument_id_list = ["RB1810", "RB1901", "JM1809", "J1809"]
    end_date = "20180706"
    for instrument_id in instrument_id_list:
        total_vwap_yield = get_days_vwap_yield(instrument_id, end_date, frequency, period)
        annualized_volatility = get_realized_volatility(total_vwap_yield, period)
        volatility_dict[instrument_id] = annualized_volatility
        print instrument_id, annualized_volatility
