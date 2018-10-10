# -*- coding: utf-8 -*-
"""

# 根据光大证券一个择时策略，20170501-光大证券-光大证券技术择时系列报告之一：基于阻力支撑相对强度（RSRS）的市场择时这篇研报，自己实现进行研究；

Mon 2018/09/03

@author: Tracy Zhu
"""

from __future__ import division
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels import regression
import matplotlib.pyplot as plt
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *


def cal_rsrs(data2, data1, N):
    """
    计算data2中标的所在日期的RSRS斜率指标和拟合优度
    """
    data11 = data1[data1['sec_code'].isin(data2['sec_code'])].reset_index()
    loc = data11[data11['tradeday'].isin(data2['tradeday'])].index.tolist()
    if loc[0] >= N:
        x = sm.add_constant(data11['low_slice'][(loc[0] - N):loc[0]]).astype('float64')
        y = data11['high_slice'][(loc[0] - N):loc[0]].astype('float64')
        est = sm.OLS(y, x)
        res = est.fit()
        params = res.params.low_slice
        r_squared = res.rsquared
    else:
        params = None
        r_squared = None
    data2['rsrs'] = params
    data2['r_squared'] = r_squared
    return data2


def rsrs(data, N):
    """
    由日频数据计算RSRS斜率指标和拟合优度
    """
    data = data.dropna()
    data['tradeday'] = pd.to_datetime(data['tradeday'], format='%Y/%m/%d %H:%M:%S')
    data.sort_values(by=['sec_code', 'tradeday'], inplace=True)
    data1 = data.copy()
    data1 = data1.groupby(['sec_code', 'tradeday']).apply(lambda x, data1=data1, N=N: cal_rsrs(x, data1, N))
    print("RSRS斜率指标和拟合优度已计算")

    return data1


def cal_rsrs_std(data2, data1, M, N):
    """
    计算data2中标的所在日期的RSRS标准分
    """
    data11 = data1[data1['sec_code'].isin(data2['sec_code'])].reset_index()
    loc = data11[data11['tradeday'].isin(data2['tradeday'])].index.tolist()
    # print(loc[0])
    rsrs = data2['rsrs']
    if loc[0] < M + N:
        rsrs_std = None
    else:
        rsrs_mean = np.mean(data11['rsrs'][(loc[0] - M):loc[0]])
        rsrs_s = np.std(data11['rsrs'][(loc[0] - M):loc[0]])
        rsrs_std = (rsrs - rsrs_mean) / rsrs_s
    data2['rsrs_std'] = rsrs_std
    return data2


def rsrs_std(data1, M, N):
    """
    由RSRS斜率计算RSRS标准分
    """
    data2 = data1.groupby(['sec_code', 'tradeday']).apply(lambda x, data1=data1, M=M, N=N: cal_rsrs_std(x, data1, M, N))
    print("RSRS标准分已计算")
    return data2


def rsrs_std_cor(data2):
    """
    由RSRS标准分计算RSRS修正标准分
    """
    data2['rsrs_std_cor'] = data2['r_squared'] * data2['rsrs_std']
    print('RSRS修正标准分已计算')
    return data2


def rsrs_std_cor_right(data2):
    """
    由RSRS修正标准分计算RSRS右偏修正标准分
    """
    data2['rsrs_std_cor_right'] = data2['rsrs_std_cor'] * data2['rsrs']
    print('RSRS右偏修正标准分已计算')
    return data2


def rsrs_std_cor_right_mean(data2, ndays=5):
    """
    计算RSRS右偏修正标准分的ndays均线
    """
    data2['rsrs_std_cor_right_mean'] = data2.groupby('sec_code')['rsrs_std_cor_right'].apply(pd.rolling_mean, ndays)
    print('RSRS右偏修正标准分均线已计算')
    return data2


def calc_ma_line(data2):
    """
    计算每只股票的均线数据
    :param data2:
    :return:
    """
    data2['MA_20'] = data2.groupby('sec_code')['close_slice'].apply(lambda x: x.rolling(window=20).mean())
    print('20日均线已计算')
    return data2


def get_rsrs(data, N, M, ndays=5):
    """
    根据日频数据计算RSRS相关指标
    data 数据，包括：标的代码sec_code,交易日tradeday,最高价high_slice、最低价low_slice、收盘价close_slice
    N，回归时间窗口，默认取16，不足16赋值为None
    M，标准分计算窗口，默认取300，不足300赋值为None
    """
    data1 = rsrs(data, N)
    data2 = rsrs_std(data1, M, N)
    data2 = rsrs_std_cor(data2)
    data2 = rsrs_std_cor_right(data2)
    data2 = rsrs_std_cor_right_mean(data2, ndays)
    data2 = calc_ma_line(data2)
    return data2


def get_signal(data2, S):
    """
    根据RSRS指标和阈值S判断是否有交易信号（最简单的情况）,trade_dir为0代表买入，为1代表卖出，为-1代表无信号
    """
    data3 = data2.copy()
    data3.ix[(data3['rsrs_std_cor_right'] > S) & (data3['trade_dir'] == -1), 'trade_dir'] = 0
    data3.ix[(data3['rsrs_std_cor_right'] > S) & (data3['trade_dir'] == 1), 'trade_dir'] = -1

    data3.ix[(data3['rsrs_std_cor_right'] < -S) & (data3['trade_dir'] == -1), 'trade_dir'] = 1
    data3.ix[(data3['rsrs_std_cor_right'] < -S) & (data3['trade_dir'] == 0), 'trade_dir'] = -1
    # data3.drop(['rsrs','r_squared','rsrs_std','rsrs_std_cor','rsrs_std_cor_right'], axis = 1, inplace = True)
    return data3


def get_signal_with_ma(data2, S):
    """
    在原有的基础上，增加均线的设定进行计算；
    :param data2:
    :param S:
    :return:
    """
    data3 = data2.copy()
    data3['ma_signal'] = data3.groupby('sec_code')['MA_20'].apply(lambda x: x.shift(1) - x.shift(4))
    data3.ix[(data3['rsrs_std_cor_right'] > S) & (data3['trade_dir'] == -1), 'trade_dir'] = 0
    data3.ix[(data3['rsrs_std_cor_right'] > S) & (data3['trade_dir'] == 1), 'trade_dir'] = -1

    data3.ix[(data3['rsrs_std_cor_right'] < -S) & (data3['trade_dir'] == -1), 'trade_dir'] = 1
    data3.ix[(data3['rsrs_std_cor_right'] < -S) & (data3['trade_dir'] == 0), 'trade_dir'] = -1
    # data3.drop(['rsrs','r_squared','rsrs_std','rsrs_std_cor','rsrs_std_cor_right'], axis = 1, inplace = True)
    return data3



def RSRS(data, N, M, S=0.7, ndays=5):
    """
    根据日频数据计算RSRS相关指标，并判断交易信号，更新trade_dir,删除中间变量
    """
    data2 = get_rsrs(data, N, M, ndays)
    data3 = get_signal_with_ma(data2, S)
    return data3


class Context():
    """
    所有策略的参数在这里初始化
    :param context:
    :return:
    """
    def __init__(self, start_date, end_date, S):
        self.start_date = start_date
        self.end_date = end_date
        self.S = S
        self.sec_code = '000300.SH'


def trans_cumprod_pct(pct_chg_series):
    """
    将日收益率序列转化成累计收益率序列
    """
    cumprod_pct = (1 + pct_chg_series / 100).cumprod()
    return cumprod_pct


def trans_cumprod_pct_with_limit_loss(pct_chg_series, limit_loss):
    """
    将日收益率转化为累计收益率序列，包含止盈止损, 这不是累计收益率序列；是单词收益率
    :param pct_chg_series:
    :return:
    """
    pct_chg_list = list(pct_chg_series)
    period_hold_percent = 1
    period_hold_percent_list = []
    hold_percent_list = [1 + float(pct_chg_list[0]) / 100]
    flag = 0
    for index, pct_chg in enumerate(pct_chg_list[:-1]):
        if index >= 1:
            period_hold_percent = period_hold_percent * (1 + float(pct_chg) / 100)
            loss_pct = period_hold_percent - 1
            if loss_pct < limit_loss:
                print loss_pct
                pct_chg = 0
                flag = 1
            if pct_chg != 0 and pct_chg_list[index+1] == 0:
                print "that's switch"
                period_hold_percent = 1
                flag = 0
            if flag == 1:
                pct_chg = 0
            cumprod_pct = hold_percent_list[-1] * (1 + float(pct_chg) / 100)
            hold_percent_list.append(cumprod_pct)
            period_hold_percent_list.append(period_hold_percent)
    period_hold_percent_series = Series(period_hold_percent_list)
    holding_cumprod_pct_with_limit_loss = Series(hold_percent_list, index=pct_chg_series.index)
    return holding_cumprod_pct_with_limit_loss, period_hold_percent_series


def analysis_period_hold(period_hold_percent_series):
    """
    分析每次的持仓收益进行统计, 获取每段的最终收益，最大回撤；
    :param period_hold_pct_series:
    :return:
    """
    condition_list = []
    final_hold_pct_list = []
    max_drawback_list = []
    temp_hold_pct_list = []
    period_hold_pct_list = list(period_hold_percent_series)
    for index, pct_chg in enumerate(period_hold_pct_list[:-1]):
        temp_hold_pct_list.append(pct_chg)
        if pct_chg != 1 and period_hold_pct_list[index+1] == 1:
            max_drawback = Series(temp_hold_pct_list).min()
            final_hold_pct = temp_hold_pct_list[-1]
            temp_hold_pct_list = []
            max_drawback_list.append(max_drawback)
            final_hold_pct_list.append(final_hold_pct)
            condition_list.append((final_hold_pct, max_drawback))
    period_hold_percent_series[period_hold_percent_series != 1].hist()
    Series(max_drawback_list).plot()
    Series(final_hold_pct_list).hist()


def back_test_by_indicator(indicator_series, contxet):
    """
    根据生成的指标序列，对过去一段时间进行回测，得到收益率序列
    :param indicator_series:
    :return:
    """
    global context
    bilateral_fee = 0.004
    trade_times = 0
    position_list = []
    df_300 = get_index_data("000300.SH", context.start_date, context.end_date)
    index_series = pd.to_datetime(df_300['time'], format='%Y/%m/%d %H:%M:%S')
    pct_chg_series = Series(df_300.pct_chg.values, index=index_series)
    # pct_chg_series = Series(index_df.pct_chg.values, index=index_df.time)


    position = 0
    for indicator in indicator_series:
        if position == 0:
            if indicator > context.S:
                position = 1
        elif position != 0:
            if indicator < -1 * context.S:
                position = 0
                trade_times += 1
        # 上面一个if代表不做空，下面一个代表做空
        # if position == 0:
        #     if indicator > context.S:
        #         position = 1
        #     elif indicator < -1 * context.S:
        #         position = -1
        # elif position == -1:
        #     if indicator > context.S:
        #         position = 1
        # elif position == 1:
        #     if indicator < -1 * context.S:
        #         position = -1
        position_list.append(position)
    print "trade times is " + str(trade_times)
    position_series = Series(position_list, index=indicator_series.index)
    holding_pct_series = pct_chg_series.shift(-1) * position_series
    holding_pct_series.dropna(inplace=True)
    pct_chg_series = pct_chg_series[pct_chg_series.index >= holding_pct_series.index[0]]
    holding_cumprod_pct = trans_cumprod_pct(holding_pct_series)
    index_cumprod_pct = trans_cumprod_pct(pct_chg_series)
    total_fee = trade_times * bilateral_fee
    holding_cumprod_pct.plot()
    # holding_cumprod_pct_with_limit_loss.plot()
    index_cumprod_pct.plot()
    return holding_cumprod_pct, index_cumprod_pct, total_fee


def back_test_by_indicator_upgrade(data_ind, contxet):
    """
    根据生成的指标序列，对过去一段时间进行回测，得到收益率序列
    和上面的函数不同的是，接受的是最后生成的矩阵data_ind为参数
    :param indicator_series:
    :return:
    """
    global context
    position_list = []
    trade_times = 0
    data_ind.dropna(subset=['rsrs_std_cor_right'], inplace=True)
    df_300 = get_index_data("000300.SH", context.start_date, context.end_date)
    index_series = pd.to_datetime(df_300['time'], format='%Y/%m/%d %H:%M:%S')
    pct_chg_series = Series(df_300.pct_chg.values, index=index_series)
    # pct_chg_series = Series(index_df.pct_chg.values, index=index_df.time)


    position = 0
    for index in data_ind.index:
        indicator = data_ind.loc[index]['rsrs_std_cor_right']
        ma_signal = data_ind.loc[index]['ma_signal']
        if position == 0:
            if indicator > context.S and ma_signal > 0:
                position = 1
        elif position != 0:
            if indicator < -1 * context.S:
                position = 0
                trade_times += 1
        # 上面一个if代表不做空，下面一个代表做空
        # if position == 0:
        #     if indicator > context.S and ma_signal > 0:
        #         position = 1
        #     elif indicator < -1 * context.S and ma_signal < 0:
        #         position = -1
        # elif position == -1:
        #     if indicator > context.S and ma_signal > 0:
        #         position = 1
        # elif position == 1:
        #     if indicator < -1 * context.S and ma_signal < 0:
        #         position = -1
        position_list.append(position)
    print "trade times is " + str(trade_times)
    position_series = Series(position_list, index=data_ind.tradeday)
    holding_pct_series = pct_chg_series.shift(-1) * position_series
    holding_pct_series.dropna(inplace=True)
    pct_chg_series = pct_chg_series[pct_chg_series.index >= holding_pct_series.index[0]]
    index_cumprod_pct = trans_cumprod_pct(pct_chg_series)
    holding_cumprod_pct_upgrade = trans_cumprod_pct(holding_pct_series)
    holding_cumprod_pct_upgrade.plot()
    # holding_cumprod_pct_with_limit_loss.plot()
    # index_cumprod_pct.plot()
    return holding_cumprod_pct_upgrade, index_cumprod_pct


def calc_evaluation_index(holding_cumprod_pct):
    """
    根据策略收益率序列计算出策略的参数：夏普比，最大回撤，年化收益率
    :param holding_cumprod_pct:
    :return:
    """
    trading_days = len(holding_cumprod_pct)
    annulized_return = float(holding_cumprod_pct.values[-1] + 1) ** (float(252) / float(trading_days)) - 1
    sharpe_ratio = holding_cumprod_pct.mean() / (holding_cumprod_pct.std() + 1e-8) * float(252) ** 0.5
    res = pd.DataFrame()
    max_value = -999
    for index_name in holding_cumprod_pct.index[1:]:
        if not np.isnan(holding_cumprod_pct.loc[index_name]):
            max_value = max(max_value, holding_cumprod_pct.loc[index_name])
        res.loc[index_name, 'drawback'] = float(holding_cumprod_pct.loc[index_name]) / float(max_value) - 1
    max_drowback = res['drawback'].min()
    print "annulized return is {}%".format(annulized_return * 100)
    print "sharp ratio is {}".format(sharpe_ratio)
    print "max drawback is {}%".format(max_drowback * 100)
    return annulized_return, sharpe_ratio, max_drowback


def get_minute_data(index_code, start_date, end_date, period):
    """
    获取指定频率的指数的分钟数据
    :param index_code:
    :param start_date:
    :param end_date:
    :param period:
    :return:
    """
    index_df = get_index_minute_data(index_code, start_date, end_date)
    resample_df = index_df.copy()
    if period != '1min':
        resample_df = transfer_index_minute_data_period(index_df, period)
    data = resample_df[['time', 'thscode', 'open', 'high', 'low', 'close']]
    data.rename(columns={'time': 'tradeday', 'thscode': 'sec_code', 'open': 'open_slice', 'high': 'high_slice',
                         'low': 'low_slice', 'close': 'close_slice'}, inplace=True)
    data['trade_dir'] = -1
    return data


if __name__ == '__main__':
    start_date = '2004-01-01'
    end_date = '2018-10-08'
    period = '1min'
    index_code = '000300.SH'
    S = 0.7
    N = 16
    M = 300
    limit_loss = -0.12
    df_300 = get_index_data("000300.SH", start_date, end_date)
    df_001 = get_index_data("000001.SH", start_date, end_date)
    data = pd.concat([df_300, df_001])
    data = data[['time', 'code', 'open', 'high', 'low', 'close']]
    data.rename(columns={'time': 'tradeday', 'code': 'sec_code', 'open': 'open_slice', 'high': 'high_slice',
                         'low': 'low_slice', 'close': 'close_slice'}, inplace=True)
    data['trade_dir'] = -1
    # data = get_minute_data(index_code, start_date, end_date, period)
    data_ind = RSRS(data, N=16, M=300, S=0.7, ndays=5)
    data_ind = data_ind[data_ind.sec_code == '000300.SH']
    indicator_series = Series(data_ind['rsrs_std_cor_right'].values, index=data_ind.tradeday)
    indicator_series = indicator_series.dropna()
    indicator_series.tail(10)
    context = Context(start_date, end_date, S)
    holding_cumprod_pct, index_cumprod_pct, total_fee = back_test_by_indicator(indicator_series, context)
    # holding_cumprod_pct_with_limit_loss =  trans_cumprod_pct_with_limit_loss(holding_cumprod_pct, limit_loss)
    holding_cumprod_pct_upgrade, _ = back_test_by_indicator_upgrade(data_ind, context)
    annulized_return, sharpe_ratio, max_drawback = calc_evaluation_index(holding_cumprod_pct)
    index_annulized_return, index_sharpe_ratio, index_drawback = calc_evaluation_index(index_cumprod_pct)
    #limit_loss_annulized_return, limit_loss_sharpe_ratio, limit_loss_drawback = calc_evaluation_index(holding_cumprod_pct_with_limit_loss)
    annulized_return_upgrade, sharpe_ratio_upgrade, max_drawback_upgrade = calc_evaluation_index(holding_cumprod_pct_upgrade)

