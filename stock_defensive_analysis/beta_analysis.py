# -*- coding: utf-8 -*-
"""

# 计算大盘在上涨的时候的beta值，在下跌的时候beta值

# 计算股票在股市下跌的时候抗跌，在大盘上涨的时候反弹又比较迅速；

# 股市就按照沪深300来计算；

WED 2018/5/2

@author: Tracy Zhu
"""
# 导入系统库
import sys
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from stock_base.stock_data_api import *

holding_days = 60
# now = datetime.now()
# end_date = now.strftime('%Y-%m-%d')
end_date = '2018-11-16'
start_date = get_next_trading_day_stock(end_date, -1 * holding_days)
index_code = "000300.SH"

sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
      ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=end_date)
tp_table = fetchall_sql(sql)
all_stock_df = pd.DataFrame(list(tp_table))
all_stock_df.columns = retrieve_column_name('stock_db', 'daily_price_tb')

index_df_table = get_index_data(index_code, start_date, end_date)
index_yield_series = Series(index_df_table.pct_chg.values, index_df_table.time)
all_stock_code_list = get_all_stock_code_list(start_date)


def transfer_time_index_df(stock_df):
    """
    将原始的stock_df转化为time为index, 只有pct_chg的series
    :param stock_df:
    :return:
    """
    pct_chg_series = Series(stock_df.PCT_CHG.values, index=stock_df.time)
    return pct_chg_series


def calc_beta_value(yield_df):
    """
    计算该股票的beta值
    :param yield_df:
    :return:
    """
    X = yield_df['hs300']
    Y = yield_df['stock_yield']
    # X = sm.add_constant(x)
    result = (sm.OLS(Y, X)).fit()
    return result.params['hs300']


def beta_analysis(stock_code, start_date, end_date):
    """
    计算每只大盘涨的时候的beta，和大盘跌的时候的beta;
    :param stock_code:
    :param start_date:
    :param end_date:
    :return:beta_negative, beta_positive
    """
    # stock_df = get_stock_df(stock_code, start_date, end_date)
    stock_df = all_stock_df[all_stock_df.code == stock_code]
    pct_chg_series = transfer_time_index_df(stock_df)
    yield_df = pd.concat([index_yield_series, pct_chg_series], axis=1)
    yield_df.columns = ['hs300', 'stock_yield']
    yield_df = yield_df[yield_df.stock_yield > -10]
    positive_yield_df = yield_df[yield_df.hs300 > 0]
    negative_yield_df = yield_df[yield_df.hs300 < 0]
    positive_beta = calc_beta_value(positive_yield_df)
    negative_beta = calc_beta_value(negative_yield_df)
    return positive_beta, negative_beta


def get_selected_code_by_dict(beta_dict, flag):
    """
    根据beta_dict, 筛选出beta靠前的股票
    :param beta_dict:
    :flag: flag = 1 代表是大盘涨的股票，beta越大越好， flag=-1， 代表大盘下跌的beta值，越小越好
    :return:
    """
    select_code_list = []
    stock_change_series = Series(beta_dict)
    stock_change_sort = stock_change_series.sort_values(ascending=False)
    if flag == 1:
        select_code_list = stock_change_sort.index[:20]
    elif flag == -1:
        select_code_list = stock_change_sort.index[-20:]
    return select_code_list


def get_beta_indicator_dict(all_stock_code_list, start_date, end_date):
    """
    计算每只股票的beta指标，排出股票的抗跌强，反弹快的股票
    :param all_stock_code_list:
    :param start_date:
    :param end_date:
    :return:
    """
    beta_indicator_dict = defaultdict()
    positive_beta_dict = defaultdict()
    negative_beta_dict = defaultdict()
    for stock_code in all_stock_code_list:
        positive_beta, negative_beta = beta_analysis(stock_code, start_date, end_date)
        beta_indicator = positive_beta - negative_beta
        beta_indicator_dict[stock_code] = beta_indicator
        positive_beta_dict[stock_code] = positive_beta
        negative_beta_dict[stock_code] = negative_beta
    indicator_select_code_list = get_selected_code_by_dict(beta_indicator_dict, 1)
    positive_select_code = get_selected_code_by_dict(positive_beta_dict, 1)
    negative_select_code = get_selected_code_by_dict(negative_beta_dict, -1)
    return indicator_select_code_list, positive_select_code, negative_select_code


indicator_select_code_list, positive_select_code, negative_select_code = get_beta_indicator_dict(all_stock_code_list, start_date, end_date)
for stock_code in indicator_select_code_list:
    chi_name = find_stock_chi_name(stock_code)
    print(stock_code, ',', chi_name)

for stock_code in positive_select_code:
    print("positive num")
    chi_name = find_stock_chi_name(stock_code)
    print(stock_code, ',', chi_name)

for stock_code in negative_select_code:
    print("negative num")
    chi_name = find_stock_chi_name(stock_code)
    print(stock_code, ',', chi_name)

