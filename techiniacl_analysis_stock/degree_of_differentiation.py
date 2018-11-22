# -*- coding: utf-8 -*-
"""

# 计算股票分化程度对大盘择时，行业择时的影响

# 股票的分化程度参考申万宏源：基于分化度的行业择时，行业轮动策略；


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


def calc_stock_differentiation(trading_day, back_period, index_name):
    """
    计算当个交易日股票的分化程度；back_period代表用了前多少天的数据计算分离度；
    计算分离度有三种方法
    :param trading_day:
    :param back_period:
    :return:
    """
    begin_date = get_next_trading_day_stock(trading_day, -1 * back_period)
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\"'.format(start_date=begin_date, end_date=trading_day)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    df_table.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    df_table = df_table[(df_table.PCT_CHG > -12) & (df_table.PCT_CHG < 12)]
    df_table = df_table.set_index('code')

    # 只考虑指数中的股票，沪深300，上证50，或者中证500
    constituent_df = get_index_stock_list(index_name, trading_day)
    df_table = df_table.join(constituent_df)
    df_table = df_table.dropna(subset=['WEIGHT'])
    # stock_differentiation = calc_differentiation_by_corr(df_table)
    stock_differentiation = calc_differentiation_by_period_pct(df_table)
    return stock_differentiation


def calc_differentiation_by_period_pct(df_table):
    """
    根据区间的收益率标准差，计算股票的分化程度
    区间长度用back_period来表示
    :param df_table:
    :return:
    """
    stock_pct_dict = defaultdict()
    stock_code_list = df_table.index.unique()
    for stock_code in stock_code_list:
        if len(df_table.loc[stock_code]) == 11:
            cumprod_pct_array = (df_table.loc[stock_code].PCT_CHG / 100 + 1).cumprod()
            stock_pct_dict[stock_code] = (cumprod_pct_array.values[-1] - 1) * 100
    cumprod_pct_series = Series(stock_pct_dict)
    stock_differentiation = cumprod_pct_series.std()
    return stock_differentiation


def calc_differentiation_by_corr(df_table):
    """
    首先计算每个股票的收益率的相关性
    然后计算相关性的标准差来代表股票的分化程度
    :param df_table:
    :return:
    """
    stock_pct_dict = defaultdict()
    stock_code_list = df_table.index.unique()
    for stock_code in stock_code_list:
        if len(df_table.loc[stock_code]) == 11:
            pct_array = df_table.loc[stock_code].PCT_CHG.values
            stock_pct_dict[stock_code] = pct_array
    stock_pct_df = DataFrame(stock_pct_dict)
    corr_matrix = stock_pct_df.corr()
    np_corr_matrix = corr_matrix.as_matrix()
    unique_corr_matrix = np.triu(np_corr_matrix, 1)
    stock_differentiation = np.std(unique_corr_matrix[unique_corr_matrix > 0])
    return stock_differentiation


def calc_days_differentiation(start_date, end_date, index_name):
    """
    计算过去一段时间股票分化程度的变化
    :param start_date:
    :param end_date:
    :return:
    """
    back_period = 10
    differentiation_dict = defaultdict()
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        trading_day = change_trading_day_format(trading_day)
        if start_date <= trading_day <= end_date:
            print(trading_day)
            differentiation_dict[trading_day] = calc_stock_differentiation(trading_day, back_period, index_name)
    differentiation_series = Series(differentiation_dict)
    index_sh_df = get_index_data('000300.SH', start_date, end_date)
    index_sh_series = Series(index_sh_df.close.values, index=differentiation_series.index)
    index_pct_series = Series(index_sh_df.pct_chg.values, index=differentiation_series.index)
    # differentiation_std_series = differentiation_series / abs(index_pct_series)
    differentiation_ma_series = differentiation_series.rolling(window=10).mean()
    # differentiation_series.describe()
    # selected = differentiation_series[differentiation_series > 7.5]
    # print(selected)

    fig, ax = plt.subplots()
    ax.plot(index_sh_series, color='r', label="index sh series")
    ax1 = ax.twinx()
    # ax1.plot(oil_df['SPG_shift'], color="b", label="SPG shift")
    ax.plot(differentiation_series, color="b", label="differentiation ma series")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "index series and differentiation degree"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)


def trade_volume_shrink():
    """
    计算11.7~11.9那天大盘下跌，股票下跌但是成交量很小的情况；
    :param start_date:
    :param end_date:
    :return:
    """
    trading_day = '2018-11-09'
    begin_date = get_next_trading_day_stock(trading_day, -20)
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\"'.format(start_date=begin_date, end_date=trading_day)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    df_table.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    df_table['ma_3_volume'] = df_table.groupby('code')['VOLUME'].apply(lambda x: x.rolling(window=3).mean())
    df_table['ma_15_volume'] = df_table.groupby('code')['VOLUME'].apply(lambda x: x.rolling(window=15).mean())
    df_table['volume_ratio'] = df_table['ma_3_volume'] / df_table['ma_15_volume']
    select_df = df_table[df_table['time'] == change_trading_day_date_stock(trading_day)]
    sort_df = select_df.sort_values(by='volume_ratio')
    sort_df = sort_df[sort_df['AMT'] > 0]



if __name__ == '__main__':
    index_name = 'zz500'
    start_date = '2018-09-01'
    end_date = '2018-11-15'
    trading_day = '2018-11-05'
    hs300_differentation_series = differentiation_series
    zz500_differentation_series = differentiation_series
    sh50_differentiation_series = differentiation_series


