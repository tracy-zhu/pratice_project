# -*- coding: utf-8 -*-
"""

# 统计描述李叔所说的技术分析的第一个策略

# 可以在加一个股价在底部的策略

# (1)短期上涨，5/10多排，股价站上55日均线5个交易日内。(2)前一日冲击涨停，回落后，形成长上影射击之星或者锤头线。(3)第二天高开 or 小幅低开迅速突破昨日实体。

Tue 2018/07/27

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *

trading_day_list = get_trading_day_list()
list_A = get_all_stock_code_list("2018-07-20")
out_file_folder = "..\\techiniacl_analysis_stock\\result\\"
back_period = 5
withdraw_percent = 0.05


def judge_stock_is_condition(stock_code, start_date, end_date, f):
    """
    判断一只股票在指定区间中满足3个条件的交易日
    start_date: '20180712"
    """
    global withdraw_percent
    stock_df = get_stock_df_qfq(stock_code, start_date, end_date)
    stock_df['MA_5'] = stock_df.groupby('code')['CLOSE'].apply(lambda x: x.rolling(window=5).mean())
    stock_df['MA_10'] = stock_df.groupby('code')['CLOSE'].apply(lambda x: x.rolling(window=10).mean())
    stock_df['MA_55'] = stock_df.groupby('code')['CLOSE'].apply(lambda x: x.rolling(window=55).mean())
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if start_date <= trading_day <= end_date:
            bottom_flag = judge_stock_is_bottom(stock_df, trading_day)
            if bottom_flag:
                one_flag = judge_condition_1(stock_df, trading_day)
                if one_flag:
                    two_flag = judge_condition_2(stock_df, trading_day, withdraw_percent)
                    if two_flag:
                        buy_price = judge_condition_3(stock_df, trading_day)
                        if buy_price != 0:
                            trading_day_str = change_trading_day_format(trading_day)
                            str_line = stock_code + ',' + trading_day_str + ',' + str(buy_price) + '\n'
                            f.write(str_line)


def judge_stock_is_bottom(stock_df, trading_day):
    """
    判断一只股票当前股价是位于高位还是底部
    :param stock_df:
    :param trading_day:
    :return:
    """
    bottom_flag = False
    trading_date = change_trading_day_date(trading_day)
    select_df = stock_df[stock_df.time <= trading_date]
    if len(select_df) > 0:
        close_price = select_df.CLOSE.values[-1]
        close_price_series = stock_df.CLOSE
        median_close = close_price_series.median()
        if close_price <= median_close:
            bottom_flag = True
    return bottom_flag


def judge_condition_1(stock_df, trading_day):
    """
    根据stock_df判断当前交易日是否满足条件1；
    短期上涨，5/10多排
    """
    global back_period
    is_flag = False
    pre_trading_day = get_next_trading_day(trading_day, -1 * back_period)
    pre_trading_date = change_trading_day_date(pre_trading_day)
    trading_date = change_trading_day_date(trading_day)
    select_df = stock_df[stock_df.time >= pre_trading_date]
    select_df = select_df[select_df.time <= trading_date]
    ma_5_list = select_df["MA_5"].values
    ma_10_list = select_df["MA_10"].values
    if len(ma_5_list) > 0 and len(ma_10_list) > 0:
        if ma_5_list[-1] > ma_10_list[-1] and ma_5_list[-1] > ma_5_list[0]:
            is_flag = True
    return is_flag


def judge_condition_2(stock_df, trading_day, withdraw_percent):
    """
    根据stock_df判断当前交易日是否满足条件2；
    (2)前一日冲击涨停，回落后，形成长上影射击之星或者锤头线。
    涨停当天的close_price, 距离涨停板最高价回调幅度有一定比例；可以先设置一个参数；
    withdraw_percent: 最后收盘价相对于涨停价的回撤比例
    """
    judge_flag = False
    pre_trading_day = get_next_trading_day(trading_day, -1)
    pre_trading_date = change_trading_day_date(pre_trading_day)
    pre_2_trading_day = get_next_trading_day(trading_day, -2)
    pre_2_trading_date = change_trading_day_date(pre_2_trading_day)
    select_df = stock_df[stock_df.time >= pre_2_trading_date]
    select_df = select_df[select_df.time <= pre_trading_date]
    pre_close_price = select_df.CLOSE.values[0]
    high_price = select_df.HIGH.values[-1]
    close_price = select_df.CLOSE.values[-1]
    if high_price > pre_close_price * (1 + 0.095):
        if close_price <= pre_close_price * (1.1 - withdraw_percent):
            judge_flag = True
    return judge_flag
    

def judge_condition_3(stock_df, trading_day):
    """
    根据stock_df判断当前交易日是否满足条件3；
    (3)第二天高开 or 小幅低开迅速突破昨日实体。
    得出开仓价，如果不满足开仓条件，则开仓价为0
    并且开仓价大于55日均线；
    如果开仓当天是一字板就算了；
    """
    buy_price = 0
    pre_trading_day = get_next_trading_day(trading_day, -1)
    pre_trading_date = change_trading_day_date(pre_trading_day)
    trading_date = change_trading_day_date(trading_day)
    select_df = stock_df[stock_df.time >= pre_trading_date]
    select_df = select_df[select_df.time <= trading_date]
    pre_high_price = stock_df.HIGH.values[0]
    open_price = select_df.OPEN.values[-1]
    high_price = select_df.HIGH.values[-1]
    ma_55_value = select_df["MA_55"].values[-1]
    if open_price >= pre_high_price and open_price != high_price:
        if open_price >= ma_55_value:
            buy_price = open_price
    elif 0.95 * pre_high_price < open_price < pre_high_price and high_price > pre_high_price:
        if pre_high_price >= ma_55_value:
            buy_price = pre_high_price
    return buy_price


def print_select_code_out(start_date, end_date):
    """
    将交易日选择的股票输出出来；
    :param start_date:
    :param end_date:
    :param back_period:
    :param limit_percent:
    :return:
    """
    out_file_name = out_file_folder + "technical_one_result.csv"
    f = open(out_file_name, 'wb')
    f.write('stock_code,trading_day,buy_price, profit_yield\n')
    for stock_code in list_A:
        print(stock_code)
        judge_stock_is_condition(stock_code, start_date, end_date, f)
    f.close()


def stock_holding_description(stock_code, trading_day, holding_period, buy_price):
    """
    计算股票开仓之后的持仓收益，
    :param stock_code:
    :param trading_day:
    :param holding_period:
    :param buy_price:
    :return:
    """
    profit_yield = 0
    end_date = get_next_trading_day_stock(trading_day, holding_period)
    start_date = get_next_trading_day_stock(trading_day, 1)
    stock_df = get_stock_df_qfq(stock_code, start_date, end_date)
    close_price = stock_df.CLOSE.values[-1]
    if close_price > 0:
        profit_yield = float(close_price) / float(buy_price) - 1
    return profit_yield


def result_analysis(result_file_name, holding_period):
    """
    对输出的股票进行分析
    :param result_file_name:
    :return:
    """
    f = open(result_file_name, 'r')
    str_lines = f.readlines()
    f.close()
    out_file_name = out_file_folder + "holding_profit_" + str(holding_period) + '.csv'
    w = open(out_file_name, 'wb')
    w.write('stock_code,trading_day,buy_price,profit_yield\n')
    for str_line in str_lines[1:]:
        stock_code = str_line.split(',')[0]
        trading_day = str_line.split(',')[1]
        buy_price = float(str_line.split(',')[2])
        profit_yield = stock_holding_description(stock_code, trading_day, holding_period, buy_price)
        str_line = stock_code + ',' + trading_day + ',' + str(buy_price) + ',' + str(profit_yield) + '\n'
        w.write(str_line)
    w.close()


def profit_analysis(profit_file_name):
    df = pd.read_csv(profit_file_name)
    yield_series = df['profit_yield']
    win_yield_series = yield_series[yield_series > 0]
    win_ratio = float(len(win_yield_series)) / float(len(yield_series))
    yield_series.hist()
    print(yield_series.mean())
    print(win_ratio)


if __name__ == '__main__':
    start_date = '20180101'
    end_date = '20180727'
    # print_select_code_out(start_date, end_date)
    result_file_name = out_file_folder + "technical_one_result.csv"
    holding_period = 3
    result_analysis(result_file_name, holding_period)
    # profit_file_name = out_file_folder + "holding_profit_" + str(holding_period) + '.csv'

