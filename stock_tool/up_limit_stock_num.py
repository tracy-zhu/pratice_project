# -*- coding: utf-8 -*-
"""

# 找出涨停板股票以及对应的概念以及持续的天数

# 从某天开始，先选择当天涨停的股票，及对应的股票；

# 三个板块，富士康，工业互联网， 高送转概念股

FRI 2018/03/09

@author: Tracy Zhu
"""

# 导入系统库
import sys
from WindPy import w
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *
from python_base.plot_method import *


def get_up_limit_concept(trading_day):
    """
    找出当天涨停的股票，并且对应的板块，统计当天涨停的板块，并且每个板块有多少涨停
    """
    concept_dict = defaultdict(list)
    up_limit_stock_list = find_stock_up_limit(trading_day, 1)
    for stock_code in up_limit_stock_list:
        concept_list = find_stock_concept(stock_code, trading_day)
        for concept_code in concept_list:
            concept_dict[concept_code].append(stock_code)
    return concept_dict


def get_up_limit_concept_ifind(trading_day):
    """
    根据同花顺的概念股划分，找出每个概念当天涨停的股票
    :param trading_day:
    :return:
    """
    concept_dict = defaultdict(list)
    up_limit_stock_list = find_stock_up_limit(trading_day, 1)
    for stock_code in up_limit_stock_list:
        concept_list = find_stock_concept_ifind(stock_code, trading_day)
        for concept_code in concept_list:
            concept_dict[concept_code].append(stock_code)
    return concept_dict


def sort_concept_by_up_num(concept_dict):
    """
    将当天的涨停的板块按照涨停数量排序
    :param concept_dict:
    :return:
    """
    new_concept_dict = defaultdict(list)
    for concept_code, stock_code_list in concept_dict.items():
        new_concept_dict[concept_code] = len(stock_code_list)
    sorted_dict = sorted(new_concept_dict.items(), key=lambda d: d[1], reverse=True)
    return sorted_dict


def print_trading_day_concept_situation(start_date, end_date, flag):
    """
    将每个交易日涨停个数排名靠前的板块输入到相应的csv中
    :param start_date: '20180305'
    :param end_date: '20180309'
    :param flag : 0 wind, 1: ifind
    :return:
    """
    trading_day_list = get_trading_day_list()
    for trade_day in trading_day_list:
        trade_day = trade_day[:-1]
        if start_date <= trade_day <= end_date:
            print trade_day
            trading_day = trade_day[:4] + '-' + trade_day[4:6] + '-' + trade_day[6:8]
            if flag == 0:
                out_file_name = '..\\stock_tool\\result\\concept_name_wind_' + trading_day + '.csv'
                f = open(out_file_name, 'wb')
                concept_dict = get_up_limit_concept(trading_day)
                sorted_concept_dict = sort_concept_by_up_num(concept_dict)
                for concept_situation in sorted_concept_dict[:20]:
                    concept_name = concept_situation[0].split(',')[1]
                    concept_num = concept_situation[1]
                    print>>f, concept_name, ',',concept_num
                f.close()
            elif flag == 1:
                out_file_name = '..\\stock_tool\\result\\concept_name_ifind_' + trading_day + '.csv'
                f = open(out_file_name, 'wb')
                concept_dict = get_up_limit_concept_ifind(trading_day)
                sorted_concept_dict = sort_concept_by_up_num(concept_dict)
                for concept_situation in sorted_concept_dict[:20]:
                    concept_name = concept_situation[0].encode('utf-8')
                    concept_num = concept_situation[1]
                    print>>f, concept_name, ',',concept_num
                f.close()


def sort_stock_by_yield(concept_code, start_date, end_date):
    """
    按照涨幅排名，筛选过去一周板块中优秀的股票
    :param concept_code:
    :param start_date : '2018-03-05'
    :return:
    """
    stock_change_dict = defaultdict()
    stock_code_list = find_concept_stock(concept_code, start_date)
    stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', start_date, end_date)
    for stock_code in stock_code_list:
        selected_df = stock_df[stock_df['code']==stock_code]
        total_percent_change = selected_df["PCT_CHG"].sum()
        stock_change_dict[stock_code] = total_percent_change
    stock_change_series = Series(stock_change_dict)
    stock_change_sort = stock_change_series.sort_values(ascending=False)
    select_code_list = stock_change_sort.index[:5]
    for stock_code in select_code_list:
        print stock_code , stock_change_dict[stock_code]
    return select_code_list


if __name__ == '__main__':
    start_date = '20180305'
    end_date = '20180309'
    # concept_code_list = ['884027.WI', "884196.WI", "884193.WI", '884031.WI']
    # for concept_code in concept_code_list:
    #     select_code_list = sort_stock_by_yield(concept_code, start_date, end_date)
    #     print concept_code
        # print select_code_list
    print_trading_day_concept_situation(start_date, end_date, 1)

