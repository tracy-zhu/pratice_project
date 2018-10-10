# -*- coding: utf-8 -*-
"""

# 分析行业中股票的不同，看如何在得出行业中将股票也筛选出来；

# 分析行业中的股票是存在动量效应还是反转效应；

Fri 2018/07/31

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_industry_analysis.volume_up_industry import *
from stock_base.stock_industry_base import *

industry_df = get_industry_df('2018-08-01', level_flag=2)


def calc_standard_indicator_series(indicator_series):
    """
    将同行业的数据标准归一化；
    :param indicator_series:
    :return:
    """
    indicator_series = indicator_series[indicator_series > -900]
    indicator_series = indicator_series.dropna()
    mean_value = indicator_series.mean()
    std_value = indicator_series.std()
    standard_indicator_series = (indicator_series - mean_value) / std_value
    return standard_indicator_series


def calc_quantile_percent(indicator_series):
    """
    计算值在当前序列中的比例值，最大值为100%，最小值为0%
    :param indicator_series:
    :return:
    """
    indicator_series = indicator_series[indicator_series > -100]
    max_value = indicator_series.max()
    mean_value = indicator_series.min()
    quantile_series = (indicator_series - mean_value) / (max_value - mean_value)
    return quantile_series


def calc_quantile_percent_order(indicator_series):
    """
    根据叙述排列计算分位数，不考虑收益的绝对数值
    :param indicator_series:
    :return:
    """
    indicator_series = indicator_series[indicator_series > -100]
    indicator_series.sort_values(inplace=True)
    order_series = Series(range(len(indicator_series)), index=indicator_series.index)
    quantile_series = order_series / len(order_series)
    return quantile_series


def get_industry_stock_description(industry_code, start_date, end_date):
    """
    获取一个行业中，所有股票在一段时间的收益率序列的数据
    :param industry_code:
    :param start_date:
    :param end_date:
    :return:
    """
    stock_cumprod_dict = defaultdict()
    global industry_df
    stock_code_list = get_industry_stock_code(industry_df, industry_code)
    for stock_code in stock_code_list:
        stock_df = get_stock_df(stock_code, start_date, end_date)
        if len(stock_df) > 0:
            cumprod_series = Series((stock_df.PCT_CHG / 100 + 1).cumprod().values, index=stock_df.time)
            stock_cumprod_dict[stock_code] = cumprod_series
    stock_cumprod_df = DataFrame(stock_cumprod_dict)
    return stock_cumprod_df


def get_industry_stock_description_by_open(industry_code, start_date, end_date):
    """
    获取一个行业中，所有股票在一段时间的收益率序列的数据, 不同于上面的函数
    是以start_date的开盘价开仓，end_date的收盘价平仓
    :param industry_code:
    :param start_date:
    :param end_date:
    :return:
    """
    stock_cumprod_dict = defaultdict()
    global industry_df
    stock_code_list = get_industry_stock_code(industry_df, industry_code)
    for stock_code in stock_code_list:
        stock_df = get_stock_df(stock_code, start_date, end_date)
        if len(stock_df) > 0:
            pct_chg = 0
            open_price = stock_df.OPEN.values[0]
            close_price = stock_df.CLOSE.values[-1]
            # cumprod_series = Series((stock_df.PCT_CHG / 100 + 1).cumprod().values, index=stock_df.time)
            if open_price > 0:
                pct_chg = float(close_price) / float(open_price)
            stock_cumprod_dict[stock_code] = pct_chg
    stock_cumprod_df = Series(stock_cumprod_dict)
    return stock_cumprod_df


def get_stock_predict_pe_series(industry_code, trading_day):
    """
    获取该板块所有的预测pe并从低到高排序
    :param industry_code:
    :param trading_day:
    :return:
    """
    stock_predict_pe_dict = defaultdict()
    global industry_df
    stock_code_list = get_industry_stock_code(industry_df, industry_code)
    for stock_code in stock_code_list:
        predict_pe = calc_stock_predict_pe(stock_code, trading_day)
        if predict_pe > 0:
            stock_predict_pe_dict[stock_code] = predict_pe
    stock_predict_pe_series = Series(stock_predict_pe_dict)
    stock_predict_pe_series = calc_standard_indicator_series(stock_predict_pe_series)
    return stock_predict_pe_series


def get_stock_predict_roe_series(industry_code, trading_day):
    """
    获取该板块所有的预测roe并从低到高排序
    :param industry_code:
    :param trading_day:
    :return:
    """
    stock_predict_roe_dict = defaultdict()
    global industry_df
    stock_code_list = get_industry_stock_code(industry_df, industry_code)
    for stock_code in stock_code_list:
        predict_roe = fetch_predict_roe(stock_code, trading_day)
        stock_predict_roe_dict[stock_code] = predict_roe
    stock_predict_roe_series = Series(stock_predict_roe_dict)
    stock_predict_roe_series = calc_standard_indicator_series(stock_predict_roe_series)
    return stock_predict_roe_series


def select_code_from_industry(industry_code, trading_day, back_period, limit_percent):
    """
    选出板块之后，不直接用板块指数回测，选择其中的部分股票，根据过去一段时间将垃圾股票删除；
    :param industry_code:
    :param trading_day:
    :param back_period:
    :param limit_percent: 选择过去一段时间前百分位的股票；0.8
    :return:
    """
    global industry_df
    start_date = get_next_trading_day_stock(trading_day, -1 * back_period)
    stock_cumprod_df = get_industry_stock_description(industry_code, start_date, trading_day)
    stock_end_yield = stock_cumprod_df.loc[stock_cumprod_df.index[-1]]
    sort_stock_yield = stock_end_yield.sort_values(ascending=False)
    select_num = int(limit_percent * len(sort_stock_yield))
    select_code_list = list(sort_stock_yield.index[:select_num])
    return select_code_list


def select_code_from_industry_reverse(industry_code, trading_day, back_period, limit_percent):
    """
    根据板块过去一段时间的走势，从中选出部分股票；上面一个函数是选择板块中涨势最好的股票，现在选取涨势不是最好的那批股票；
    但是考虑到有垃圾的股票，（连续跌停或者跌幅很大的股票）
    使用这样的算法：算出所有股票的平均收益率，然后在小于平均收益率的地方，选择前一定比例的股票；或者大于平均收益，选择最后的n只股票
    :param industry_code:
    :param trading_day:
    :param back_period:
    :param limit_percent:
    :return:
    """
    global industry_df
    start_date = get_next_trading_day_stock(trading_day, -1 * back_period)
    stock_cumprod_df = get_industry_stock_description(industry_code, start_date, trading_day)
    stock_end_yield = stock_cumprod_df.loc[stock_cumprod_df.index[-1]]
    sort_stock_yield = stock_end_yield.sort_values(ascending=False)
    select_stock_yield = sort_stock_yield[sort_stock_yield >= sort_stock_yield.mean()]
    select_num = int(limit_percent * len(select_stock_yield))
    select_code_list = list(select_stock_yield.index[-select_num:])
    return select_code_list


def select_code_from_industry_by_quantile(industry_code, trading_day):
    """
    根据过去一段时间的收益分布，选择同行业的股票在过去一段时间收益分布在一定的分位区间内；
    根据过去一段时间总结，在前5天排名百分位数在30%至50%的股票似乎表现比较好；
    :param industry_code:
    :param trading_day:
    :param back_period:
    :param limit_percent:
    :return:
    """
    global industry_df
    pre_start_date = get_next_trading_day_stock(trading_day, -5)
    pre_end_date = get_next_trading_day_stock(trading_day, -1)
    stock_pre_pct_chg = get_industry_stock_description_by_open(industry_code, pre_start_date, pre_end_date)
    standard_pct_chg = calc_quantile_percent_order(stock_pre_pct_chg)
    select_stock_series = standard_pct_chg[standard_pct_chg >= 0.3]
    select_stock_series = select_stock_series[select_stock_series <= 0.5]
    select_code_list = list(select_stock_series.index)
    return select_code_list


def select_code_industry_holding_profit(select_code_list, start_date, end_date):
    """
    选出的股票列表，得出收益列表，和平均收益率；
    :param select_code_list:
    :param start_date:
    :param end_date:
    :return:
    """
    stock_cumprod_dict = defaultdict()
    sort_stock_yield = 0
    mean_yield = 0
    for stock_code in select_code_list:
        stock_df = get_stock_df(stock_code, start_date, end_date)
        stock_df = stock_df[stock_df.PCT_CHG > -10]
        cumprod_series = Series((stock_df.PCT_CHG / 100 + 1).cumprod().values, index=stock_df.time)
        stock_cumprod_dict[stock_code] = cumprod_series
    stock_cumprod_df = DataFrame(stock_cumprod_dict)
    if len(stock_cumprod_df) > 0:
        stock_end_yield = stock_cumprod_df.loc[stock_cumprod_df.index[-1]]
        sort_stock_yield = stock_end_yield.sort_values(ascending=False)
        mean_yield = sort_stock_yield.mean() - 1
    return sort_stock_yield, mean_yield


if __name__ == '__main__':
    industry_code = '801034.SI'
    start_date = '2018-08-24'
    end_date = '2018-08-30'
    pre_start_date = get_next_trading_day_stock(start_date, -5)
    pre_end_date = get_next_trading_day_stock(start_date, -1)
    stock_pre_pct_chg = get_industry_stock_description_by_open(industry_code, pre_start_date, pre_end_date)
    standard_pct_chg = calc_quantile_percent(stock_pre_pct_chg)
    stock_cumprod_df = get_industry_stock_description_by_open(industry_code, start_date, end_date)
    stock_predict_pe_series = get_stock_predict_pe_series(industry_code, start_date)
    stock_predict_roe_series = get_stock_predict_roe_series(industry_code, start_date)
    # stock_end_yield = stock_cumprod_df.loc[stock_cumprod_df.index[-1]]
    concat_df = pd.concat([stock_cumprod_df, stock_predict_pe_series, stock_predict_roe_series, standard_pct_chg], axis=1)
    concat_df.columns = ['stock_yield', 'predict_pe', 'predict_roe', 'pre_standard_pct_chg']
    sort_stock_yield = concat_df.sort_values(by='stock_yield', ascending=False)
    print sort_stock_yield.head(10)

    sort_stock_roe = concat_df.sort_values(by='predict_roe', ascending=False)
    print "this is high roe stock list:"
    print sort_stock_roe.head(10)
    print sort_stock_roe.head(10)['stock_yield'].mean()

