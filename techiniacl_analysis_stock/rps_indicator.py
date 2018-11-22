# -*- coding: utf-8 -*-
"""

# 计算市场相对强弱指标RPS, 代表市场当前的趋势强度，

# RPS_1 = (当前涨跌幅 - Min(250交易日涨幅））/ (max(250交易日涨幅）-min(250交易日涨幅）)
 RPS = MA(RPS, 10)

# 可以用于指数和个股，欧奈尔值关注RPS值在80%以上的股票；

# 想法参考于《基于相对强弱下单向波动差值应用》

Tue 2018/11/06

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *
from python_base.plot_method import *

trading_day_list = get_trading_day_list()


def calc_rps_index(index_df):
    """
    接受一个stock_df, 计算他的rps值
    :param stock_df:
    :return:
    """
    back_period = 250
    pct_chg_series = index_df['pct_chg']
    index_df['rps_1'] = (pct_chg_series - pct_chg_series.rolling(window=back_period).min()) / (pct_chg_series.rolling(window=back_period).max()- pct_chg_series.rolling(window=back_period).min())
    index_df['RPS'] = index_df['rps_1'].rolling(window=30).mean()
    return index_df


def calc_rps_stock(end_date):
    """
    计算每个股票的rps值
    :param start_date:
    :param end_date:
    :return:
    """
    back_period = 250
    start_date = get_next_trading_day_stock(end_date, -1 * (back_period + 12))
    sql = 'SELECT time, code, CLOSE, PCT_CHG FROM stock_db.daily_price_qfq_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=end_date)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    df_table.columns = ['time', 'code', 'CLOSE', 'PCT_CHG']
    df_table['rps_1'] = df_table.groupby('code')['PCT_CHG'].apply(lambda x: (x - x.rolling(window=back_period).min()) / (x.rolling(window=back_period).max() - x.rolling(window=back_period).min()))
    df_table['RPS'] = df_table.groupby('code')['rps_1'].apply(lambda x: x.rolling(window=10).mean())
    select_df = df_table[df_table.time >= change_trading_day_date_stock(end_date)]
    select_df = select_df.sort_values(by=['RPS'], ascending=False)
    select_df = select_df[select_df.RPS > 0.8]
    print(select_df)


def plot_rps(index_df):
    """
    接受一个计算好的stock_df, 计算他的rps值
    :param stock_df:
    :return:
    """
    # index_df = index_df[index_df.time >= change_trading_day_date_stock('2018-01-01')]
    fig, ax = plt.subplots()
    ax.plot(index_df['close'], color='r', label="index sh series")
    ax1 = ax.twinx()
    # ax1.plot(oil_df['SPG_shift'], color="b", label="SPG shift")
    ax1.plot(index_df['RPS'], color="b", label="RPS series")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "index series and RPS series"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)


if __name__ == '__main__':
    start_date = '2008-01-01'
    end_date = '2018-11-20'
    # calc_rps_stock(end_date)
    index_code = '000300.SH'
    index_df = get_index_data(index_code, start_date, end_date)
