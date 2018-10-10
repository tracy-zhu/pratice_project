# -*- coding: utf-8 -*-
"""

# 在行业板块启动的过程中，往往龙头股会有率先启动的结果

# 根据筛选出来的龙头股（先根据市值大小排序），找出龙头股相对于其余股票区别比较大的股票；

# 参考研报《光大证券：技术指标系列报告之五：行业轮动，从动量谈起》 201806热点研报

Fri 2018/06/15

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_industry_base import *
from stock_base.stock_data_api import *

out_file_folder = '..\\stock_industry_analysis\\result\\'
limit_percent = 0.3

# trading_date = datetime.now()
# trading_day = trading_date.strftime('%Y-%m-%d')
# trading_day = '2018-06-11'


def calc_herding_index(industry_df, industry_code, trading_day, back_period):
    """
    计算一个行业的herding_index参数, 认为该参数越大，行业启动的概率越大
    开始是通过市值因子对龙头股和跟随股进行区分，显然是个简单的方法；
    :param industry_df:
    :param industry_code:
    :param trading:
    :param back_period:
    :return:
    """
    herding_index = -999
    lead_stock_list, follow_stock_list, stock_code_list = find_industry_leading_stock(industry_df, industry_code, trading_day)
    if len(lead_stock_list) > 0:
        lead_pct_mean, _ = calc_stock_list_mean_pct(lead_stock_list, trading_day, back_period)
        follow_pct_mean, _ = calc_stock_list_mean_pct(follow_stock_list, trading_day, back_period)
        _, stock_std = calc_stock_list_mean_pct(stock_code_list, trading_day, back_period)
        herding_index = float(lead_pct_mean - follow_pct_mean) / float(stock_std)
    return herding_index


def calc_herding_index_by_yield(industry_df, industry_code, trading_day, back_period):
    """
    计算一个行业的herding_index参数, 认为该参数越大，行业启动的概率越大
    直接将过去涨幅最好的前percent的股票的平均涨幅和其余的股票的平均涨幅作差异计算herding index
    :param industry_df:
    :param industry_code:
    :param trading:
    :param back_period:
    :return:
    """
    global limit_percent
    herding_index = -999
    stock_code_list = get_industry_stock_code(industry_df, industry_code)
    pct_chg_series = get_stock_list_description(stock_code_list, trading_day, back_period)
    stock_std = pct_chg_series.std()
    sort_pct_chg_series = pct_chg_series.sort_values(ascending=False)
    split_num = int(limit_percent * len(pct_chg_series))
    if split_num > 0:
        lead_pct_mean = sort_pct_chg_series.head(split_num).mean()
        follow_pct_mean = sort_pct_chg_series.tail(-1 * split_num).mean()
        herding_index = float(lead_pct_mean - follow_pct_mean) / float(stock_std)
    return herding_index


def find_industry_leading_stock_by_yield(industry_df, industry_code, trading_day, back_period):
    """
    根据收益率计算出该行业的排名靠前的股票和排名靠前股票的平均收益率
    :param industry_df:
    :param industry_code:
    :param trading_day:
    :param back_period:
    :return:
    """
    global limit_percent
    lead_stock_code_list = []
    lead_pct_mean = 0
    follow_pct_mean = 0
    stock_code_list = get_industry_stock_code(industry_df, industry_code)
    pct_chg_series = get_stock_list_description(stock_code_list, trading_day, back_period)
    sort_pct_chg_series = pct_chg_series.sort_values(ascending=False)
    split_num = int(limit_percent * len(pct_chg_series))
    split_num = split_num if split_num >= 3 else 3
    if split_num > 0:
        lead_pct_mean = sort_pct_chg_series.head(split_num).mean()
        follow_pct_mean = sort_pct_chg_series.tail(-1 * split_num).mean()
        lead_stock_code_list = list(sort_pct_chg_series.head(split_num).index)
    return lead_stock_code_list, lead_pct_mean, follow_pct_mean


def sort_industry_by_herding_index(trading_day, back_period, level_flag):
    """
    根据上述函数计算herding_index将industry进行排序；
    :param trading_day:
    :param back_period:
    :return:
    """
    herding_index_dict = defaultdict()
    industry_code_list = get_industry_code(trading_day, level_flag)
    industry_df = get_industry_df(trading_day, level_flag)
    for industry_code in industry_code_list:
        print industry_code
        herding_index = calc_herding_index_by_yield(industry_df, industry_code, trading_day, back_period)
        herding_index_dict[industry_code] = herding_index
    herding_index_series = Series(herding_index_dict)
    herding_index_series = herding_index_series.sort_values(ascending=False)
    return herding_index_series


if __name__ == '__main__':
    # trading_date = datetime.now()
    # trading_day = trading_date.strftime('%Y-%m-%d')
    trading_day = '2018-07-05'
    back_period = 5
    level_flag = 1
    industry_df = get_industry_df(trading_day, level_flag)
    out_file_name = '..\\stock_industry_analysis\\result\\lead_stock_primacy.txt'
    f = open(out_file_name, 'wb')
    print "calc herding index by yield:"
    herding_index_series = sort_industry_by_herding_index(trading_day, back_period, level_flag)
    for industry_code in herding_index_series.index:
        chi_name = find_industry_chi_name(industry_code, level_flag)
        lead_stock_list, lead_pct_mean, follow_mean = find_industry_leading_stock_by_yield(industry_df, industry_code, trading_day, back_period)
        print>>f, industry_code, ',', chi_name, ',', herding_index_series[industry_code]
        for stock_code in lead_stock_list[-3:]:
            stock_chi_name = find_stock_chi_name(stock_code)
            print>>f,  stock_code, ',', stock_chi_name, ',', lead_pct_mean
