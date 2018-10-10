# -*- coding: utf-8 -*-
"""

# 本脚本用来统计郑商所在集合竞价发生的交易次数

# 将交易次数大于某个阀值的交易日和合约筛选出来

# 输出一个DataFrame到一个csv中

Tue 2016/12/21

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *
trading_day_list = get_trading_day_list()

#variety_id_list = ['SR', 'CF', 'TA', 'RM', 'FG', 'MA', 'ZC']
variety_id_list = ['ZC']
open_time = '20:59:00'
limit_period_num = 15
limit_last_tick_change = 7


def get_deal_times_before_open_auction(main_instrument_id, trading_day):
    main_quote_data = read_data(main_instrument_id, trading_day)
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0:
        trade_times = main_open_quote.index.values[0] - 1
    else:
        trade_times = 0
    return trade_times


def get_last_period_change_before_open_auction(instrument_id, trading_day):
    """
    找出集合竞价最后一笔波动超过Limit last tick change合约和交易日
    :param instrument_id:
    :param trading_day:
    :return:
    """
    pass


def get_max_deviation_during_open_auction():
    pass


if __name__ == '__main__':
    result_file = "..\\open_price_strategy\\result\\czce_deal_times_before_open_auction_zc.csv"
    f = open(result_file, 'wb')
    f.write('instrument_id, trading_day, trade_times\n')
    trade_times_list = []
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day > '20170501':
            for variety_id in variety_id_list:
                main_instrument_id, _ = get_variety_main(variety_id, trading_day)
                if main_instrument_id != None:
                    print main_instrument_id, trading_day
                    trade_times = get_deal_times_before_open_auction(main_instrument_id, trading_day)
                    trade_times_list.append(trade_times)
                    #if trade_times > limit_period_num:
                    str_line = main_instrument_id + ',' + trading_day + ',' + str(trade_times) + '\n'
                    f.write(str_line)
    f.close()
