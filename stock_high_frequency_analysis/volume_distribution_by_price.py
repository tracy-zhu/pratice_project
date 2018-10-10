# -*- coding: utf-8 -*-
"""

# 根据股票的tick数据，计算股票日成交量相对于价格的分布；

# 借此判断出股票是放量下跌还是有承接的放量；

Mon 2018/6/4

@author: Tracy Zhu
"""
# 导入系统库
import sys
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *
from stock_high_frequency_analysis.stock_lee_ready_algorithm import *

trading_day_list = get_trading_day_list()
out_picture_folder = "..\\stock_high_frequency_analysis\\picture\\"


def calc_volume_distribution_based_price(stock_code, trading_day):
    """
    根据tick数据计算出成交量对应与股价的分布
    :param stock_code:
    :param trading_day:
    :return:
    """
    price_volume_distribution = Series()
    price_volume_dict = defaultdict(int)
    stock_df = read_stock_tick_data_qian(stock_code, trading_day)
    if len(stock_df) > 100:
        stock_df = drop_duplicate_index(stock_df)
        tick_match_volume_series = stock_df.volume.diff()
        for index in stock_df.index:
            last_price = stock_df['last'][index]
            tick_match_volume = tick_match_volume_series[index]
            price_volume_dict[last_price] += tick_match_volume
        price_volume_distribution = Series(price_volume_dict)
        price_volume_distribution = price_volume_distribution.sort_index()
        price_volume_distribution.plot()
    return price_volume_distribution


def calc_volume_distribution_based_price_days(stock_code, trading_day, back_period):
    """
    将过去一段时间，用tick数据计算出的成交量分布，和上面函数不同的是，上面函数只计算一天；
    :param stock_code:
    :param trading_day:
    :param back_period:回看的日期
    :return:
    """
    stock_df = DataFrame()
    price_volume_distribution = Series()
    price_volume_dict = defaultdict(int)
    pre_trading_day = get_next_trading_day_stock(trading_day, -1 * back_period)
    for trade_day in trading_day_list:
        trade_day = trade_day[:-1]
        stock_trading_day = change_trading_day_format(trade_day)
        if pre_trading_day <= stock_trading_day <= trading_day:
            temp_df = read_stock_tick_data_qian(stock_code, stock_trading_day)
            stock_df = pd.concat([stock_df, temp_df], axis=0)
    if len(stock_df) > 100:
        stock_df = drop_duplicate_index(stock_df)
        tick_match_volume_series = stock_df.volume.diff()
        for index in stock_df.index:
            last_price = stock_df['last'][index]
            tick_match_volume = tick_match_volume_series[index]
            if tick_match_volume > 0:
                price_volume_dict[last_price] += tick_match_volume
        price_volume_distribution = Series(price_volume_dict)
        price_volume_distribution = price_volume_distribution.sort_index()
        price_volume_distribution.plot()
    return price_volume_distribution


def calc_active_buy_distribution_based_price(stock_code, trading_day):
    """
    根据tick数据计算出主动买成交额，随着价格的分布，如果价格越低，主动成交买额占比越大，则代表该股票承接力量比较强
    :param stock_code:
    :param trading_day:
    :return:
    """
    price_volume_distribution = Series()
    buy_ratio_distribution = Series()
    price_volume_dict = defaultdict(int)
    stock_df = read_stock_tick_data_qian(stock_code, trading_day)
    if len(stock_df) > 100:
        stock_df = drop_duplicate_index(stock_df)
        active_buy_series, active_buy_ratio_series = get_active_buy_series(stock_code, trading_day)
        for index in stock_df.index:
            last_price = stock_df['last'][index]
            active_buy_money = active_buy_ratio_series[index]
            price_volume_dict[last_price] += active_buy_money
        price_volume_distribution = Series(price_volume_dict)
        buy_ratio_distribution = price_volume_distribution.sort_index()

        for index in stock_df.index:
            last_price = stock_df['last'][index]
            active_buy_money = active_buy_series[index]
            price_volume_dict[last_price] += active_buy_money
        price_volume_distribution = Series(price_volume_dict)
        price_volume_distribution = price_volume_distribution.sort_index()
    return price_volume_distribution, buy_ratio_distribution


def plot_price_distribution(stock_code, trading_day):
    """
    将price_volume_distribution, buy_ratio_distribution的图形实例化出来；
    :param price_volume_distribution:
    :param buy_ratio_distribution:
    :return:
    """
    price_volume_distribution, buy_ratio_distribution = calc_active_buy_distribution_based_price(stock_code, trading_day)
    out_file_folder = out_picture_folder + trading_day + "\\"
    isExists = os.path.exists(out_file_folder)
    if not isExists:
        os.makedirs(out_file_folder)
    fig, ax = plt.subplots(figsize=(23.2, 14.0))
    ax.plot(buy_ratio_distribution, color='r', label='active buy ratio distribution based on price')
    ax.legend(loc='best')
    title = "active buy ratio distribution based on price"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + stock_code.split('.')[0] + ".png"
    plt.savefig(out_file_name)
    plt.close()

    fig, ax = plt.subplots(figsize=(23.2, 14.0))
    ax.plot(price_volume_distribution, color='r', label='active buy money distribution based on price')
    ax.legend(loc='best')
    title = "active buy money distribution based on price"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + stock_code.split('.')[0] + "_active_buy_money.png"
    plt.savefig(out_file_name)
    plt.close()


def calc_third_volume_ratio(price_distribution):
    """
    根据上面一个函数计算的price_volume_distribution,计算当日的最下的三分之一的价格的成交量，
    和最上面三分之一的价格的成交量，找出在价格下方有很多承接的股票（也可能是往下突破了价格抛的人变多呢？——2018.5.29 片仔癀）
    低价格的主动承接量高于高价格的，是不是有人正好逢低吸筹；
    :param price_volume_distribution:
    :return:
    """
    compare_ratio = 0
    quote_num = len(price_distribution) / 3
    low_price_sum = price_distribution.head(quote_num).sum()
    high_price_sum = price_distribution.tail(quote_num).sum()
    if high_price_sum != 0:
        compare_ratio = float(low_price_sum) / float(high_price_sum)
    return compare_ratio


def sort_stock_by_third_volume_ratio(trading_day):
    """
    按照上一个函数计算的third_volume_ratio, 然后将此因素按照从高到低排序
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
            price_volume_distribution, active_buy_ratio_distribution = calc_active_buy_distribution_based_price(stock_code, trading_day)
            compare_ratio = calc_third_volume_ratio(active_buy_ratio_distribution)
            active_buy_stock_dict[stock_code] = compare_ratio
    active_buy_stock_series = Series(active_buy_stock_dict)
    sort_active_buy_stock = active_buy_stock_series.sort_values(ascending=False)
    return sort_active_buy_stock


if __name__ == '__main__':
    stock_code = "000860.SZ"
    trading_day = '2018-05-29'
    # price_volume_distribution = calc_volume_distribution_based_price(stock_code, trading_day)
    print stock_code, trading_day
    # price_volume_distribution, active_buy_distribution = calc_active_buy_distribution_based_price(stock_code, trading_day)
    plot_price_distribution(stock_code, trading_day)
    # sort_active_buy_stock = sort_stock_by_third_volume_ratio(trading_day)
    # sort_active_buy_stock.to_csv("third_volume_ratio_stock.csv")
    # print sort_active_buy_stock.head(10)