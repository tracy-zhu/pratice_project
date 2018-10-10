# -*- coding: utf-8 -*-
"""

# 将行业中资金净流入占比比较大的行业找出来；

# 由于不同行业的市值，和当日的成交额不同，考虑用行业的市值或者是行业的平均成交额进行标准化

Mon 2018/07/02

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_industry_base import *
from stock_high_frequency_analysis.stock_lee_ready_algorithm import *

trading_day_list = get_trading_day_list()


def calc_industry_capital_inflow(industry_code, trading_day, industry_df):
    """
    计算每个板块的资金净流入量，根据stock_lee_ready算法计算每个股票单独的资金净流入
    :param industry_code:
    :param trading_day:
    :return:
    """
    total_active_buy_money = 0
    total_net_buy_money = 0
    stock_code_list = get_industry_stock_code(industry_df, industry_code)
    for stock_code in stock_code_list:
        total_turnover, active_buy_ratio, active_sell_ratio = lee_ready_algorithm_stock(stock_code, trading_day)
        active_buy_money = total_turnover * active_buy_ratio
        active_sell_money = total_turnover * active_sell_ratio
        net_buy_money = active_buy_money - active_sell_money
        total_active_buy_money += active_buy_money
        total_net_buy_money += net_buy_money
    return total_active_buy_money, total_net_buy_money


def get_industry_capital_inflow_series(industry_code, end_date, back_period, industry_df):
    """
    计算该行业板块过去一段时间流入的资金序列
    :param industry_code:
    :param trading_day:当前日期
    :param back_period:回看天数
    :param industry_df:
    :return:
    """
    total_active_buy_money_list = []
    total_net_buy_money_list = []
    start_date = get_next_trading_day_stock(end_date, -1 * back_period)
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        trading_day = change_trading_day_format(trading_day)
        if start_date <= trading_day <= end_date:
            total_active_buy_money, total_net_buy_money = calc_industry_capital_inflow(industry_code, trading_day, industry_df)
            total_active_buy_money_list.append(total_active_buy_money)
            total_net_buy_money_list.append(total_net_buy_money)
    return total_active_buy_money_list, total_net_buy_money_list


def calc_net_buy_money_blow(active_buy_money_list):
    """
    计算最后一天的买量相对于前n天的平均净买量放大的比例
    :param active_buy_money_list:
    :return:
    """
    blow_up_ratio = 0
    mean_active_buy_money = np.mean(active_buy_money_list[:-1])
    if mean_active_buy_money != 0:
        blow_up_ratio = float(active_buy_money_list[-1]) / float(mean_active_buy_money)
    return blow_up_ratio


if __name__ == '__main__':
    out_file_name = "..\\stock_industry_analysis\\result\\active_buy_ratio.csv"
    f = open(out_file_name, 'wb')
    trading_day = '2018-07-03'
    industry_df = get_industry_df(trading_day, 1)
    back_period = 6
    industry_code_list = industry_df.block_code.unique()
    f.write('industry_code, active_buy_blow_up, net_buy_blow_up\n')
    for industry_code in industry_code_list:
        print industry_code
        total_active_buy_money_list, total_net_buy_money_list = get_industry_capital_inflow_series(industry_code, trading_day, back_period, industry_df)
        active_buy_blow_up = calc_net_buy_money_blow(total_active_buy_money_list)
        net_buy_blow_up = calc_net_buy_money_blow(total_net_buy_money_list)
        str_line = industry_code + ',' + str(active_buy_blow_up) + ',' + str(net_buy_blow_up) + '\n'
        f.write(str_line)
    f.close()

        
