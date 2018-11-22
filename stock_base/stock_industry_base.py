# -*- coding: utf-8 -*-
"""

# 用于编写行业分析相关的基础代码；包括读取行业指数代码，行业指数日线数据；

@author: hp
"""


import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *


def get_industry_df(trading_day, level_flag):
    """
    根据trading_day, 得出指数的dataframe, 包括指数代码和对应的股票代码
    :param level_flag : 1代表1级行业， 2代表2级行业
    :return:
    """
    sql = ''
    if level_flag == 1:
        sql = 'SELECT * FROM stock_db.sw_ind1_tb WHERE date = \"{trading_day}\"'.format(trading_day=trading_day)
    elif level_flag == 2:
        sql = 'SELECT * FROM stock_db.sw_ind2_tb WHERE date = \"{trading_day}\"'.format(trading_day=trading_day)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    if len(df_table) > 0:
        df_table.columns = retrieve_column_name('stock_db', 'sw_ind1_tb')
    return df_table


def get_industry_df_test():
    """
    读取测试文件的三级行业文件，测试下三级行业是否能分的更细一点；
    :return:
    """
    test_file_name = 'E:\\quote_data\\industry_data\\industry_test.csv'
    industry_df = pd.read_csv(test_file_name)
    industry_df = industry_df.drop('Unnamed: 0', 1)
    return industry_df


def find_stock_industry_name(stock_code, industry_df):
    """
    根据股票代码，找出对应的一级行业，或者二级行业
    :param stock_code:
    :param trading_day:
    :param level_flag : 1代表1级行业， 2代表2级行业
    :return:
    """
    block_code = None
    block_name = None
    select_df = industry_df[industry_df.wind_code == stock_code]
    if len(select_df) > 0:
        block_code = select_df.block_code.values[0]
        block_name = select_df.block_name.values[0]
    return block_code, block_name


def get_industry_code(trading_day, level_flag):
    """
    根据上面得出的industry_df, 得出当天所有的行业代码
    :param trading_day:
    :param level_flag: 1,2
    :return:
    """
    industry_code_list = []
    industry_df = get_industry_df(trading_day, level_flag)
    if len(industry_df) > 0:
        industry_code_list = industry_df.block_code.unique()
    return industry_code_list


def get_industry_stock_code(industry_df, industry_code):
    """
    根据行业代码；找出对应该行业代码对应的股票代码
    :param industry_df:
    :param industry_code:
    :return:
    """
    select_df = industry_df[industry_df.block_code == industry_code]
    stock_code_list = list(select_df.wind_code.values)
    return stock_code_list


def sort_stock_by_market_value(stock_code_list, trading_day):
    """
    将给定的stock_code_list,按照股票市值从大到小排序
    """
    market_value_dcit = defaultdict()
    for stock_code in stock_code_list:
        market_value = calc_stock_market_value(stock_code, trading_day)
        market_value_dcit[stock_code] = market_value
    market_value_series = Series(market_value_dcit)

    # 将大市值判断为龙头股，认为大市值的股票会先涨
    market_value_series = market_value_series.sort_values(ascending=False)

    # 将小市值的股票判断为龙头股，认为小市值的股票会先涨；
    # market_value_series = market_value_series.sort_values()
    sort_stock_code_by_market_value = list(market_value_series.index)
    return sort_stock_code_by_market_value


def calc_stock_list_mean_pct(stock_code_list, trading_day, back_period):
    """
    计算stock_code_list在回看区间的平均收益率和收益率的标准差
    :param stock_code_list:
    :param trading_day:
    :param back_period: 代表回溯的区间，1周：5， 一月：22等
    :return:
    """
    pct_chg_series = get_stock_list_description(stock_code_list, trading_day, back_period)
    pct_chg_mean = pct_chg_series.mean()
    pct_chg_std = pct_chg_series.std()
    return pct_chg_mean, pct_chg_std


def find_industry_leading_stock(industry_df, industry_code, trading_day):
    """
    根据市值因子找出该行业的龙头股票；
    采取市值前后10%计算，行业股票至少大于等于10只；
    """
    limit_percent = 0.1
    lead_stock_list = []
    follow_stock_list = []
    stock_code_list = get_industry_stock_code(industry_df, industry_code)
    if len(stock_code_list) >= 10:
        sort_stock_code_by_market_value = sort_stock_by_market_value(stock_code_list, trading_day)
        split_num = int(limit_percent * len(sort_stock_code_by_market_value))
        lead_stock_list = sort_stock_code_by_market_value[:split_num] 
        follow_stock_list = sort_stock_code_by_market_value[split_num:]
    return lead_stock_list, follow_stock_list, stock_code_list


def fetch_industry_code_daily_data(industry_code, start_date, end_date):
    """
    根据industry_code, 获取行业的日数据
    :param industry_code: '801780.SI'
    :param start_date: '2018-05-02'
    :param end_date:
    :return:
    """
    db_name = str(industry_code.split('.')[0]) + "_sl_tb"
    sql = 'SELECT * FROM daily_market_ths_db.{db_name} WHERE time >= \"{start_date}\" and time <= \"{end_date}\"'\
        .format(db_name=db_name, start_date=start_date, end_date=end_date)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    df_table.columns = retrieve_column_name('daily_market_ths_db', db_name)
    return df_table


def find_industry_up_limit_stock(industry_df, industry_code, trading_day):
    """
    找出当天该板块有多少只股票涨停
    :param industry_df:
    :param industry_code:
    :param trading_day:
    :return:
    """
    up_stock_ind_list = []
    stock_code_list = get_industry_stock_code(industry_df, industry_code)
    up_stock_list = find_stock_up_limit(trading_day, 1)
    for stock_code in stock_code_list:
        if stock_code in up_stock_list:
            up_stock_ind_list.append(stock_code)
    return up_stock_ind_list


def calc_industry_feature(industry_code, start_date, end_date):
    """
    计算单行业的平均换手率，过去一段时间的波动率指标
    :param industry_code:
    :param start_date:
    :param end_date:
    :return:
    """
    industry_df = fetch_industry_code_daily_data(industry_code, start_date, end_date)
    pass


if __name__ == '__main__':
    trading_day = '2018-05-09'
    level_flag = 2
    stock_code = "600436.SH"
    start_date = '2018-04-20'
    end_date = '2018-05-09'
    industry_code_list = get_industry_code(trading_day, level_flag)
