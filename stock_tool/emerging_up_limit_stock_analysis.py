# -*- coding: utf-8 -*-
"""

# 找出间隔很久没有涨停，在早上涨停且后面没有打开的股票

WED 2018/03/14

@author: Tracy Zhu
"""

# 导入系统库
import sys
from WindPy import w


# 导入用户库
sys.path.append("..")
from stock_tool.up_limit_stock_num import *
interval_period = timedelta(60)

stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', '2018-03-13', '2018-03-13')
raw_stock_code_list = stock_df.code.unique()


def find_stock_up_limit_days(stock_code, all_up_limit_data, start_date):
    """
    找出一个股票代码涨停的天数,满足在一个日期之后，并且当天涨停之后没有打开
    :param stock_code:
    :param all_up_limit_data: 所有股票的涨停数据
    :return:
    """
    result_list = []
    df_table = all_up_limit_data[all_up_limit_data['code'] == stock_code]
    df_table = df_table[df_table.time >= start_date]
    if len(df_table) > 1:
        is_always_up_limit_list = []
        delta_time = df_table.time.diff()
        concat_df = pd.concat([df_table.time, delta_time], axis=1)
        concat_df.columns = ['trade_time', 'time_delta']
        for index_num in concat_df.index:
            time_index = concat_df.loc[index_num]['trade_time']
            trading_day = str(time_index)
            time_delta = concat_df.loc[index_num]['time_delta']
            if trading_day >= "2017-11-13" and time_delta > interval_period:
                _, is_always_up_limit = find_stock_up_limit_time_from_raw_data(stock_code, trading_day)
                if is_always_up_limit == 1:
                   result_list.append((stock_code, trading_day, time_delta))
    return result_list


def get_all_condition_code(raw_stock_code_list, all_up_limit_data, start_date):
    """
    将股票中所有符合情况的日期和股票列举出来
    :param raw_stock_code_list:
    :param all_up_limit_data:
    :param start_date:
    :return:
    """
    condition_list = []
    for stock_code in raw_stock_code_list:
        print stock_code
        result_list = find_stock_up_limit_days(stock_code, all_up_limit_data, start_date)
        condition_list = condition_list + result_list
    return condition_list


def get_stock_after_trend(stock_code, trading_day, hold_days):
    """
    根据stock_code和trading_day，将后面几天的走势列出来；
    :param stock_code:
    :param trading_day:
    :param hold_days:
    :return:
    """
    yield_list = []
    next_day = get_next_trading_day_stock(trading_day, 1)
    end_date = get_next_trading_day_stock(trading_day, hold_days + 1)
    stock_df = get_stock_df(stock_code, next_day, end_date)
    cum_yield = stock_df['CLOSE'] / stock_df['OPEN'].values[0]
    for yield_value in cum_yield:
        if yield_value < 0 or yield_value > 8:
            yield_value = 1
        yield_list.append(yield_value)
    yield_series = Series(yield_list)
    # cum_yield.index = stock_df.time
    return yield_series


def get_after_trend_all(condition_list):
    """
    将每个符合条件的之后的行情走势绘制出来，返回一个字典
    每个日期和符合条件的代码都是一个key
    :param condition_list:
    :return:
    """
    cum_yield_dict = defaultdict()
    for stock_code, trading_day, time_delta in condition_list:
        print stock_code, trading_day
        key_name = stock_code + "_" + trading_day
        cum_yield = get_stock_after_trend(stock_code, trading_day, hold_days=22)
        cum_yield_dict[key_name] = cum_yield
    cum_yield_df = DataFrame(cum_yield_dict)
    mean_yield = cum_yield_df.mean(axis=1)
    return cum_yield_df, mean_yield


def condition_list_second_filter(condition_list, limit_interval_period):
    """
    对condition_list作二次筛选，将limit_interval_period放大看
    :param condition_list: 由get_all_condition_code生成的condition_list
    :param limit_interval_period: timedelta(N)格式
    :return:
    """
    new_condition_list = []
    for condition_value in condition_list:
        delta_time = condition_value[2]
        if delta_time >= limit_interval_period:
            new_condition_list.append(condition_value)
    return new_condition_list


def cum_yield_df_describe(cum_yield_df):
    """
    对cum_yield_df进行统计，得到之后每个交易日的平均收益率，最大收益率和最小收益率
    :param cum_yield_df:
    :return:
    """
    max_yield_list = []
    min_yield_list = []
    mean_yield_list = []
    for index_day in cum_yield_df.index:
        day_yield = cum_yield_df.loc[index_day]
        day_yield = day_yield.dropna()
        max_yield_list.append(day_yield.max())
        min_yield_list.append(day_yield.min())
        mean_yield_list.append(day_yield.mean())
    fig, ax = plt.subplots()
    ax.plot(max_yield_list, label='max_yield_list')
    ax.plot(min_yield_list, label='min_yield_list')
    ax.plot(mean_yield_list, label='mean_yield_list')
    ax.legend(loc='best')


if __name__ == '__main__':
    sql_sentence = 'SELECT time, code FROM stock_db.stock_trade_status_tb where MAXUPORDOWN = 1'
    tp_table = fetchall_sql(sql_sentence)
    all_up_limit_data = pd.DataFrame(list(tp_table),
                            columns=['time', 'code'])
    start_str = '2013-05-27'
    date_time = datetime.strptime(start_str, "%Y-%m-%d")
    start_date = date(date_time.year, date_time.month, date_time.day)
    condition_list = get_all_condition_code(raw_stock_code_list, all_up_limit_data, start_date)
    cum_yield_dict = get_after_trend_all(condition_list)

