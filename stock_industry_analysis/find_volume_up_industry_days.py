# -*- coding: utf-8 -*-
"""

# 根据同文件夹下volume_up_industry找出过去交易日中，一个行业筛选的股票数大于一定个数8只以上的；

# 主要是为了像2018.7.18那样能够把电力板块筛选出来；

Fri 2018/07/31

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_industry_analysis.industry_stock_analysis import *
from stock_base.stock_industry_base import *

ma_num = 10
level_flag = 2
# 板块当天至少选出的股票个数
limit_num = 8 
trading_day_list = get_trading_day_list()


def find_condition_industry_days(start_date, end_date, limit_num):
    """
    找出指定区间符合条件的板块，观察后期的走势
    :param start_date: "2018-07-16"
    :param end_date:
    :return:
    """
    global ma_num, level_flag
    out_file_name = out_file_folder + 'volume_up_industry_days.csv'
    f = open(out_file_name, 'wb')
    f.write('industry_code, trading_day, stock_num\n')
    for trade_day in trading_day_list:
        trade_day = trade_day[:-1]
        trading_day = change_trading_day_format(trade_day)
        if start_date <= trading_day <= end_date:
            print trading_day
            select_df = sort_stock_by_volume_ratio(trading_day, ma_num)
            industry_dict = find_stock_industry_sort(select_df, industry_df)
            select_industry_dict = judge_industry_dict_condition(industry_dict, limit_num)
            if len(select_industry_dict) > 0:
                for industry_code, stock_num in select_industry_dict.items():
                    str_line = industry_code + ',' + trading_day + ',' + str(stock_num) + '\n'
                    f.write(str_line)
    f.close()


def judge_industry_dict_condition(industry_dict, limit_num):
    select_industry_dict = defaultdict()
    for industry_code, stock_code_list in industry_dict.items():
        all_stock_code_list = get_industry_stock_code(industry_df, industry_code)
        if len(stock_code_list) >= limit_num or len(stock_code_list) >= len(all_stock_code_list) * 0.25:
            select_industry_dict[industry_code] = len(stock_code_list)
    return select_industry_dict


def industry_holding_profit(industry_code, trading_day, holding_period):
    """
    计算行业指数这段时间获得的收益, 分别返回绝对收益和相对收益；
    :param industry_code:
    :param trading_day:
    :param holding_period:
    :return:
    """
    holding_profit = 0
    comparative_index_profit = 0
    end_date = get_next_trading_day_stock(trading_day, holding_period)
    start_date = get_next_trading_day_stock(trading_day, 1)
    industry_df = fetch_industry_code_daily_data(industry_code, start_date, end_date)
    open_price = industry_df.OPEN.values[0]
    close_price = industry_df.CLOSE.values[-1]
    index_df = get_index_data('000300.SH', start_date, end_date)
    index_open_price = index_df.open.values[0]
    index_close_price = index_df.close.values[-1]
    if open_price != 0 and index_open_price !=0 :
        holding_profit = float(close_price) / float(open_price) - 1
        index_profit = float(index_close_price) / float(index_open_price) - 1
        comparative_index_profit = holding_profit - index_profit
    return holding_profit, comparative_index_profit


def industry_holding_profit_by_stock(industry_code, trading_day, holding_period, back_period, limit_percent):
    """
    上面一个函数是直接根据指数的成分进行后面持有收益的分布，后面是持有的股票收益进行的分布
    :param industry_code:
    :param trading_day:
    :param holding_period:
    :return:
    """
    comparative_index_profit = 0
    # select_code_list = select_code_from_industry_reverse(industry_code, trading_day, back_period, limit_percent)
    select_code_list = select_code_from_industry_by_quantile(industry_code, trading_day)
    end_date = get_next_trading_day_stock(trading_day, holding_period)
    start_date = get_next_trading_day_stock(trading_day, 1)
    index_df = get_index_data('000300.SH', start_date, end_date)
    index_open_price = index_df.open.values[0]
    index_close_price = index_df.close.values[-1]
    sort_stock_yield, mean_yield = select_code_industry_holding_profit(select_code_list, start_date, end_date)
    if index_open_price !=0 :
        index_profit = float(index_close_price) / float(index_open_price) - 1
        comparative_index_profit = mean_yield - index_profit
    return mean_yield, comparative_index_profit


def industry_holding_profit_out(result_file_name, holding_period):
    f = open(result_file_name, 'r')
    str_lines = f.readlines()
    f.close()
    out_file_name = out_file_folder + 'industry_holding_profit_' + str(holding_period) + '.csv'
    w = open(out_file_name, 'wb')
    w.write('industry_code,trading_day,stock_num,holding_profit,comparative_index_profit,up_stock_num\n')
    for line in str_lines[1:]:
        industry_code = line.split(',')[0]
        trading_day = line.split(',')[1]
        stock_num = line.split(',')[-1][:-1]
        up_stock_ind_list = find_industry_up_limit_stock(industry_df, industry_code, trading_day)
        if len(up_stock_ind_list) > 0:
            holding_profit, comparative_index_profit = industry_holding_profit(industry_code, trading_day, holding_period)
            str_line = industry_code + ',' + trading_day + ',' + str(stock_num) + ',' + str(holding_profit) + ',' + str(comparative_index_profit) + ',' + str(len(up_stock_ind_list)) + '\n'
            w.write(str_line)
    w.close()


def industry_holding_profit_out_by_stock(result_file_name, holding_period):
    """
    这是根据选出的股票来分析选出来板块之后几天的持仓分析
    :param result_file_name:
    :param holding_period:
    :return:
    """
    back_period = 15
    limit_percent = 0.3
    f = open(result_file_name, 'r')
    str_lines = f.readlines()
    f.close()
    out_file_name = out_file_folder + 'industry_holding_profit_by_stock_03' + str(holding_period) + '.csv'
    w = open(out_file_name, 'wb')
    w.write('industry_code,trading_day,stock_num,holding_profit,comparative_index_profit,up_stock_num\n')
    for line in str_lines[1:]:
        industry_code = line.split(',')[0]
        trading_day = line.split(',')[1]
        stock_num = line.split(',')[-1][:-1]
        up_stock_ind_list = find_industry_up_limit_stock(industry_df, industry_code, trading_day)
        if len(up_stock_ind_list) > 0:
            holding_profit, comparative_index_profit = industry_holding_profit_by_stock(industry_code, trading_day, holding_period, back_period, limit_percent)
            str_line = industry_code + ',' + trading_day + ',' + str(stock_num) + ',' + str(holding_profit) + ',' + str(comparative_index_profit) + ',' + str(len(up_stock_ind_list)) + '\n'
            w.write(str_line)
    w.close()


def result_analysis(profit_file_name):
    """
    对输出的结果进行分析
    :param profit_file_name:
    :return:
    """
    profit_df = pd.read_csv(profit_file_name)
    holding_profit = profit_df.holding_profit
    comparative_index_profit = profit_df.comparative_index_profit
    holding_profit.hist()
    comparative_index_profit.hist()
    print "average holding profit is " + str(holding_profit.mean())
    print "comparative holding profit is " + str(comparative_index_profit.mean())


if __name__ == '__main__':
    start_date = '2017-01-01'
    end_date = '2018-08-31'
    limit_num = 5
    # find_condition_industry_days(start_date, end_date, limit_num)
    result_file_name = out_file_folder + 'volume_up_industry_days.csv'
    holding_period = 5
    industry_holding_profit_out_by_stock(result_file_name, holding_period)
    industry_holding_profit_out(result_file_name, holding_period)
    # profit_file_name = out_file_folder + 'industry_holding_profit_' + str(holding_period) + '.csv'
    profit_file_name = out_file_folder + 'industry_holding_profit_by_stock_03' + str(holding_period) + '.csv'
