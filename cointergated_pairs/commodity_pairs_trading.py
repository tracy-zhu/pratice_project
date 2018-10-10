# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 本脚本用于生成淀粉玉米套利每日的参数，beta和std

@author: Tracy Zhu
"""

# 导入系统库
import sys, time, os
import logging
import shutil

# 导入用户库
sys.path.append("..")
from python_base.plot_method import *
now = datetime.now()
trading_day = now.strftime('%Y%m%d')
#trading_day = '20170703'
variety_id1 = 'Y1'
variety_id2 = 'OI'


def get_price_series(trading_day, instrument_date, variety_id1, variety_id2):
    rm_quote_data = read_minute_data(variety_id1 + instrument_date, trading_day)
    m_quote_data = read_minute_data(variety_id2 + instrument_date, trading_day)
    rm_close_price_series = Series(rm_quote_data.close_price.values,index=rm_quote_data.Update_Time)
    m_close_price_series = Series(m_quote_data.close_price.values, index=m_quote_data.Update_Time)
    concat_series = pd.concat([rm_close_price_series, m_close_price_series], axis=1)
    concat_series = concat_series.dropna(axis=0,how='any')
    raw_rm_close_price_series = Series(concat_series[0],name='X_data')
    raw_m_close_price_series = Series(concat_series[1],name='Y_data')
    rm_close_price_series = resample_time_index(raw_rm_close_price_series)
    m_close_price_series = resample_time_index(raw_m_close_price_series)
    return rm_close_price_series, m_close_price_series


def resample_time_index(price_series):
    result = 0
    night_data = price_series[price_series.index > '15:00']
    day_data = price_series[price_series.index <= '15:00']
    mor_data = day_data[day_data.index <= '11:30']
    noon_data =  day_data[day_data.index > '11:30']
    #new_price_series = pd.concat([night_data, day_data])
    int_hour = time.localtime().tm_hour
    if 8 <= int_hour <= 9:
        result = night_data
        if len(night_data) < 20:
            result = noon_data
    elif int_hour == 10:
        result = mor_data
    elif 12 <= int_hour <= 13:
        result = mor_data
    elif 16 <= int_hour <= 19:
        result = noon_data
    return result


def linear_model_main(price_series_1, price_series_2):
    X = price_series_2
    result = (sm.OLS(price_series_1, X)).fit()
    # constant_para = result.params.const
    coef_para = result.params.X_data
    Z_data = price_series_1 - price_series_2 * coef_para
    err_std = Z_data.std()
    return coef_para, err_std


if __name__ == '__main__':
    close_price_series1, close_price_series2 = get_price_series(trading_day, '801',variety_id1, variety_id2)
    beta1, std1 = linear_model_main(close_price_series2, close_price_series1)

    out_put_file_name = "D:\\pairs_trading_parameter\\" + variety_id1 + variety_id2 +"_parameter_result_file_801.txt"
    out_put_file = open(out_put_file_name, 'wb')
    line1 = 'the beta is ' + str(beta1) + '\n'
    line2 = 'the std is ' + str(std1) + '\n'
    out_put_file.write(line1)
    out_put_file.write(line2)
    out_put_file.close()

    close_price_series1, close_price_series2 = get_price_series(trading_day, '709', variety_id1, variety_id2)
    beta2, std2 = linear_model_main(close_price_series2, close_price_series1)

    out_put_file_name = "D:\\pairs_trading_parameter\\" + variety_id1 + variety_id2 + "_parameter_result_file_709.txt"
    out_put_file = open(out_put_file_name, 'wb')
    line1 = 'the beta is ' + str(beta2) + '\n'
    line2 = 'the std is ' + str(std2) + '\n'
    out_put_file.write(line1)
    out_put_file.write(line2)
    out_put_file.close()
