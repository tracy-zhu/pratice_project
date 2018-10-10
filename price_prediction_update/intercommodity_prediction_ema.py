# -*- coding: utf-8 -*-
"""

# 该脚本主要针对论文上的改进，对跨品种的预测进行改进, 并采用每个品种变化的ema值做自变量

Tue 2018/2/26

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from price_prediction_update.price_prediction_ema import *


def get_independent_instrument(instrument_id_group, dependent_instrument_id):
    independent_instrument_list = instrument_id_group[:]
    independent_instrument_list.remove(dependent_instrument_id)
    return independent_instrument_list


def independent_variable_df_generation_update(instrument_id_group, trading_day):
    """
    得出每个合约的msp_diff, 和MSP的dataframe
    :param instrument_id_group:
    :param trading_day:
    :return:
    """
    instrument_id = instrument_id_group[0]
    instrument_dict, msp_dict = get_independent_dict_instrument(instrument_id, trading_day)
    independent_df = DataFrame(instrument_dict)
    msp_df = DataFrame(msp_dict)
    for instrument_id in instrument_id_group[1:]:
        print instrument_id
        instrument_dict, msp_dict = get_independent_dict_instrument(instrument_id, trading_day)
        for independent_name, independent_value in instrument_dict.items():
            print independent_name
            new_independent_value = drop_duplicate_index(independent_value)
            independent_df[independent_name] = new_independent_value
        for independent_name, msp_series in msp_dict.items():
            print independent_name
            new_msp = drop_duplicate_index(msp_series)
            msp_df[independent_name] = new_msp
    return independent_df, msp_df


def get_tv_data_frame(independent_df, msp_df):
    """
    计算每个合约的tv序列，运用之前的msp_diff,和msp序列
    :param independent_df: msp_diff
    :param msp_df: msp_series
    :return:
    """
    independent_columns = independent_df.columns
    msp_columns = msp_df.columns
    tv_dict = defaultdict()
    for i in range(len(independent_columns)):
        independent_column = independent_columns[i]
        msp_column = msp_columns[i]
        instrument_id = independent_columns[i].split('_')[0]
        tv_series = 0.5 * independent_df.sum(axis=1) - independent_df[independent_column] + msp_df[msp_column]
        tv_dict[instrument_id] = tv_series
    return tv_dict


def compare_tv_to_mid_price(instrument_id, trading_day, tv_dict):
    """
    将计算出来的tv_series和中间价做比较，看差距有多大；
    :param instrument_id:
    :param trading_day:
    :param tv_dict:
    :return:
    """
    quote_data = read_data(instrument_id, trading_day)
    time_index = get_time_index(quote_data)
    mid_price = (quote_data.Bid_Price1 + quote_data.Ask_Price1) / 2
    mid_price.index = time_index
    tv_series = tv_dict[instrument_id]


def get_independent_dict_instrument(instrument_id, trading_day):
    alpha = 0.99
    ema_diff_series, msp_series = get_msp_ema(instrument_id, trading_day, alpha)
    independent_dict = {instrument_id + "_ema_diff": ema_diff_series}
    msp_dict = {instrument_id + "_msp": msp_series}
    # independent_df = DataFrame(independent_dict)
    return independent_dict, msp_dict


def drop_duplicate_index(independent_value):
    """
    将具有重复index的series去掉
    :param independent_value:
    :return:
    """
    duplicate_value = independent_value[independent_value.index.duplicated()]
    new_independent_value = independent_value.drop(duplicate_value.index)
    return new_independent_value


def ema_function(raw_list, alpha):
    """
    根据alpha和初始价格序列，计算出他的ema序列
    :param np_array:
    :param alpha:
    :return:
    """
    ema_list = []
    ema_list.append(raw_list[0])
    for i, price in enumerate(raw_list):
        if i >= 1:
            ema_list.append(alpha * ema_list[i - 1] + (1 - alpha) * price)
    return ema_list


def get_msp_ema(instrument_id, trading_day, alpha):
    """
    根据第一步计算msp_series计算msp_ema序列
    :param instrument_id:
    :param trading_day:
    :return:
    """
    _, msp_series = linear_model_update_ema(instrument_id, trading_day)
    ema_list = ema_function(list(msp_series), alpha)
    ema_series = Series(ema_list, index=msp_series.index)
    ema_diff = msp_series - ema_series
    # ema_diff = ema_diff.shift()
    return ema_diff, msp_series


def get_dependent_variable_ema(instrument_id, trading_day, forecast_num):
    """
    得到李老师更改的策略的因变量
    :param dependent_instrument_id:
    :param trading_day:
    :param forecast_num:
    :return:
    """
    _, msp_series = linear_model_update_ema(instrument_id, trading_day)
    quote_data = read_data(instrument_id, trading_day)
    time_index = get_time_index(quote_data)
    variety_id = get_variety_id(instrument_id)
    tick, unit, _ = get_variety_information(variety_id)
    vwap_series = get_vwap_series(quote_data, unit)
    vwap_arr = np.array(vwap_series)
    msp_arr = np.array(msp_series)
    vwap_diff_list = [np.nan] * forecast_num
    for i in range(len(vwap_arr) - forecast_num):
        vwap_diff = float(sum(vwap_arr[i+1: i+forecast_num+1])) / float(forecast_num) - msp_arr[i]
        vwap_diff_list.append(vwap_diff)
    diff_series = Series(vwap_diff_list, index=time_index)
    dependent_variable = diff_series.shift(-1)
    return dependent_variable


def intercommodity_prediction_update(dependent_instrument_id, instrument_id_group, trading_day, forecast_num):
    dependent_variable = get_dependent_variable_ema(dependent_instrument_id, trading_day, forecast_num)
    dependent_variable = drop_duplicate_index(dependent_variable)
    independent_df = independent_variable_df_generation_update(instrument_id_group, trading_day)
    independent_df["dependent_variable"] = dependent_variable
    independent_dropna = independent_df.dropna(how='any')
    Y = independent_dropna["dependent_variable"]
    X = independent_dropna.drop('dependent_variable', 1)
    result = (sm.OLS(Y, X)).fit()
    print result.summary()
    return result.params
    # out_file_name = "..\\price_prediction_update\\" + dependent_instrument_id + "_params.csv"
    # f = open(out_file_name, 'wb')
    # print result.params
    # for params_value in result.params:
    #     print>>f, params_value
    # f.close()


if __name__ == '__main__':
    trading_day = "20180528"
    out_file_folder = "..\\price_prediction_update\\params_folder\\"
    out_file_name = out_file_folder + "correlation.csv"
    f = open(out_file_name, 'wb')

    instrument_id_group = ["RB1810", "RB1901", "JM1809", "J1809"]
    for dependent_instrument_id in instrument_id_group:
        # dependent_instrument_id = "RB1805"
        print dependent_instrument_id
        forecast_num = 20
        # independent_instrument_list = get_independent_instrument(instrument_id_group, dependent_instrument_id)
        params_series = intercommodity_prediction_update(dependent_instrument_id, instrument_id_group, trading_day, forecast_num)
        str_line = (',').join(params_series.astype('str')) + '\n'
        f.write(str_line)

    f.close()
