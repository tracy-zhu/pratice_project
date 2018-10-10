# -*- coding: utf-8 -*-
"""

# 计算沪深300指数期货和现货指数的相关性, 及其他指标

# 以及这样类似的策略

Tue 2018/02/06

@author: Tracy Zhu
"""
# 导入系统库
import sys
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *


index_spot_file_folder = "E:\\quote_data\\index_spot_data\\"
trading_day_list = get_trading_day_list()


def read_spot_index(index_code):
    file_name = index_spot_file_folder + index_code + '.csv'
    spot_df_temp = pd.read_csv(file_name, index_col="DateTime")
    time_index_list = []
    for str_index in spot_df_temp.index[:-1]:
        stamp = datetime.strptime(str_index, '%Y-%m-%d %H:%M:%S')
        time_index_list.append(stamp)
    spot_df = DataFrame(spot_df_temp.values[:-1], index=time_index_list, columns=spot_df_temp.columns)
    return spot_df


def read_future_data(instrument_id):
    future_df = DataFrame()
    start_date = "20180102"
    end_date = "20180122"
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


def concat_future_spot(future_df, spot_df):
    close_dict = {'future_close': future_df.close_price,
                  'spot_price': spot_df.close}
    close_df = DataFrame(close_dict)
    close_df_dropna = close_df.dropna(how='any')
    future_close = close_df_dropna.future_close
    spot_close = close_df_dropna.spot_price
    future_arr = np.array(future_close)
    spot_arr = np.array(spot_close)
    future_yield = np.diff(future_arr) / future_arr[:-1]
    spot_yield = np.diff(spot_arr) / spot_arr[:-1]
    # cor, pval = st.pearsonr(future_yield.values[1:], spot_yield.values[1:])
    cor, pval = st.pearsonr(future_yield, spot_yield)
    print "the correlation of spot index and future is " + str(cor)


def get_yield_arr(future_close, spot_close):
    future_yield = future_close.diff() / future_close.shift()
    spot_yield = spot_close.diff() / spot_close.shift()
    return future_yield, spot_yield


def plot_spread(future_close, spot_close):
    fig, ax = plt.subplots()
    ax.plot(future_close.values, color='r', label="future_close")
    ax.plot(spot_close.values, color="b", label="spot_close")
    ax.legend(loc="upper left")
    ax.legend(loc="upper right")
    title = "HS300_index & IF1802"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)


    fig, ax1 = plt.subplots()
    basis_spread = spot_close - future_close
    ax1.plot(basis_spread.values, color="r", label="basis spread")
    ax1.legend(loc="upper left")
    title = "basis spread"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)

    future_yield, spot_yield = get_yield_arr(future_close, spot_close)
    fig, ax2 = plt.subplots()
    ax2.plot(future_yield, spot_yield, 'ro',label="yield correlation")
    ax2.legend(loc="upper left")
    title = "basis spread"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)

if __name__ == '__main__':
    index_code = "000300"
    instrument_id = "IF1802"
    future_df = read_future_data(instrument_id)
    spot_df = read_spot_index(index_code)
    concat_future_spot(future_df, spot_df)

