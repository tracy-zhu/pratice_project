# -*- coding: utf-8 -*-
"""

# 本脚本用于分析通过API累计的比特币order book数据

Tue 2018/2/13

@author: Tracy Zhu
"""
# 导入系统库
import sys
import numpy as np
from pandas import DataFrame, Series
import matplotlib.pyplot as plt
import statsmodels.api as sm
sys.path.append("..")



def read_order_book(file_name):
    f = open(file_name, "r")
    all_lines = f.readlines()
    data_num = len(all_lines) / 3
    bid_ask_spread_list = []
    mid_price_list = []
    bid_price1_list = []
    ask_price1_list = []
    bid_volume1_list = []
    ask_volume1_list = []
    ask_price2_list = []
    bid_price2_list = []
    ask_volume2_list = []
    bid_volume2_list = []
    ask_price3_list = []
    bid_price3_list = []
    ask_volume3_list = []
    bid_volume3_list = []
    ask_price4_list = []
    bid_price4_list = []
    ask_volume4_list = []
    bid_volume4_list = []
    ask_price5_list = []
    bid_price5_list = []
    ask_volume5_list = []
    bid_volume5_list = []
    update_time_list = []
    vwap_list = []
    lee_ready_vol_list = []
    lee_read_ratio_list = []
    for i in range(data_num):
        mid_price_line = all_lines[3*i]
        bid_price_line = all_lines[3*i + 1]
        ask_price_line = all_lines[3*i + 2]
        update_time_list.append(mid_price_line.split(',')[0])
        mid_price = float(mid_price_line.split(',')[1])
        if mid_price_line.split(',')[2] != "None":
            vwap = float(mid_price_line.split(',')[2])
        else:
            vwap = np.nan
        lee_ready_vol = float(mid_price_line.split(',')[3])
        if mid_price_line.split(',')[4] != "None\n":
            lee_ready_ratio = float(mid_price_line.split(',')[4])
        else:
            lee_ready_ratio = np.nan
        bid_price1 = float(bid_price_line.split(',')[1])
        bid_volume1 = float(bid_price_line.split(',')[2])
        bid_price2 = float(bid_price_line.split(',')[3])
        bid_volume2 =float(bid_price_line.split(',')[4])
        bid_price3 = float(bid_price_line.split(',')[5])
        bid_volume3 =float(bid_price_line.split(',')[6])
        bid_price4 = float(bid_price_line.split(',')[7])
        bid_volume4 =float(bid_price_line.split(',')[8])
        bid_price5 = float(bid_price_line.split(',')[9])
        bid_volume5 =float(bid_price_line.split(',')[10])
        ask_price1 = float(ask_price_line.split(',')[1])
        ask_volume1 =float(ask_price_line.split(',')[2])
        ask_price2 = float(ask_price_line.split(',')[3])
        ask_volume2 =float(ask_price_line.split(',')[4])
        ask_price3 = float(ask_price_line.split(',')[5])
        ask_volume3 =float(ask_price_line.split(',')[6])
        ask_price4 = float(ask_price_line.split(',')[7])
        ask_volume4 =float(ask_price_line.split(',')[8])
        ask_price5 = float(ask_price_line.split(',')[9])
        ask_volume5 =float(ask_price_line.split(',')[10])
        bid_ask_spread = ask_price1 - bid_price1
        bid_ask_spread_list.append(bid_ask_spread)
        bid_price1_list.append(bid_price1)
        bid_volume1_list.append(bid_volume1)
        bid_price2_list.append(bid_price2)
        bid_volume2_list.append(bid_volume2)
        bid_price3_list.append(bid_price3)
        bid_volume3_list.append(bid_volume3)
        bid_price4_list.append(bid_price4)
        bid_volume4_list.append(bid_volume4)
        bid_price5_list.append(bid_price5)
        bid_volume5_list.append(bid_volume5)
        ask_price1_list.append (ask_price1)
        ask_volume1_list.append(ask_volume1)
        ask_price2_list.append (ask_price2)
        ask_volume2_list.append(ask_volume2)
        ask_price3_list.append (ask_price3)
        ask_volume3_list.append(ask_volume3)
        ask_price4_list.append (ask_price4)
        ask_volume4_list.append(ask_volume4)
        ask_price5_list.append (ask_price5)
        ask_volume5_list.append(ask_volume5)
        mid_price_list.append(mid_price)
        vwap_list.append(vwap)
        lee_ready_vol_list.append(lee_ready_vol)
        lee_read_ratio_list.append(lee_ready_ratio)

    order_book_dict = {"mid_price":mid_price_list, "bid_price1":bid_price1_list, "bid_volume1":bid_volume1_list,
                                                    "ask_price1":ask_price1_list, "ask_volume1":ask_volume1_list,
                       "bid_price2":bid_price2_list, "bid_volume2":bid_volume2_list,
                                                    "ask_price2":ask_price2_list, "ask_volume2":ask_volume2_list,
                        "bid_price3":bid_price3_list, "bid_volume3":bid_volume3_list,
                        "ask_price3":ask_price3_list, "ask_volume3":ask_volume3_list,
                        "bid_price4":bid_price4_list, "bid_volume4":bid_volume4_list,
                        "ask_price4":ask_price4_list, "ask_volume4":ask_volume4_list,
                       "bid_price5":bid_price5_list, "bid_volume5":bid_volume5_list,
                        "ask_price5":ask_price5_list, "ask_volume5":ask_volume5_list, "bid_ask_spread": bid_ask_spread_list,
                       "vwap":vwap_list, "lee_ready_vol": lee_ready_vol_list, "lee_ready_ratio":lee_read_ratio_list}
    order_book_df = DataFrame(order_book_dict, index=update_time_list)
    return order_book_df


def get_order_imbalance_ratio(order_book_df, depth_level):
    bid_ask_spread = order_book_df.ask_price1 - order_book_df.bid_price1
    order_imbalance_ratio = 0
    if depth_level == 1:
        order_imbalance_ratio = (order_book_df['bid_volume1'] - order_book_df['ask_volume1']) / (order_book_df['bid_volume1'] + order_book_df['ask_volume1'])
    elif depth_level == 2:
        order_imbalance_ratio = (order_book_df['bid_volume1'] + order_book_df['bid_volume2'] - order_book_df['ask_volume1'] - order_book_df['ask_volume2']) /\
                    (order_book_df['bid_volume1'] + order_book_df['bid_volume2'] + order_book_df['ask_volume1'] + order_book_df['ask_volume2'])
    elif depth_level == 3:
        total_bid_volume = order_book_df['bid_volume1'] + order_book_df['bid_volume2'] + order_book_df['bid_volume3']
        total_ask_volume = order_book_df['ask_volume1'] + order_book_df['ask_volume2'] + order_book_df['ask_volume3']
        order_imbalance_ratio = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
    elif depth_level == 4:
        total_bid_volume = order_book_df['bid_volume1'] + order_book_df['bid_volume2'] + order_book_df['bid_volume3'] + order_book_df['bid_volume4']
        total_ask_volume = order_book_df['ask_volume1'] + order_book_df['ask_volume2'] + order_book_df['ask_volume3'] + order_book_df['ask_volume4']
        order_imbalance_ratio = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
    elif depth_level == 5:
        total_bid_volume = order_book_df['bid_volume1'] + order_book_df['bid_volume2'] + order_book_df['bid_volume3']\
                           + order_book_df['bid_volume4'] + order_book_df['bid_volume5']
        total_ask_volume = order_book_df['ask_volume1'] + order_book_df['ask_volume2'] + order_book_df['ask_volume3']\
                           + order_book_df['ask_volume4'] + order_book_df['ask_volume5']
        order_imbalance_ratio = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)

    # order_imbalance_ratio = order_imbalance_ratio / bid_ask_spread
    return order_imbalance_ratio


def get_order_imbalance(order_book_df):
    bid_ask_spread = order_book_df.ask_price1 - order_book_df.bid_price1
    bid_product = order_book_df['bid_volume1'] * order_book_df['bid_price1']
    ask_product = order_book_df['ask_volume1'] * order_book_df['ask_price1']
    order_imbalance = (bid_product - ask_product) / (bid_product + ask_product)
    # order_imbalance = order_imbalance / bid_ask_spread
    return order_imbalance


def get_mid_price_deviation(order_book_df):
    vwap_price_series = order_book_df['vwap']
    mid_price_series = order_book_df['mid_price']
    mid_price_deviation = vwap_price_series - mid_price_series
    return mid_price_deviation


def get_independent_variable(order_book_df):
    order_imbalance_ratio1 = get_order_imbalance_ratio(order_book_df, 1)
    order_imbalance_ratio2 = get_order_imbalance_ratio(order_book_df, 2)
    order_imbalance_ratio3 = get_order_imbalance_ratio(order_book_df, 3)
    order_imbalance_ratio4 = get_order_imbalance_ratio(order_book_df, 4)
    order_imbalance_ratio5 = get_order_imbalance_ratio(order_book_df, 5)
    order_imbalance = get_order_imbalance(order_book_df)
    middle_price_momentum = order_book_df['mid_price'].diff(5)
    vwap_momentum = order_book_df['vwap'].diff(5)
    mid_price_deviation = get_mid_price_deviation(order_book_df)
    lee_ready_vol = order_book_df["lee_ready_vol"]
    lee_ready_ratio = order_book_df['lee_ready_ratio']
    # bid_ask_spread = order_book_df.ask_price1 - order_book_df.bid_price1
    # middle_price_momentum = middle_price_momentum / bid_ask_spread
    concat_dict = {"order_imbalance_ratio1": order_imbalance_ratio1, "order_imbalance_ratio2": order_imbalance_ratio2,
                   'order_imbalance': order_imbalance, 'middle_price_momentum': middle_price_momentum, "mid_price_deviation": mid_price_deviation,
                   'lee_ready_vol':lee_ready_vol, 'lee_ready_ratio':lee_ready_ratio, 'vwap_momentum':vwap_momentum,
                   "order_imbalance_ratio3": order_imbalance_ratio3, "order_imbalance_ratio4": order_imbalance_ratio4, "order_imbalance_ratio5":order_imbalance_ratio5}
    independent_variable = DataFrame(concat_dict)
    return independent_variable


def get_dependent_variable(order_book_df, forecast_num):
    index_arr = order_book_df.index
    vwap_arr = np.array(order_book_df['mid_price'])
    vwap_diff_list = [np.nan] * forecast_num
    for i in range(len(vwap_arr) - forecast_num):
        vwap_diff = float(sum(vwap_arr[i+1: i+forecast_num+1])) / float(forecast_num) - vwap_arr[i]
        vwap_diff_list.append(vwap_diff)
    diff_series = Series(vwap_diff_list, index=index_arr)
    dependent_variable = diff_series.shift(-1)
    return dependent_variable


def get_dependent_variable_vwap(order_book_df, forecast_num):
    index_arr = order_book_df.index
    vwap_arr = np.array(order_book_df['vwap'])
    vwap_diff_list = [np.nan] * forecast_num
    for i in range(len(vwap_arr) - forecast_num):
        vwap_diff = float(sum(vwap_arr[i+1: i+forecast_num+1])) / float(forecast_num) - vwap_arr[i]
        vwap_diff_list.append(vwap_diff)
    diff_series = Series(vwap_diff_list, index=index_arr)
    dependent_variable = diff_series.shift(-1)
    return dependent_variable


def analysis_order_book(order_book_df):
    forecast_num = 4
    dependent_variable = get_dependent_variable(order_book_df, forecast_num)
    independent_variable = get_independent_variable(order_book_df)
    independent_variable['dependent_variable'] = dependent_variable
    temp_df = independent_variable.dropna(how='any')
    Y = temp_df['dependent_variable']
    X = temp_df.drop('dependent_variable', 1)
    result = (sm.OLS(Y, X)).fit()
    prediction_Y = (X * result.params).sum(axis=1)
    # prediction_Y.hist()
    # count, bins, _ = plt.hist(np.array(prediction_Y), 30, normed=True)
    # mu = prediction_Y.mean()
    # sigma = prediction_Y.std()
    # # normed是进行拟合的关键
    # # count统计某一bin出现的次数，在Normed为True时，可能其值会略有不同
    # plt.plot(bins, 1./(np.sqrt(2*np.pi)*sigma)*np.exp(-(bins-mu)**2/(2*sigma**2)))
    # plt.show()
    print(prediction_Y.describe())
    print(result.summary())


if __name__ == '__main__':
    file_name = "..\\bitcoin\\order_book_data_1.txt"
    order_book_df = read_order_book(file_name)
    analysis_order_book(order_book_df)

