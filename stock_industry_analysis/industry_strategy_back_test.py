# -*- coding: utf-8 -*-
"""

# 根据该文件夹下的其他脚本，行业选择的策略代码

# 对此进行回测，选择基准为wind全A指数或者沪深300指数；

Mon 2018/06/25

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_industry_analysis.lead_stock_primacy import *
from stock_industry_analysis.industry_index_custom import *
from python_base.plot_method import *

out_file_folder = '..\\stock_industry_analysis\\result\\back_test\\'
trading_day_list = get_trading_day_list()

# param list
# 决定选出前多少的行业板块
limit_industry_num = 5


def select_industry_code(trading_day, back_period, level_flag):
    """
    选出那一个交易日的选出的前几industry_code,要修改策略就用这个函数修改
    :param trading_day:
    :param back_period:
    :return:
    """
    global limit_industry_num
    # herding_index_series = sort_industry_by_herding_index(trading_day, back_period, level_flag)
    herding_index_series = sort_industry_by_custom_momentum(trading_day, back_period, level_flag)
    industry_code_list = list(herding_index_series.index)[:limit_industry_num]
    return industry_code_list


def back_test_industry_code_out(start_date, end_date, back_period):
    """
    根据筛选行业代码的条件，将持仓指数输出到一个csv文件中，用于钱哥的回测代码；
    :param start_date: '2018-01-01'
    :param end_date: '2018-08-09'
    :param back_period:
    :return:
    """
    level_flag = 1
    out_file_name = out_file_folder + "position_back_test_level.csv"
    f = open(out_file_name, 'wb')
    f.write(',time,position,code\n')
    index_num = 0
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        weekday = datetime.strptime(trading_day, '%Y%m%d').weekday()
        trading_day = change_trading_day_format(trading_day)
        if start_date <= trading_day <= end_date and weekday == 4:
            industry_code_list = select_industry_code(trading_day, back_period, level_flag)
            industry_position_dict = calc_industry_position_equal_market(industry_code_list, trading_day)
            for industry_code, position in industry_position_dict.items():
                str_code = str(industry_code.split('.')[0]) + ".SL"
                str_line = str(index_num) + ',' + trading_day + ',' + str(position) + ',' + str_code + '\n'
                f.write(str_line)
                index_num += 1
    f.close()


def calc_industry_position_equal_market(industry_code_list, trading_day):
    """
    根据等市值权重计算每个板块的分配的仓位；
    :param industry_code_list:
    :param trading_day:
    :return:
    """
    industry_position_dict = defaultdict()
    initial_money = 100000000
    each_industry_money = float(initial_money) / len(industry_code_list)
    for industry_code in industry_code_list:
        industry_df = fetch_industry_code_daily_data(industry_code, trading_day, trading_day)
        close_price = industry_df.CLOSE.values[-1]
        position = float(each_industry_money) / float(close_price)
        industry_position_dict[industry_code] = position
    return industry_position_dict


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


def back_test_market_value(start_date, end_date, back_period, holding_period):
    """
    对每个板块采用相等的市值进行回测
    :param start_date:回测开始日期
    :param end_date:回测结束日期
    :param back_period:参数回看日期
    :param holding_period:每次的持仓时间
    :return:
    """
    global limit_industry_num, level_flag
    strategy_net_value = 1
    strategy_net_list = [1]
    begin_day = start_date
    bin_shift_day = get_next_trading_day_stock(start_date, holding_period)
    while bin_shift_day <= end_date:
        # 换仓那天的数据是用不到的，所以选择用前一天的数据生成选择列表
        pre_begin_day = get_next_trading_day_stock(begin_day, -1)
        industry_code_list = select_industry_code(pre_begin_day, back_period, 2)
        industry_hold_yield, mean_yield_series = select_code_list_holding_period(industry_code_list, begin_day, holding_period)
        period_yield_series = strategy_net_value * mean_yield_series
        strategy_net_list = strategy_net_list + list(period_yield_series)
        begin_day = bin_shift_day
        bin_shift_day = get_next_trading_day_stock(begin_day, holding_period)
        strategy_net_value = strategy_net_value * mean_yield_series.values[-1]
        print begin_day
    strategy_net_series = Series(strategy_net_list)
    return strategy_net_series


def fetch_bench_market_yield(start_date, end_date):
    """
    得出基准指数的走势，可以用wind全A指数或者沪深300指数
    :param start_date:
    :param end_date:
    :return:
    """
    pass


def result_print_out(strategy_net_series):
    """
    将计算的净值结果输出出来，包括输出到csv和绘制成图形；
    :param strategy_net_series:
    :return:
    """
    fig, ax = plt.subplots(figsize=(23.2, 14.0))
    ax.plot(strategy_net_series, color='r', label='net yield')
    # ax.plot(mid_price_series.values[begin_N:end_N], color='pink', label='middle price')
    ax.legend(loc='best')
    title = "net yield series"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)

    csv_file_name = out_file_folder + "net_yield_series.csv"
    strategy_net_series.to_csv(csv_file_name)


if __name__ == '__main__':
    start_date = '2016-01-01'
    end_date = '2018-10-08'
    back_period = 5
    holding_period = 5
    back_test_industry_code_out(start_date, end_date, back_period)
    # strategy_net_series = back_test_market_value(start_date, end_date, back_period, holding_period)
    # result_print_out(strategy_net_series)