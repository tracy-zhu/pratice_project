# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 09:14:58 2018

@author: Tracy Zhu
"""

import sys
import scipy.stats as st
from datetime import datetime

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *

trading_day_list = get_trading_day_list()


def read_a50_index(file_name):
    raw = pd.read_csv(file_name, header=0, index_col=0)
    raw = raw.dropna(how='any')
    time_index = []
    for index in raw.index:
        stamp_index = datetime.strptime(index, "%Y/%m/%d %H:%M")
        time_index.append(stamp_index)
    raw_df = pd.DataFrame(raw.values, index=time_index)
    return raw_df


def read_future_data(instrument_id):
    future_df = DataFrame()
    start_date = "20180201"
    end_date = "20180212"
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if start_date <= trading_day <= end_date:
            quote_data_temp = read_minute_data(instrument_id, trading_day)
            quote_data = change_date_with_time_index(quote_data_temp, trading_day)
            future_df = pd.concat([future_df, quote_data])
    return future_df


def change_date_with_time_index(quote_data, trading_day):
    """
    将quote_data转化为date_time为index
    :param quote_data:
    :param trading_day:
    :return:
    """
    time_index_list = []
    for update_time in quote_data.Update_Time:
        str_index = trading_day + " " + update_time
        stamp = datetime.strptime(str_index, "%Y%m%d %H:%M")
        time_index_list.append(stamp)
    df = DataFrame(quote_data.values, index=time_index_list, columns=quote_data.columns)
    return df


def concat_a50_IH(a50_df, IH_df):
    a50_df["IH_index"] = IH_df.close_price
    close_df = a50_df.sort_index()
    close_df_dropna = close_df.dropna(how='any')
    a50_index = close_df_dropna[0]
    IH_index = close_df_dropna.IH_index
    a50_yield = a50_index.diff() / a50_index.shift()
    IH_yield = IH_index.diff() / IH_index.shift()
    cor, pval = st.pearsonr(a50_yield.values[1:], IH_yield.values[1:])
    print "the correlation of spot index and future is " + str(cor)
    return a50_index, IH_index


def plot_a50_IH(a50_index, IH_index):
    fig, ax = plt.subplots()
    ax.plot(a50_index.values, color='r', label="a50_index")
    ax1 = ax.twinx()
    ax1.plot(IH_index.values, color="b", label="IH_index")
    ax1.legend(loc="upper left")
    ax.legend(loc="upper right")
    title = "a50_index & IH_index"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)


if __name__ == '__main__':
    file_name = ".\\wind_api\\a50_index.csv"
    instrument_id = "IH1802"
    a50_df = read_a50_index(file_name)
    IH_df = read_future_data(instrument_id)
    a50_index, IH_index = concat_a50_IH(a50_df, IH_df)

