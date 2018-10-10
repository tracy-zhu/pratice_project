# -*- coding: utf-8 -*-
"""

# 找出大盘下跌的时候，按照股票的收益率进行排序

# 比较抗跌的股票在后市中是否有好的影响；

Tue 2018/03/06

@author: Tracy Zhu
"""

# 导入系统库
import sys
from WindPy import w

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *
from python_base.plot_method import *


def find_defensive_stock(start_date, end_date, select_num):
    """
    找出选出的股票组合中，收益率排名靠前的股票
    :param stock_df:
    :return:
    """
    stock_change_dict = defaultdict()
    stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', start_date, end_date)
    raw_stock_code_list = stock_df.code.unique()
    stock_code_list = delete_new_stock(raw_stock_code_list, 60, start_date)
    index_df = get_index_data("000300.SH", start_date, end_date)
    index_yield = index_df['pct_chg'].sum()
    for stock_code in stock_code_list:
        # stock_code = stock_code_list[0]
        if stock_code[:3] != '300':
            selected_df = stock_df[stock_df['code']==stock_code]
            total_percent_change = selected_df["PCT_CHG"].sum() - index_yield
            stock_change_dict[stock_code] = total_percent_change
    stock_change_series = Series(stock_change_dict)
    stock_change_sort = stock_change_series.sort_values(ascending=False)
    select_code_list = stock_change_sort.index[:select_num]
    return select_code_list, stock_change_sort


def find_defensive_stock_without_high_volatility(start_date, end_date, select_num):
    """
    找出指定的时间段中，股票涨幅排名靠前的股票，与上一个函数有所不同的是：在股票中，将有交易日
    涨幅过大的股票删除掉了，避免高波动性的股票被选入当中
    :param stock_df:
    :return:
    """
    limit_high_percent = 8
    stock_change_dict = defaultdict()
    stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', start_date, end_date)
    raw_stock_code_list = stock_df.code.unique()
    stock_code_list = delete_new_stock(raw_stock_code_list, 60, start_date)
    index_df = get_index_data("000300.SH", start_date, end_date)
    index_yield = index_df['pct_chg'].sum()
    for stock_code in stock_code_list:
        # stock_code = stock_code_list[0]
        if stock_code[:3] != '300':
            selected_df = stock_df[stock_df['code']==stock_code]
            if selected_df["PCT_CHG"].max() < limit_high_percent:
                total_percent_change = selected_df["PCT_CHG"].sum() - index_yield
                stock_change_dict[stock_code] = total_percent_change
    stock_change_series = Series(stock_change_dict)
    stock_change_sort = stock_change_series.sort_values(ascending=False)
    select_code_list = stock_change_sort.index[:select_num]
    return select_code_list, stock_change_sort


def volume_ratio_stock_sort(start_date, end_date):
    """
    找出某个交易日（大跌过程中，换手率（或成交量比例排名靠前的股票）
    :param start_date:
    :param end_date:
    :return:
    """
    stock_free_turn_dict = defaultdict()
    stock_volume_ratio_dict = defaultdict()
    stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', start_date, end_date)
    raw_stock_code_list = stock_df.code.unique()
    stock_code_list = delete_new_stock(raw_stock_code_list, 60, start_date)
    index_df = get_index_data("000300.SH", end_date, end_date)
    index_yield = index_df['pct_chg'].sum()
    for stock_code in stock_code_list:
        # stock_code = stock_code_list[0]
        selected_df = stock_df[stock_df['code']==stock_code]
        now_day_free_turn = selected_df.FREE_TURN.values[-1]
        now_day_yield = selected_df.PCT_CHG.values[-1]
        if now_day_free_turn != -999 and now_day_yield >= 0: #index_yield:
            stock_free_turn_dict[stock_code] = now_day_free_turn
            now_trade_volume = selected_df.VOLUME.values[-1]
            pre_trade_volume = selected_df.VOLUME.values[:-1]
            volume_ratio = float(now_trade_volume) / np.mean(pre_trade_volume)
            stock_volume_ratio_dict[stock_code] = volume_ratio
    stock_change_series = Series(stock_free_turn_dict)
    free_turn_sort = stock_change_series.sort_values(ascending=False).head(100)
    stock_volume_series = Series(stock_volume_ratio_dict)
    stock_volume_sort = stock_volume_series.sort_values(ascending=False).head(100)
    return free_turn_sort, stock_volume_sort


def get_select_stock_trend(select_code_list, after_start, after_end):
    """
    统计选出来的股票，在选出后相对指数的收益率
    :param select_code_list: 选出来的指数列表，指数选取为HS300；
    :param after_start:统计的开始时间段
    :param after_end:统计的结束时间段
    :return:
    """
    stock_change_dict = defaultdict()
    stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', after_start, after_end)
    index_df = get_index_data("000300.SH", after_start, after_end)
    index_yield = index_df['pct_chg'].sum()
    for stock_code in select_code_list:
        selected_df = stock_df[stock_df['code']==stock_code]
        total_percent_change = selected_df["PCT_CHG"].sum()
        if total_percent_change > -100:
            stock_change_dict[stock_code] = total_percent_change - index_yield
    stock_change_series = Series(stock_change_dict)
    return stock_change_series


def correlation_yield_before_after(stock_change_sort, after_start, after_end):
    """
    根据stock_change_sort选取的股票，将之后的走势和前面的走势对应起来
    :param stock_change_sort:
    :param after_start:
    :param after_end:
    :return:
    """
    stock_change_dict = defaultdict()
    stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', after_start, after_end)
    index_df = get_index_data("000300.SH", after_start, after_end)
    index_yield = index_df['pct_chg'].sum()
    select_code_list = stock_change_sort.index
    for stock_code in select_code_list:
        selected_df = stock_df[stock_df['code']==stock_code]
        total_percent_change = selected_df["PCT_CHG"].sum()
        stock_change_dict[stock_code] = total_percent_change - index_yield
    after_stock_change_series = Series(stock_change_dict)
    concat_df = pd.concat([stock_change_sort, after_stock_change_series], axis=1)
    concat_df.columns = ['before_yield', 'after_yield']
    concat_df_sort = concat_df.sort_values(by=['before_yield'], ascending=False)
    concat_df_sort = concat_df_sort[concat_df_sort['before_yield'] > -100]
    concat_df_sort = concat_df_sort[concat_df_sort['after_yield'] > -100]
    fig, ax = plt.subplots()
    ax.plot(concat_df_sort['before_yield'].values, concat_df_sort['after_yield'].values,'ro')
    plt.xlabel("1.31-2.9 yield")
    plt.ylabel("2.12-3.5 yield")
    ax.legend(loc="upper left")
    title = "before yield and after yield"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    return concat_df_sort


def get_top_stock_yield(select_num, concat_df_sort):
    """
    获取前select_num的股票的收益率分布，以及平均收益率
    :param select_num:
    :param concat_df_sort:
    :return:
    """
    select_num = 100
    select_df = concat_df_sort.head(select_num)
    rank_series = Series(range(1,101), index=select_df.index)
    select_df['rank_num'] = rank_series
    select_df_by_after_yield = select_df.sort_values(by='after_yield', ascending=False)
    fig, ax = plt.subplots()
    ax.hist(select_df['after_yield'])
    title = "n is " + str(select_num)
    plt.title(title)
    select_df['after_yield'].hist()
    print "mean yield above hs300 is " + str(select_df['after_yield'].mean())



if __name__ == '__main__':
    start_date = "2018-03-21"
    end_date = '2018-03-28'
    after_start = "2018-02-12"
    after_end = "2018-03-05"
    select_num = 50
    select_code_list, stock_change_sort = find_defensive_stock(start_date, end_date, select_num)
    select_code_list = stock_change_sort.index[:select_num]
    stock_change_series = get_select_stock_trend(select_code_list, after_start, after_end)
    stock_change_series.hist()



