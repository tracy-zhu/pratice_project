# -*- coding: utf-8 -*-
"""

# 根据股票的tick数据，还有lee_ready算法计算出主动成交的买金额和卖金额，和当天相对于总成交的比例作比较

# 主要是为了找出大盘在下跌过程中，主动买占比还比较高的股票；

WED 2018/5/2

@author: Tracy Zhu
"""
# 导入系统库
import sys
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from stock_base.stock_data_api import *

trading_day_list = get_trading_day_list()


def drop_duplicate_index(independent_value):
    """
    将具有重复index的series去掉
    :param independent_value:
    :return:
    """
    duplicate_value = independent_value[independent_value.index.duplicated()]
    new_independent_value = independent_value.drop(duplicate_value.index)
    return new_independent_value


def get_active_buy_series(stock_code, trading_day):
    """
    根据股票代码和lee_ready算法，计算出该股票的主动买成交额序列
    :param stock_code:“600001.SH”
    :param trading_day:"2018-05-29"
    :return:total_turnover:当天的总成交额， active_buy_ratio:当天主动买成交额； active_sell_ratio: 当天主动卖成交额
    """
    active_buy_money_list = []
    active_buy_ratio_list = []
    stock_df = read_stock_tick_data_qian(stock_code, trading_day)
    if len(stock_df) > 100:
        stock_df = drop_duplicate_index(stock_df)
        tick_match_volume = stock_df.volume.diff()
        tick_turnover = stock_df.amount.diff()
        for i in range(len(stock_df.index[:-1])):
            index = stock_df.index[i]
            next_index = stock_df.index[i+1]
            active_buy_money = 0
            active_buy_ratio = 0
            active_sell_money = 0
            first_bid_price = stock_df.bid[index]
            first_ask_price = stock_df.ask[index]
            next_bid_price = stock_df.bid[next_index]
            next_ask_price = stock_df.ask[next_index]
            if first_bid_price == next_bid_price and first_ask_price == next_ask_price:
                volume_bid = (tick_turnover[next_index] - first_ask_price * tick_match_volume[next_index]) / \
                             (first_bid_price - first_ask_price)
                volume_ask = (tick_turnover[next_index] - first_bid_price * tick_match_volume[next_index]) / \
                             (first_ask_price - first_bid_price)
                active_buy_money = volume_ask * first_ask_price
                active_buy_money = 0 if active_buy_money < 0 else active_buy_money
                active_buy_money = 0 if next_bid_price == 0 else active_buy_money
            elif next_ask_price > first_ask_price:
                active_buy_money = tick_turnover[next_index]
            elif next_bid_price < first_bid_price:
                active_buy_money = 0
            elif first_bid_price == next_bid_price and next_ask_price < first_ask_price:
                active_buy_money = 0
            elif first_ask_price == next_ask_price and next_bid_price > first_bid_price:
                active_buy_money = tick_turnover[next_index]
            if np.isnan(active_buy_money):
                active_buy_money = 0
            if np.isnan(active_sell_money):
                active_sell_money = 0
            if tick_turnover[next_index] != 0:
                active_buy_ratio = float(active_buy_money) / float(tick_turnover[next_index])
            active_buy_ratio_list.append(active_buy_ratio)
            active_buy_money_list.append(active_buy_money)
    active_buy_money_list.append(0)
    active_buy_ratio_list.append(0)
    active_buy_money_series = Series(active_buy_money_list, index=stock_df.index)
    active_buy_ratio_series = Series(active_buy_ratio_list, index=stock_df.index)
    return active_buy_money_series, active_buy_ratio_series


def lee_ready_algorithm_stock(stock_code, trading_day):
    """
    根据股票代码和lee_ready算法，计算出主动买和主动卖的成交金额
    :param stock_code:“600001.SH”
    :param trading_day:"2018-05-29"
    :return:total_turnover:当天的总成交额， active_buy_ratio:当天主动买成交额； active_sell_ratio: 当天主动卖成交额
    """
    total_turnover = 0
    active_buy_ratio = 0
    active_sell_ratio = 0
    total_active_buy_money = 0
    total_active_sell_money = 0
    stock_df = read_stock_tick_data_qian(stock_code, trading_day)
    if len(stock_df) > 100:
        stock_df = drop_duplicate_index(stock_df)
        tick_match_volume = stock_df.volume.diff()
        tick_turnover = stock_df.amount.diff()
        for i in range(len(stock_df.index[:-1])):
            index = stock_df.index[i]
            next_index = stock_df.index[i+1]
            active_buy_money = 0
            active_sell_money = 0
            first_bid_price = stock_df.bid[index]
            first_ask_price = stock_df.ask[index]
            next_bid_price = stock_df.bid[next_index]
            next_ask_price = stock_df.ask[next_index]
            if first_bid_price == next_bid_price and first_ask_price == next_ask_price:
                volume_bid = (tick_turnover[next_index] - first_ask_price * tick_match_volume[next_index]) / \
                             (first_bid_price - first_ask_price)
                volume_ask = (tick_turnover[next_index] - first_bid_price * tick_match_volume[next_index]) / \
                             (first_ask_price - first_bid_price)
                active_buy_money = volume_ask * first_ask_price
                active_sell_money = volume_bid * first_bid_price
                active_buy_money = 0 if active_buy_money < 0 else active_buy_money
                active_buy_money = 0 if next_bid_price == 0 else active_buy_money
            elif next_ask_price > first_ask_price:
                active_buy_money = tick_turnover[next_index]
                active_sell_money = 0
            elif next_bid_price < first_bid_price:
                active_sell_money = tick_turnover[next_index]
                active_buy_money = 0
            elif first_bid_price == next_bid_price and next_ask_price < first_ask_price:
                active_sell_money = tick_turnover[next_index]
                active_buy_money = 0
            elif first_ask_price == next_ask_price and next_bid_price > first_bid_price:
                active_buy_money = tick_turnover[next_index]
                active_sell_money = 0
            if np.isnan(active_buy_money):
                active_buy_money = 0
            if np.isnan(active_sell_money):
                active_sell_money = 0
            total_active_buy_money += active_buy_money
            total_active_sell_money += active_sell_money
        total_turnover = stock_df.amount.values[-1]
        active_buy_ratio = float(total_active_buy_money) / float(total_turnover)
        active_sell_ratio = float(total_active_sell_money) / float(total_turnover)
    return total_turnover, active_buy_ratio, active_sell_ratio


def get_average_buy_ratio(stock_code, start_date, end_date):
    """
    根据上面的stock_code计算出过去几个交易日的主动买的比例
    :param stock_code:
    :param start_date:
    :param end_date:
    :return: total_turnover: 最近几日的总成交金额， 最近几日主动买的占比比例；
    """
    total_turnover = 0
    total_active_buy = 0
    total_active_buy_ratio = 0
    for trade_day in trading_day_list:
        trade_day = trade_day[:-1]
        trading_day = change_trading_day_format(trade_day)
        if start_date <= trading_day <= end_date:
            print stock_code, trading_day
            day_turnover, day_active_buy_ratio, _ = lee_ready_algorithm_stock(stock_code, trading_day)
            total_active_buy += day_turnover * day_active_buy_ratio
            total_turnover += day_turnover
    if total_turnover != 0:
        total_active_buy_ratio = float(total_active_buy) / float(total_turnover)
    return total_turnover, total_active_buy_ratio


def get_sort_stock_by_active_buy(trading_day):
    """
    获取当天股票的active_buy_ratio, 并将所有的股票按照active_buy_ratio排序
    去除掉当天涨停跌停的股票。
    :param trading_day:
    :return:
    """
    active_buy_stock_dict = defaultdict()
    all_stock_code_list = get_all_stock_code_list(trading_day)
    stock_up_limit = find_stock_up_limit(trading_day, 1)
    stock_down_limit = find_stock_up_limit(trading_day, -1)
    for stock_code in all_stock_code_list:
        if stock_code not in stock_up_limit and stock_code not in stock_down_limit:
            print stock_code
            df_table = get_stock_df(stock_code, trading_day, trading_day)
            pct_chg = df_table.PCT_CHG.values[0]
            if pct_chg > 0:
                total_turnover, active_buy_ratio, active_sell_ratio = lee_ready_algorithm_stock(stock_code, trading_day)
                active_buy_stock_dict[stock_code] = active_buy_ratio
    active_buy_stock_series = Series(active_buy_stock_dict)
    sort_active_buy_stock = active_buy_stock_series.sort_values(ascending=False)
    return sort_active_buy_stock


def get_sort_stock_by_active_buy_days(start_date, end_date):
    """
    跟上面函数不同的是，这是获取一段时间的
    获取当天股票的active_buy_ratio, 并将所有的股票按照active_buy_ratio排序
    去除掉当天涨停跌停的股票。
    :param trading_day:
    :return:
    """
    active_buy_stock_dict = defaultdict()
    all_stock_code_list = get_all_stock_code_list(end_date)
    stock_up_limit = find_stock_up_limit(end_date, 1)
    stock_down_limit = find_stock_up_limit(end_date, -1)
    for stock_code in all_stock_code_list:
        if stock_code not in stock_up_limit and stock_code not in stock_down_limit:
                total_turnover, active_buy_ratio = get_average_buy_ratio(stock_code, start_date, end_date)
                active_buy_stock_dict[stock_code] = active_buy_ratio
    active_buy_stock_series = Series(active_buy_stock_dict)
    sort_active_buy_stock = active_buy_stock_series.sort_values(ascending=False)
    return sort_active_buy_stock


if __name__ == '__main__':
    stock_code = "002830.SZ"
    end_date = "2018-06-08"
    start_date = "2018-06-07"
    # sort_active_buy_stock = get_sort_stock_by_active_buy(end_date)
    sort_active_buy_stock = get_sort_stock_by_active_buy_days(start_date, end_date)
    sort_active_buy_stock.to_csv('active_buy_stock_week.csv')
    print sort_active_buy_stock.head()
