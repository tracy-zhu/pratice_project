# -*- coding: utf-8 -*-
"""

# 找出热点概念及相关股票，在第一天起势之后，后面的相关股票走势分析

# 先决定出热点概念第一天起势的时间和结束的时间

# 三个板块，富士康，工业互联网， 高送转概念股

FRI 2018/03/09

@author: Tracy Zhu
"""

# 导入系统库
import sys
from WindPy import w

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *
from python_base.plot_method import *


foxconn_concept_stock_index = ["600207.SH", "002885.SZ", "300277.SZ", "002681.SZ", "300476.SZ", "300400.SZ",
                               "002388.SZ", "000727.SZ", "002886.SZ", "300537.SZ", "300032.SZ", "300503.SZ",
                               "601137.SH", "603595.SH", "600673.SH", "002138.SZ", "002182.SZ"]
industrial_internet_stock_index = []
high_turn_to_stock_index = []


def find_index_average_series(index_list, start_date, end_date):
    """
    将选出的一篮子的概念股票，平均收益率绘出，主要为了得出哪一天涨的最多，并且后期有较高涨幅的,
    还有之中达到涨停板个数的
    :param index_list:
    :param start_date:
    :param end_date:
    :return:
    """
    pct_dict = defaultdict()
    for stock_code in index_list:
        stock_df = get_stock_df(stock_code, start_date, end_date)
        pct_chg_series = Series(stock_df['PCT_CHG'].values, index=stock_df['time'].values)
        if len(pct_chg_series[pct_chg_series < -100]) == 0:
            pct_dict[stock_code] = pct_chg_series
    pct_df = DataFrame(pct_dict)
    pct_mean = pct_df.mean(axis=1)
    pct_above_7 = (pct_df > 7).sum(axis=1)
    index_df = get_index_data("000300.SH", start_date, end_date)
    index_pct_chg = Series(index_df['pct_chg'].values, index=index_df['time'].values)
    excess_return = pct_mean - index_pct_chg
    concat_df = pd.concat([pct_mean, excess_return, pct_above_7], axis=1)
    concat_df.columns = ['mean_pct', "excess_return", "pct_above7_num"]
    concat_df.to_csv(".\\stock_tool\\test.csv")
    return pct_df, pct_above_7


def sort_stock_yield(pct_df, reference_date):
    """
    pct_df是所选股票的收益率列表，reference_date是自启动开始，观察的日期天数
    :param pct_df:
    :param reference_date:
    :return:
    """
    stock_num = len(pct_df.columns)
    each_group_num = stock_num / 3
    return each_group_num




if __name__ == '__main__':
    start_date = "2018-02-12"
    end_date = "2018-03-08"
