# -*- coding: utf-8 -*-
"""

# 找出当天涨停股票个数超过3个的热点板块

# 从板块中选择出龙一， 龙二， 龙三

# 分析涨停之后，龙一，龙二， 龙三的走势

FRI 2018/03/09

@author: Tracy Zhu
"""

# 导入系统库
import sys
from WindPy import w


# 导入用户库
sys.path.append("..")
from stock_tool.up_limit_stock_num import *


DELETE_CONCEPT_LIST = []
up_limit_critical_value = 3


def find_hot_concept_trading_day(trading_day):
    """
    找出当个交易日的热点板块，判定条件为该板块涨停股票个数大于3
    并且前一天不超过1只股票涨停
    :param trading_day:
    :return:
    """
    global up_limit_critical_value
    final_concept_dict = defaultdict()
    concept_dict_wind = get_up_limit_concept(trading_day)
    select_concept_dict = {k:v for k, v in concept_dict_wind.items() if len(v) >= up_limit_critical_value}
    pre_trading_day = get_pre_trading_day_stock(trading_day)
    for concept_name, stock_list in select_concept_dict.items():
        concept_code = concept_name.split(',')[0]
        stock_code_list = find_concept_stock(concept_code, trading_day)
        pre_up_stock_list = find_stock_up_limit(pre_trading_day, 1)
        pre_up_limit_stock = list(set(stock_code_list).intersection(set(pre_up_stock_list)))
        if len(pre_up_limit_stock) <= 1:
            final_concept_dict[concept_name] = stock_list
    return final_concept_dict


def find_leading_stock(stock_code_list, trading_day, reference_days):
    """
    根据指定的条件，对概念板块的龙头股进行排序
    :param stock_code_list:
    :param trading_day: 确定哪一天涨停
    :param reference_days: 1的话就看当天哪只股票首先涨停；大于1则看过去天数的涨跌幅
    :return:
    """
    stock_up_limit_time_dict = defaultdict()
    if reference_days == 1:
        for stock_code in stock_code_list:
            first_up_limit_time, _ = find_stock_up_limit_time_from_raw_data(stock_code, trading_day)
            stock_up_limit_time_dict[stock_code] = first_up_limit_time
    else:
        pass
    sorted_dict = sorted(stock_up_limit_time_dict.items(), key=lambda d: d[1])
    return sorted_dict


def leading_stock_trading(stock_code, second_day, hold_days, flag_num):
    """
    统计龙头股票的后期走势,以第二天的开盘价计算，持有天数由hold_days计算
    :param second_day:
    :param hold_days:
    :param flag_num:0:代表以持有日的开盘价出，1代表以持有日的收盘价计算；后期会加入更多的平仓条件；
    :return:
    """
    end_date = get_next_trading_day_stock(second_day, hold_days)
    close_price = 0
    open_price = 0
    if end_date != None:
        stock_df = get_stock_df(stock_code, second_day, end_date)
        open_price = stock_df.loc[0]["OPEN"]
        high_price = stock_df.loc[0]["HIGH"]
        if open_price >= high_price:
            print "can't buy the stock"
            return None
        else:
            if flag_num == 0:
                close_price = stock_df["OPEN"].values[-1]
            elif flag_num == 1:
                close_price = stock_df["CLOSE"].values[-1]
    try:
        hold_yield = float(close_price) / float(open_price) - 1
    except:
        print "open price is zero"
    else:
        if hold_yield > -0.2:
            return hold_yield


def hist_save_picture(data_series, flag_num):
    """
    将绘制出的频率分布图，存储进去
    :param data_series:
    :param flag_num:
    :return:
    """
    result_path = "..\\stock_tool\\picture\\"
    out_file_name = result_path + "yield_distribution_" + str(flag_num) + '.png'
    fig, ax = plt.subplots()
    ax.hist(data_series)
    fig.set_size_inches(23.2, 14.0)
    plt.savefig(out_file_name)


def strategy_main(start_date, end_date, hold_days):
    """
    统计热点板块的收益率分布，分为龙一，龙二，龙三
    由多少天确认板块，并在第二个交易日介入也是个参数；
    介入之后，持有多少天，并且什么样的平仓条件也是一个参数
    板块的分类首先按照wind来看
    :return:
    """
    leading_yield_close_first = []
    leading_yield_close_second = []
    leading_yield_close_third = []
    leading_yield_open_first = []
    leading_yield_open_second = []
    leading_yield_open_third = []
    trading_day_list = get_trading_day_list()
    for i in range(len(trading_day_list) - 1):
        first_day = trading_day_list[i][:-1]
        second_day = trading_day_list[i+1][:-1]
        first_day = change_day_str_stock(first_day)
        second_day = change_day_str_stock(second_day)
        if first_day > start_date and second_day <= end_date:
            print first_day
            final_concept_dict = find_hot_concept_trading_day(first_day)
            for concept_name, stock_code_list in final_concept_dict.items():
                sorted_dict = find_leading_stock(stock_code_list, first_day, 1)
                stock_first = sorted_dict[0][0]
                stock_second = sorted_dict[1][0]
                stock_third = sorted_dict[2][0]
                leading_yield_close_first.append(leading_stock_trading(stock_first, second_day, hold_days, 1))
                leading_yield_close_second.append(leading_stock_trading(stock_second, second_day, hold_days, 1))
                leading_yield_close_third.append(leading_stock_trading(stock_third, second_day, hold_days, 1))
                leading_yield_open_first.append(leading_stock_trading(stock_first, second_day, hold_days, 0))
                leading_yield_open_second.append(leading_stock_trading(stock_second, second_day, hold_days, 0))
                leading_yield_open_third.append(leading_stock_trading(stock_third, second_day, hold_days, 0))
    print "leading yield close first series:"
    leading_yield_close_first_series = Series(leading_yield_close_first).dropna()
    hist_save_picture(leading_yield_close_first_series, 1)
    print(leading_yield_close_first_series.describe())
    print "leading yield close second series:"
    leading_yield_close_second_series = Series(leading_yield_close_second).dropna()
    hist_save_picture(leading_yield_close_second_series, 2)
    print(leading_yield_close_second_series.describe())
    print "leading yield close third series:"
    leading_yield_close_third_series = Series(leading_yield_close_third).dropna()
    hist_save_picture(leading_yield_close_third_series, 3)
    print(leading_yield_close_third_series.describe())
    print "leading yield open first series:"
    leading_yield_open_first_series = Series(leading_yield_open_first).dropna()
    hist_save_picture(leading_yield_open_first_series, 4)
    print(leading_yield_open_first_series.describe())
    print "leading yield open second series:"
    leading_yield_open_second_series = Series(leading_yield_open_second).dropna()
    hist_save_picture(leading_yield_open_second_series, 5)
    print(leading_yield_open_second_series.describe())
    print "leading yield open third series:"
    leading_yield_open_third_series = Series(leading_yield_open_third).dropna()
    hist_save_picture(leading_yield_open_third_series, 6)
    print(leading_yield_open_third_series.describe())


if __name__ == '__main__':
    start_date = '2017-11-20'
    end_date = '2018-03-09'
    hold_days = 3
    strategy_main(start_date, end_date, hold_days)

