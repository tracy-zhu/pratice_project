# -*- coding: utf-8 -*-
"""

# 用于读取期权数据等基础函数

@author: hp
"""


import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *

option_file_folder = "V:\\snapdata_fo_ths\\"


def filter_option_file(trading_day):
    """
    将当天所有期权文件的文件名筛选出来
    :param trading_day: '2018-07-09
    :return:
    """
    file_name_list = []
    option_file_path = option_file_folder + trading_day
    for filenames in os.listdir(option_file_path):
        option_num = filenames.split("_")[0]
        if len(option_num) == 8 and option_num[0] == '1':
            file_name_list.append(filenames)
    return file_name_list


def get_option_chi_name(trading_day):
    """
    获取一天中所有期权的中文名称
    :param option_code:
    :param trading_day:
    :return:
    """
    sql = 'SELECT * FROM stock_db.50etf_option_code_name where date = \"' + trading_day + '\"'

    tp_table = fetchall_sql(sql)
    option_chi_df = pd.DataFrame(list(tp_table))
    option_chi_df.columns = retrieve_column_name('stock_db', '50etf_option_code_name')
    return option_chi_df


def get_option_attribute(trading_day, file_name_list):
    """
    获取当天所有的期权名称，并且判断是看涨还是看跌期权
    :param trading_day:
    :return:
    """
    option_attribute_dict = defaultdict()
    direction_attribute = None
    option_chi_df = get_option_chi_name(trading_day)
    for file_name in file_name_list:
        option_num = file_name.split('_')[0] + '.SH'
        sec_name = option_chi_df[option_chi_df['wind_code']==option_num].sec_name.values[0]
        if sec_name[5:8] ==  '\xe8\xb4\xad':
            "认购期权"
            direction_attribute = "call"
        elif sec_name[5:8] == '\xe6\xb2\xbd':
            "认沽期权"
            direction_attribute = 'put'
        option_attribute_dict[file_name] = direction_attribute
    return option_attribute_dict


def read_option_data(file_name):
    """
    读取期权文件的高频数据，获取最后一行的收盘数据，收盘价格，持仓量大小，成交量大小；
    :param file_name:
    :return:
    """
    result_list = None
    folder_file_name = option_file_folder + file_name
    f = open(folder_file_name, 'r')
    readlines = f.readlines()
    last_line = readlines[-1]
    last_list = last_line.split(',')
    if len(last_list) >= 6:
        close = float(last_list[5])
        volume = float(last_list[8])
        amount = float(last_list[9])
        position = float(last_list[13])
        result_list = [close, volume, amount, position]
    return result_list


def read_option_data_daily(trading_day):
    """
    读取所有期权的日线数据，包含了开高低收，成交量持仓量，隐含波动率，历史波动率等指标
    :param file_name:
    :return:
    """
    sql = 'SELECT * FROM stock_db.daily_50etf_option_price_tb where time = \"' + trading_day + '\"'

    tp_table = fetchall_sql(sql)
    option_daily_df = pd.DataFrame(list(tp_table))
    option_daily_df.columns = retrieve_column_name('stock_db', 'daily_50etf_option_price_tb')
    return option_daily_df


def read_option_data_daily_ths(trading_day):
    """
    从同花顺的数据库生成的表中，读取期权的日线数据
    :param trading_day:
    :return:
    """
    sql = 'SELECT * FROM stock_db.daily_50etf_option_price_ths_tb where time = \"' + trading_day + '\"'

    tp_table = fetchall_sql(sql)
    option_daily_df = pd.DataFrame(list(tp_table))
    option_daily_df.columns = retrieve_column_name('stock_db', 'daily_50etf_option_price_ths_tb')
    return option_daily_df


def read_option_tick_data_ths(file_name):
    """
    读取期权的tick数据，同花顺目录中
    :param file_name:
    :return:
    """
    open_time = '09:25:00'
    trading_day = file_name.split('.')[-2].split("_")[-1]
    file_path = option_tick_file_path_ths + trading_day + '\\' + file_name
    tick_data = pd.read_csv(file_path)
    trade_tick = tick_data[tick_data.tradeTime >= open_time]
    trade_tick = trade_tick.sort_values(by='tradeTime')
    open_price = trade_tick.latest.values[0]
    spot_time = '09:30:00'
    open_tick = trade_tick[trade_tick.tradeTime >= spot_time]
    return open_price, open_tick


