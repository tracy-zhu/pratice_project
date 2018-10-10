# -*- coding: utf-8 -*-
"""

# 本脚本分析tick数据, 用回归分析预测价格走势

Tue 2017/12/28

@author: Tracy Zhu
"""
# 导入系统库
import sys
import itertools
import scipy.stats as st
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# 导入用户库：
sys.path.append("..")
from price_prediction.lee_ready_algorithm import *


def get_vwap_series(quote_data, unit):
    """
    返回每个tick的成交均价序列，对于没有成交的tick，函数是用前成交均价代替
    :param instrument_id:
    :param trading_day:
    :return:
    """
    average_price = quote_data.Turnover.diff() / quote_data.Total_Match_Volume.diff() / unit
    # print len(average_price)
    # print len(average_price.dropna())
    average_price_fillna = average_price.fillna(method="ffill")
    return average_price_fillna


def calc_no_change_tick_ratio(variety_id):
    trading_day_list = get_trading_day_list()
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day > "20171201":
            instrument_id, _ = get_variety_main(variety_id, trading_day)
            tick, unit, _ = get_variety_information(variety_id)
            quote_data = read_data(instrument_id, trading_day)
            average_price = quote_data.Turnover.diff() / quote_data.Total_Match_Volume.diff() / unit
            no_trading_ratio = float(len(average_price.dropna())) / len(average_price)
            print trading_day + " , " + str(no_trading_ratio)


def get_no_trading_duration(instrument_id, trading_day):
    """
    函数生成的是一个序列，每个值为当笔交易距离上一笔有交易的间隔时间，
    以tick计数
    :param instrument_id:
    :param trading_day:
    :return:
    """
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    tick_match_volume_series = quote_data.Total_Match_Volume.diff()
    trading_duration_list = [np.nan]
    trading_duration = 0
    for tick_match_volume in tick_match_volume_series.values[1:]:
        if tick_match_volume != 0:
            trading_duration += 1
            trading_duration_list.append(trading_duration)
            trading_duration = 0
        else:
            trading_duration += 1
            trading_duration_list.append(np.nan)
    trading_duration_series = Series(trading_duration_list, index=tick_match_volume_series.index)
    return trading_duration_series


def regression_tick_data_dropna(instrument_id, trading_day):
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    trading_power_difference_arr, _ = lee_ready_algorithm_deform(instrument_id, trading_day)
    trading_power_difference_series = Series(trading_power_difference_arr, index=quote_data.index)
    trading_power_difference_series = trading_power_difference_series.fillna(0)
    average_price = quote_data.Turnover.diff() / quote_data.Total_Match_Volume.diff() / unit
    quote_data["VWAP"] = average_price
    quote_data['volume_direction'] = trading_power_difference_series
    quote_data["order_balance"] = get_order_balance_series(quote_data)
    quote_data["vwap_momentum"] = get_vwap_series(quote_data, unit)
    quote_data["vwap_deviation"] = get_vwap_deviation_from_middle_price(quote_data, unit)
    quote_data["trading_duration"] = get_no_trading_duration(instrument_id, trading_day)
    quote_data_dropna = quote_data.dropna(subset=["trading_duration"])
    dependent_variable = Series(quote_data_dropna["VWAP"].diff().values)
    independent_variable_df = DataFrame(quote_data_dropna[["vwap_deviation", "order_balance", "volume_direction", "vwap_momentum", "trading_duration"]].loc[range(quote_data_dropna.index[3], quote_data_dropna.index[-1])].dropna().values,
                                        columns=["vwap_deviation", "order_balance", "volume_direction", "vwap_momentum", "trading_duration"])
    in_sample_rsquared, out_sample_rsquared = linear_model_main_prediction(dependent_variable, independent_variable_df)
    return in_sample_rsquared, out_sample_rsquared


def combination_of_independent_variable_regression_dropna(quote_data_dropna, independent_variable_list):
    """
    选取自变量的所有不同的排列组合，分别进行回归，将方程回归结果输出
    此函数是已经将没有交易数据的tick行情删除得到的回归
    :param quote_data_dropna:去除掉没有交易行情的数据文件
    :param independent_variable_list: 自变量变量名列表
    :return: 不同自变量的回归模型结果
    """
    independent_variable_list = ["vwap_deviation", "order_balance", "volume_direction", "vwap_momentum", "trading_duration"]
    dependent_variable = Series(quote_data_dropna["VWAP"].diff().values)
    for x in xrange(len(independent_variable_list)):
        for i in itertools.combinations(independent_variable_list,x+1):
            #print list(i)
            k = list(i)
            if len(k) in [1,5]:
                independent_variable_df = DataFrame(quote_data_dropna[k].loc[range(quote_data_dropna.index[3], quote_data_dropna.index[-1])].dropna().values,
                                                    columns=k)
                in_sample_rsquared, _ = linear_model_main_prediction(dependent_variable, independent_variable_df)


def get_order_balance_series(quote_data):
    """
    (bid_price1 * bid_volume1 - ask_price1 * ask_volume1) / (bid_price1 * bid_volume1 + ask_price1 * ask_volume1)
    :param quote_data:
    :return:
    """
    bid_product_series = quote_data.Bid_Price1 * quote_data.Bid_Volume1
    ask_product_series = quote_data.Ask_Price1 * quote_data.Ask_Volume1
    order_balance_series = (bid_product_series - ask_product_series) / (bid_product_series + ask_product_series)
    return order_balance_series


def get_order_imbalance_ratio(quote_data):
    order_imbalance_ratio = (quote_data.Bid_Volume1 - quote_data.Ask_Volume1) /  (quote_data.Bid_Volume1 - quote_data.Ask_Volume1)
    return order_imbalance_ratio


def get_vwap_deviation_from_middle_price(quote_data, unit):
    average_price = quote_data.Turnover.diff() / quote_data.Total_Match_Volume.diff() / unit
    average_price_fillna = average_price.fillna(method="ffill")
    #vwap_deviation_series = average_price_fillna - (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    # order_weighted_price = (quote_data.Bid_Price1 * quote_data.Bid_Volume1 + quote_data.Ask_Price1 * quote_data.Ask_Volume1) \
    #                         / (quote_data.Bid_Volume1 + quote_data.Ask_Volume1)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    weighted_mid_price = (middle_price_series + middle_price_series.shift()) / 2
    vwap_deviation_series = average_price_fillna - weighted_mid_price
    return vwap_deviation_series


def get_momentum_factor_vwap(quote_data, unit, lag_num):
    """
    计算出vwap的动量因子，采取的是前两个行情的vwap变化
    :param instrument_id:
    :param trading_day:
    :return:
    """
    average_price = quote_data.Turnover.diff() / quote_data.Total_Match_Volume.diff() / unit
    average_price_fillna = average_price.fillna(method="ffill")
    momentum_vwap = average_price_fillna.diff(lag_num)
    return momentum_vwap


def get_independent_variable_df(instrument_id, trading_day):
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    trading_power_difference_arr, _ = lee_ready_algorithm_deform(instrument_id, trading_day)
    trading_power_difference_series = Series(trading_power_difference_arr)
    trading_power_difference_series = trading_power_difference_series.fillna(0)
    average_price_fillna = get_vwap_series(quote_data, unit)
    vwap_deviation_series = get_vwap_deviation_from_middle_price(quote_data, unit)
    order_balance_series = get_order_balance_series(quote_data)
    vwap_momentum_series = get_momentum_factor_vwap(quote_data, unit)
    # data = {"VWAP_Pre": average_price_fillna.values[1:-1],
    #         "Volume_Direction":trading_power_difference_series.values[1:-1],
    #         "Order_Balance": order_balance_series.values[1:-1]}
    data = {"vwap_deviation": vwap_deviation_series.values[3:-1],
            "volume_direction": trading_power_difference_series.values[3:-1],
            "order_balance": order_balance_series.values[3:-1],
            "vwap_momentum": vwap_momentum_series.values[3:-1]}
    independent_variable_df = DataFrame(data)
    return independent_variable_df


def combination_of_independent_variable_regression(average_price_fillna, independent_variable_df):
    """
    选取自变量的所有不同的排列组合，分别进行回归，将方程回归结果输出
    :param quote_data_dropna:去除掉没有交易行情的数据文件
    :param independent_variable_list: 自变量变量名列表
    :return: 不同自变量的回归模型结果
    """
    independent_variable_list = ["vwap_deviation", "order_balance", "volume_direction", "vwap_momentum"]
    dependent_variable = average_price_fillna.diff()
    for x in xrange(len(independent_variable_list)):
        for i in itertools.combinations(independent_variable_list,x+1):
            #print list(i)
            k = list(i)
            if len(k) in [1, 4]:
                selected_independent_df = independent_variable_df[k]
                in_sample_rsquared, _ = linear_model_main_prediction(dependent_variable, selected_independent_df)


def price_change_stat(average_price):
    """
    统计成交均价的特征值，没有交易的笔数，成交均价变化的分布
    :param average_price:
    :return:
    """
    tick = 5
    average_price_dropna = average_price.dropna()
    no_trading_num = len(average_price) - len(average_price_dropna)
    print "No trading ratio is " + str(float(no_trading_num) / float(len(average_price)))
    average_tick_diff = average_price_dropna.diff() / tick
    no_change_num = len(average_tick_diff[average_tick_diff==0])
    print "no change tick num ratio is " + str(float(no_change_num) / float(len(average_price)))
    change_above_1_tick_num = len(average_tick_diff[abs(average_tick_diff) >= 1])
    change_above_half_tick_num = len(average_tick_diff[abs(average_tick_diff) >= 0.5])
    print "change above half tick ratio is " + str(float(change_above_half_tick_num) / float(len(average_price)))
    print "change above 1 tick ratio is " + str(float(change_above_1_tick_num) / float(len(average_price)))


def draw_acf_pacf(average_price_fillna, lags=31):
    f = plt.figure(facecolor='white')
    ax1 = f.add_subplot(211)
    plot_acf(average_price_fillna, lags=31, ax=ax1)
    ax2 = f.add_subplot(212)
    plot_pacf(average_price_fillna, lags=31, ax=ax2)
    plt.show()


def linear_model_main_prediction(dependent_variable, independent_variable_df):
    """
    函数选取样本量的前2/3作为训练样本，后1/3作为样本外检验
    :param dependent_variable:
    :param independent_variable_df:
    :return:
    """
    total_num = len(dependent_variable)
    in_sample_num = total_num / 3 * 2
    Y = Series(dependent_variable.values[4:][:in_sample_num])
    X = independent_variable_df[:in_sample_num]
    #X = sm.add_constant(x)
    result = (sm.OLS(Y, X)).fit()
    out_sample_Y = Series(dependent_variable.values[4:])[in_sample_num:]
    out_sample_X = independent_variable_df[in_sample_num:]
    prediction_Y = (out_sample_X * result.params).sum(axis=1)
    out_sample_r_squared = calc_r_square(out_sample_Y, prediction_Y)
    print result.summary()
    # print "in sample R_squared is " + str(result.rsquared)
    # print "out sample R_squared is " + str(out_sample_r_squared)
    return result.rsquared, out_sample_r_squared


def calc_r_square(raw_data, prediction_data):
    # raw_data = out_sample_Y
    # prediction_data = prediction_Y
    total_num = len(raw_data)
    var_y = raw_data.var()
    SSE = ((prediction_data - raw_data) ** 2).sum()
    R_squared = 1 - float(SSE) / float(var_y * (total_num - 1))
    return R_squared


def regression_all_tick_data(instrument_id, trading_day):
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    average_price_fillna = get_vwap_series(quote_data, unit)
    dependent_variable = average_price_fillna.diff()
    # quote_data = read_data(instrument_id, trading_day)
    # middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    # dependent_variable = middle_price_series.diff()
    independent_variable_df = get_independent_variable_df(instrument_id, trading_day)
    in_sample_rsquared, out_sample_rsquaed = linear_model_main_prediction(dependent_variable, independent_variable_df)
    return in_sample_rsquared, out_sample_rsquaed


def single_factor_analysis(instrument_id, trading_day):
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    quote_data = read_data(instrument_id, trading_day)
    average_price_fillna = get_vwap_series(quote_data, unit)
    independent_variable_df = get_independent_variable_df(instrument_id, trading_day)
    combination_of_independent_variable_regression(average_price_fillna, independent_variable_df)


def correlation_vwap_and_middle_price_change(instrument_id, trading_day):
    """
    函数对vwap价格的变化以及middle_price_change的变化相关性
    :param instrument_id:
    :param trading_day:
    :return:
    """
    quote_data = read_data(instrument_id, trading_day)
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    vwap_series = get_vwap_series(quote_data, unit)
    middle_price_series = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    middle_price_change = middle_price_series.diff()
    vwap_series_change = vwap_series.diff()
    concat_data_frame = pd.concat([middle_price_change, vwap_series_change],axis=1)
    concat_data_frame_dropna = concat_data_frame.dropna(subset=[1])
    selected_list = []
    for index in concat_data_frame_dropna.index:
        if abs(concat_data_frame_dropna.ix[index][0]) >= 10:
            selected_list.append(abs(concat_data_frame_dropna.ix[index][1]))
    selected_series = Series(selected_list)
    selected_series.describe()


if __name__ == '__main__':
    # result_file_name = "..\\markt_maker\\result\\r_squared_result_dropna.csv"
    # f = open(result_file_name, "wb")
    # f.write("trading_day, in_sample ,out_sample\n")
    # instrument_id = "AL1802"
    # trading_day_list = get_trading_day_list()
    # for trade_day in trading_day_list:
    #     trading_day = trade_day[:-1]
    #     if trading_day > "20171217":
    #         print trading_day
    #         in_sample_rsquared, out_sample_rsquared = regression_tick_data_dropna(instrument_id, trading_day)
    #         str_line = trading_day + "," + str(in_sample_rsquared) + "," + str(out_sample_rsquared) + "\n"
    #         f.write(str_line)
    instrument_id = "AL1803"
    trading_day = "20180111"
    in_sample_rsquared, _  = regression_all_tick_data(instrument_id, trading_day)
