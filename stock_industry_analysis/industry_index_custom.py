# -*- coding: utf-8 -*-
"""

# 同样分析行业的板块，采取申万一级行业指数不同的是，是根据自己的需要自定义行业指数涨幅；

# 首先是根据将股票过去一段时间的涨幅来生成指数；

Wed 2018/10/10

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_industry_base import *


def industry_index_custom_by_momentum(industry_df, industry_code, trading_day, back_period):
    """
    根据过去一段时间，行业中的股票涨跌幅，剔除行业中涨幅比较差的股票，按照平均收益率作为指数的平均涨幅；
    :param industry_df:
    :param industry_code:
    :param trading_day:
    :param back_period:
    :return:
    """
    lead_pct_mean = 0
    lead_stock_code_list = []
    limit_percent = 0.8
    stock_code_list = get_industry_stock_code(industry_df, industry_code)
    pct_chg_series = get_stock_list_description(stock_code_list, trading_day, back_period)
    sort_pct_chg_series = pct_chg_series.sort_values(ascending=False)
    split_num = int(limit_percent * len(pct_chg_series))
    split_num = split_num if split_num >= 3 else 3
    if split_num > 0:
        lead_pct_mean = sort_pct_chg_series.head(split_num).mean()
        lead_stock_code_list = list(sort_pct_chg_series.head(split_num).index)
    return lead_pct_mean, lead_stock_code_list


def sort_industry_by_custom_momentum(trading_day, back_period, level_flag):
    """
    根据自定义的行业动量对板块进行一定的排序
    :return:
    """
    ind_momentum_dict = defaultdict()
    industry_code_list = get_industry_code(trading_day, level_flag)
    industry_df = get_industry_df(trading_day, level_flag)
    for industry_code in industry_code_list:
        print(industry_code)
        ind_momentum, _ = industry_index_custom_by_momentum(industry_df, industry_code, trading_day, back_period)
        ind_momentum_dict[industry_code] = ind_momentum
    ind_momentum_series = Series(ind_momentum_dict)
    ind_momentum_series = ind_momentum_series.sort_values(ascending=False)
    return ind_momentum_series