# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 09:14:58 2018

@author: Tracy Zhu
"""
from WindPy import w

import sys
import scipy.stats as st
from datetime import datetime

# 导入用户库：
sys.path.append("..")
out_file_folder = "..\\wind_api\\picture\\"
from python_base.plot_method import *


def download_option_data(start_date, end_date, var_symbol):
    """
    下载指定日期的指定期权的分钟收盘价数据
    :param start_date:"2018-02-05 09:00:00"
    :param end_date:
    :param var_symbol:"10001110.SH"
    :return:
    """
    if w.isconnected() == False:
        w.start()
    raw = w.wsi(var_symbol, "close", start_date, end_date, "")
    raw_df = pd.DataFrame(raw.Data, index=raw.Codes, columns=raw.Times)
    raw_df = raw_df.T
    return raw_df


def read_a50_index(file_name):
    raw = pd.read_csv(file_name, header=0, index_col=0)
    raw = raw.dropna(how='any')
    time_index = []
    for index in raw.index:
        stamp_index = datetime.strptime(index, "%Y/%m/%d %H:%M")
        time_index.append(stamp_index)
    raw_df = pd.DataFrame(raw.values, index=time_index)
    return raw_df


def concat_and_analysis(option_df, a50_df):
    """
    首先将期权数据和a50数据结合起来
    :param option_df:
    :param a50_df:
    :return:
    """
    concat_df = pd.concat([option_df, a50_df], axis=1)
    concat_df = concat_df.dropna(how='any')
    option_df_new = concat_df["10001110.SH"]
    a50_df_new = concat_df[0]
    a50_yield = a50_df_new.diff() / a50_df_new
    option_yield = option_df_new.diff() / option_df_new
    cor, pval = st.pearsonr(a50_yield.values[1:], option_yield.values[1:])
    print "the correlation of a50 index and option is " + str(cor)


if __name__ == '__main__':
    start_date = "2018-02-05 09:00:00"
    end_date = "2018-02-12 12:30:00 "
    var_symbol = "10001110.SH"
    file_name = ".\\wind_api\\a50_index.csv"
    option_df = download_option_data(start_date, end_date, var_symbol)
    a50_df = read_a50_index(file_name)
