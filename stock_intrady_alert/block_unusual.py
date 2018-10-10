# -*- coding: utf-8 -*-
"""

# 将盘中异动的板块提示出来

Thu 2018/03/27

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_file_api import *
from stock_data_task.find_hot_block import *
import time


start_time = time.clock()
now = datetime.now()
trading_day = now.strftime('%Y-%m-%d')
pre_trading_day = get_pre_trading_day_stock(trading_day)
# trading_day = '2018-03-29'
# pre_trading_day = '2018-03-28'
begin_time = 143000
end_time = 145500


concept_list = find_all_stock_concept_list_ifind(pre_trading_day)

concept_list_all = []
stock_list_all = []
concept_name_dict = defaultdict()

for concept_value in concept_list:
    concept_code = concept_value.split(',')[0]
    concept_name = concept_value.split(',')[1]
    concept_name_dict[concept_code] = concept_name
    stock_code_list = find_concept_stock_ifind(concept_code, pre_trading_day)
    concept_code_list = [concept_code for i in range(len(stock_code_list))]
    concept_list_all = concept_list_all + concept_code_list
    stock_list_all = stock_list_all + stock_code_list

df_dict = {'index_code':stock_list_all, 'concept_list_all':concept_list_all}
concept_df = DataFrame(df_dict)

slice_df = read_real_time_stock_data_wind(trading_day, begin_time)
begin_slice_df = slice_df[['index_code', 'pct_chg']]
slice_df = read_real_time_stock_data_wind(trading_day, end_time)
end_slice_df = slice_df[['index_code', 'pct_chg']]


def get_concept_yield(concept_df, stock_slice_df):
    """
    获取板块的平均收益
    :param concept_df:
    :param stock_slice_df:
    :return:
    """
    concat_df = pd.merge(concept_df, stock_slice_df)
    grouped_df = concat_df['pct_chg'].groupby(concat_df['concept_list_all'])
    concept_yield = grouped_df.mean()
    ratio_positive = count_positive_ratio(grouped_df)
    return concept_yield, ratio_positive


def count_positive_ratio(grouped_df):
    """
    计算分组之后的股票正收益的比例
    :param grouped_df:
    :return:
    """
    ratio_chg_dict = defaultdict()
    grouped_dict = dict(list(grouped_df))
    for concept_code, stock_yield_list in grouped_dict.items():
        positive_ratio = float(sum(stock_yield_list.values > 0)) / float(len(stock_yield_list))
        ratio_chg_dict[concept_code] = positive_ratio
    ratio_positive = Series(ratio_chg_dict)
    return ratio_positive


begin_concept_yield, begin_ratio_positive = get_concept_yield(concept_df, begin_slice_df)
end_concept_yield, end_ratio_positive = get_concept_yield(concept_df, end_slice_df)

concept_yield_chg = end_concept_yield - begin_concept_yield
ratio_chg = end_ratio_positive - begin_ratio_positive

concept_yield = concept_yield_chg.sort_values(ascending=False)
sort_ratio_chg = ratio_chg.sort_values(ascending=False)

print "this is yield sort!"

for values in concept_yield.index[:10]:
    block_name = concept_name_dict[values]
    select_code_str = find_leading_stock_by_iwencai(block_name)
    print block_name, ',', concept_yield_chg.loc[values], ',', select_code_str

print "this is ratio change!"

for values in sort_ratio_chg.index[:10]:
    block_name = concept_name_dict[values]
    select_code_str = find_leading_stock_by_iwencai(block_name)
    print block_name, ',', sort_ratio_chg.loc[values], ',', select_code_str

print time.clock() - start_time, 'process time!'