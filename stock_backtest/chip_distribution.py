# -*- coding: utf-8 -*-
"""

# 主要计算出股票的某个价位的买盘力量；

# 找出该股票的安全区间，和普通的筹码分布不同，主要计算大盘下跌过程中的安全价位；

# 并且在过去几天中，成交量是放大的；

Mon 2018/04/23

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_data_task.find_hot_block import *
from stock_base.stock_file_api import *

picture_out_folder = ".\\stock_backtest\\picture\\"
trading_day_list = get_trading_day_list()


def get_chip_distribution(stock_code, trading_day):
    """
    获取某只股票当天价格的筹码分布
    :param stock_code: "601318.SH"
    :param trading_day: "2018-04-20"
    :return:
    """
    price_chip_dict = defaultdict()
    stock_df = read_stock_minute_data(stock_code, trading_day)
    for index in stock_df.index:
        close_price = stock_df.loc[index].close
        trade_volume = stock_df.loc[index].volume
        if not price_chip_dict.has_key(close_price):
            price_chip_dict[close_price] = trade_volume
        else:
            price_chip_dict[close_price] = price_chip_dict[close_price] + trade_volume
    price_chip_series = Series(price_chip_dict)
    price_chip_series = price_chip_series.dropna()
    return price_chip_series



if __name__ == '__main__':
    stock_code = '601318.SH'
    trading_day = '2018-04-19'