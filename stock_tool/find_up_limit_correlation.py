# -*- coding: utf-8 -*-
"""

# 计算板块涨停之间的相关性，即这只股票涨停，同一天内，或者涨停前后10分钟涨停的股票,回溯过去所有交易日的情况，最后留下来的即为相关性较高的股票


Mon 2018/4/16

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math
from collections import Counter

# 导入用户库：
sys.path.append("..")
from stock_base.stock_file_api import *

trading_day_list = get_trading_day_list()

stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', '2018-04-13', '2018-04-13')
all_stock_code_list = stock_df.code.unique()


def stock_limit_corr(stock_code, start_day):
    """
    找出股票代码的涨停日期，并找出相同日期的涨停股票
    不断取交集
    :param stock_code:'000300.SH'
    :param limit_day: 初始日期，代表大于当前的日期, '2018-04-01'
    :return: list 里面是股票代码
    """
    total_up_num = 0
    all_corr_stock_list = []
    corr_stock_list = list(all_stock_code_list)
    up_limit_days = stock_up_limit_days(stock_code)
    if len(up_limit_days) > 0:
        for limit_day in up_limit_days:
            trading_day = str(limit_day.year) + '-' + str(limit_day.month).zfill(2) + '-' + str(limit_day.day).zfill(2)
            if trading_day > start_day:
                stock_up_list = find_stock_up_limit(trading_day, 1)
                all_corr_stock_list = all_corr_stock_list + stock_up_list
                corr_stock_list = list(set(corr_stock_list).intersection(set(stock_up_list)))
                total_up_num += 1
        #corr_stock_list.remove(stock_code)
    else:
        corr_stock_list = []
    corr_stock_sort_dict = Counter(all_corr_stock_list)
    return corr_stock_list, corr_stock_sort_dict, total_up_num


def stock_corr_condition(stock_code, start_day, up_limit_pct):
    """
    找出股票，当天涨幅超过一定比例的股票，一般是8%；
    :param stock_code:
    :param start_day:
    :param up_limit_pct: 8，代表8%
    :return:
    """
    total_up_num = 0
    all_corr_stock_list = []
    corr_stock_list = list(all_stock_code_list)
    up_limit_days = stock_up_limit_days(stock_code)
    if len(up_limit_days) > 0:
        for limit_day in up_limit_days:
            trading_day = str(limit_day.year) + '-' + str(limit_day.month).zfill(2) + '-' + str(limit_day.day).zfill(2)
            if trading_day > start_day:
                stock_up_list = find_stock_up_condition(trading_day, 1)
                all_corr_stock_list = all_corr_stock_list + stock_up_list
                corr_stock_list = list(set(corr_stock_list).intersection(set(stock_up_list)))
                total_up_num += 1
        #corr_stock_list.remove(stock_code)
    else:
        corr_stock_list = []
    corr_stock_sort_dict = Counter(all_corr_stock_list)
    return corr_stock_list, corr_stock_sort_dict, total_up_num


def find_stock_up_condition(trading_day, up_limit_pct):
    """
    找出当个交易日，找出股票涨幅大于某个值的股票个数
    :param trading_day: “2018-04-22”
    :param up_limit_pct:8
    :return:
    """
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time = \"{trading_day}\" ' \
          ' and  PCT_CHG >= {up_limit_pct}'.format(trading_day=trading_day,
                                                                   up_limit_pct=up_limit_pct)

    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    df_table.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    select_code_list = list(df_table.code)
    return select_code_list


def get_up_corr_stock_dict(all_stock_code_list, start_day, flag_num):
    """
    根据上述的股票得出每只股票对应的涨停板相关的股票
    :param all_stock_code_list:
    :param flag_num:0 用 stock_limit_corr ; 1 用 stock_corr_condition
    :return:
    """
    up_corr_stock_dict_intersection = defaultdict(list)
    up_corr_stock_sort_dict = defaultdict()
    stock_up_num_dict = defaultdict()
    for stock_code in all_stock_code_list:
        if flag_num == 0:
            corr_stock_list, corr_stock_sort_dict, total_up_num = stock_limit_corr(stock_code, start_day)
        else:
            corr_stock_list, corr_stock_sort_dict, total_up_num = stock_corr_condition(stock_code, start_day,8)
        up_corr_stock_dict_intersection[stock_code] = corr_stock_list
        up_corr_stock_sort_dict[stock_code] = corr_stock_sort_dict
        stock_up_num_dict[stock_code] = total_up_num
    return up_corr_stock_dict_intersection, up_corr_stock_sort_dict, stock_up_num_dict


if __name__ == '__main__':
    out_file_name = '..\\stock_tool\\result\\up_limit_correlation.txt'
    f = open(out_file_name, 'wb')
    start_day = '2012-01-01'
    # stock_code = '600830.SH'
    up_limit_pct = 8
    up_corr_stock_dict_intersection, up_corr_stock_sort_dict, stock_up_num_dict = get_up_corr_stock_dict(all_stock_code_list, start_day, flag_num=1)
    for stock_code in all_stock_code_list:
        print stock_code
        up_corr_stock_list = up_corr_stock_sort_dict[stock_code].most_common(4)
        str_line = stock_code + ','
        for tuple_value in up_corr_stock_list:
            if tuple_value[0] != stock_code:
                str_line = str_line + tuple_value[0] + ','
        str_line = str_line + '\n'
        f.write(str_line)
    f.close()

