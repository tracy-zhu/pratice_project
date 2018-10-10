# -*- coding: utf-8 -*-
"""

# 找出大盘下跌的时候，按照股票的收益率进行排序

# 比较抗跌的股票在后市中是否有好的影响；

Tue 2018/03/06

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_industry_base import *

trading_date = datetime.now()
#trading_day = trading_date.strftime('%Y-%m-%d')
trading_day = '2018-07-06'

# start_date = get_next_trading_day_stock(trading_day, -1 * back_period)

industry_code_list = get_industry_code(trading_day, level_flag=2)
trading_day_list = get_trading_day_list()


def back_period_momentum_generation(industry_code, trading_day, back_period):
    """
    获取回看期间该板块的industry_code的momentum
    :param industry_code:
    :param trading_day:
    :param back_period:
    :return:
    """
    start_date = get_next_trading_day_stock(trading_day, -1 * back_period)
    industry_df = fetch_industry_code_daily_data(industry_code, start_date, trading_day)
    sum_pct_chg = (industry_df.PCT_CHG / 100 + 1).cumprod().values[-1]
    return sum_pct_chg


def industry_positive_ratio_generation(industry_code, trading_day, back_period):
    """
    获取回看期间板块的industry的涨幅为正的比例
    :param industry_code:
    :param trading_day:
    :param back_period:
    :return:
    """
    start_date = get_next_trading_day_stock(trading_day, -1 * back_period)
    industry_df = fetch_industry_code_daily_data(industry_code, start_date, trading_day)
    pct_chg_series = industry_df.PCT_CHG
    positive_ratio = float(sum(pct_chg_series>0)) / float(back_period)
    return positive_ratio


def get_next_period_industry_yield(industry_code, trading_day, holding_period):
    """
    获取后面持有期间的industry_code的yield
    :param industry_code:
    :param trading_day:
    :param holding_period:
    :return:
    """
    start_date = get_next_trading_day_stock(trading_day, 1)
    end_date = get_next_trading_day_stock(trading_day, holding_period)
    industry_df = fetch_industry_code_daily_data(industry_code, start_date, end_date)
    yield_to_maturity = (industry_df.PCT_CHG / 100 + 1).cumprod().values[-1]
    yield_series = (industry_df.PCT_CHG / 100 + 1).cumprod()
    return yield_to_maturity, yield_series


def select_industry_code_by_positive_ratio(industry_code_list, trading_day, back_period):
    positive_dict = defaultdict()
    for industry_code in industry_code_list:
        sum_pct_chg = back_period_momentum_generation(industry_code, trading_day, back_period)
        positive_dict[industry_code] = sum_pct_chg

    momentum_series = Series(positive_dict)
    momentum_series_sort = momentum_series.sort_values()
    momentum_list = list(momentum_series_sort.index[-5:])
    reverse_list = list(momentum_series_sort.index[:6])
    return momentum_list, reverse_list


def sort_industry_code_by_momentum(industry_code_list, trading_day, back_period):
    """
    根据前期涨幅排名，对所选的板块进行排序；
    :param industry_code_list:
    :param trading_day:
    :param back_period:
    :return:
    """
    momentum_dict = defaultdict()
    for industry_code in industry_code_list:
        sum_pct_chg = back_period_momentum_generation(industry_code, trading_day, back_period)
        momentum_dict[industry_code] = sum_pct_chg

    momentum_series = Series(momentum_dict)
    momentum_series_sort = momentum_series.sort_values()
    return momentum_series_sort


def select_industry_code_by_momentum(industry_code_list, trading_day, back_period):
    """
    根据当个交易日和回看周期，选出前期动量最好的三只industry_code, 动量最差的三只Industry_code
    :param industry_code_list:
    :param trading_day:
    :param back_period:
    :return:
    """
    momentum_series_sort = sort_industry_code_by_momentum(industry_code_list, trading_day, back_period)
    momentum_list = list(momentum_series_sort.index[-3:])
    reverse_list = list(momentum_series_sort.index[:3])
    return momentum_list, reverse_list


def select_code_list_holding_period(select_code_list, trading_day, holding_period):
    """
    根据前面函数条件选取的指数代码，得到后面的走势的平均收益率；
    :param select_code_list:
    :param trading_day:
    :param hold_period:
    :return:
    """
    yield_list = []
    yield_series_dict = defaultdict()
    for industry_code in select_code_list:
        hold_yield, yield_series = get_next_period_industry_yield(industry_code, trading_day, holding_period)
        yield_list.append(hold_yield)
        yield_series_dict[industry_code] = yield_series
    industry_hold_yield = Series(yield_list).mean()
    yield_df = DataFrame(yield_series_dict)
    mean_yield_series = yield_df.mean(axis=1)
    return industry_hold_yield, mean_yield_series


def back_test_strategy():
    momentum_yield = 1
    reverse_yield = 1
    momentum_yield_list = [1]
    reverse_yield_list = [1]
    back_period = 30
    holding_period = 30
    begin_day = "2016-04-06"
    end_day = get_next_trading_day_stock(begin_day, holding_period)
    while end_day <= '2018-05-16':
        momentum_list, reverse_list = select_industry_code_by_momentum(industry_code_list, begin_day, back_period)
        momentum_hold_yield, momentum_yield_series = select_code_list_holding_period(momentum_list, begin_day, holding_period)
        reverse_hold_yield, reverse_yield_series = select_code_list_holding_period(reverse_list, begin_day, holding_period)
        momentum_yield_series = momentum_yield_list[-1] * momentum_yield_series
        reverse_yield_series = reverse_yield_list[-1] * reverse_yield_series
        momentum_yield_list = momentum_yield_list + list(momentum_yield_series)
        reverse_yield_list = reverse_yield_list + list(reverse_yield_series)
        begin_day = get_next_trading_day_stock(begin_day, holding_period)
        end_day = get_next_trading_day_stock(begin_day, holding_period)

    all_momentum_yield_series = Series(momentum_yield_list)
    all_reverse_yield_series = Series(reverse_yield_list)
    all_momentum_yield_series.plot()
    all_reverse_yield_series.plot()


if __name__ == '__main__':
    back_period = 43
    trading_day = '2018-07-05'
    sort_momentum_series = sort_industry_code_by_momentum(industry_code_list, trading_day, back_period)
    out_file_name = '..\\stock_industry_analysis\\result\\sort_momentum_series.csv'
    sort_momentum_series.to_csv(out_file_name)
    # positive_ratio_list, negative_ratio_list = select_industry_code_by_positive_ratio(industry_code_list, trading_day, back_period)
    # print positive_ratio_list[::-1]
    # print negative_ratio_list