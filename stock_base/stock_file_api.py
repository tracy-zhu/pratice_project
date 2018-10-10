# -*- coding: utf-8 -*-
"""

# 股票数据的api,非数据库，主要从文件目录读入

# 数据格式分为两种，王仔和钱哥的

Tue 2018/03/20

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *


def read_real_time_stock_data_wind(trading_day, spot_time):
    """
    根据钱哥从wind上下载的实时数据，读取某天某个时间段的数据
    :param stock_code: 300597.SZ (str)
    :param trading_day: '2018-03-22' (str)
    :param spot_time:6位数字，不足6位最后加个. , 93124. (int)
    :return:
    """
    time_spot = None
    data_file_folder = wind_rt_data_path + trading_day
    file_names_list = os.listdir(data_file_folder)
    time_list = []
    for file_name in file_names_list:
        time_spot = int(file_name.split('.')[0])
        time_list.append(time_spot)
    time_list.sort()

    for time_spot in time_list:
        if time_spot >= spot_time:
            break

    spot_str = str(time_spot) if len(str(time_spot)) == 6 else (str(time_spot) + '.')
    data_file_name = data_file_folder + "\\" + spot_str + '.csv'
    slice_df = pd.read_csv(data_file_name)
    slice_df.columns = rt_data_columns
    return slice_df


def get_stock_slice_data(stock_code, slice_df):
    """
    获取某只股票那个时点的切片数据
    :param stock_code:
    :param slice_df:
    :return:
    """
    stock_code_data = slice_df[slice_df.index_code == stock_code]
    return stock_code_data


def get_stock_slice_data_by_minute_data(stock_code, trading_day, spot_time):
    """
    根据钱哥分钟数据获取某个股票某个时间的价格，和相对与前一天的收益率
    :param stock_code: "600300.SZ'
    :param spot_time: '9:30'(str)
    :param trading_day: '2018-3-26'
    :return:
    """
    spot_yield = -999
    end_yield = -999
    end_price = -999
    end_time = "14:57"
    pre_trading_day = get_pre_trading_day_stock(trading_day)
    stock_df = read_stock_minute_data(stock_code, trading_day)
    pre_stock_df = read_stock_minute_data(stock_code, pre_trading_day)
    if len(stock_df) > 0 and len(pre_stock_df) > 0:
        begin_period = trading_day + ' ' + spot_time
        end_period = trading_day + ' ' + end_time
        select_df = stock_df[stock_df.time >= begin_period]
        select_df = select_df[select_df.time <= end_period]
        begin_price = select_df.close.values[0]
        end_price = select_df.close.values[-1]
        _, pre_close_price = get_stock_open_close_price(stock_code, pre_trading_day)
        spot_yield = float(begin_price) / float(pre_close_price) - 1
        end_yield = float(end_price) / float(pre_close_price) - 1
    return spot_yield, end_yield, end_price


def get_stock_open_close_price(stock_code, trading_day):
    """
    从钱哥的分钟数据中，得到当日股票的开盘和收盘价
    :param stock_code:
    :param trading_day: "2018-03-20"
    :return:
    """
    stock_df = read_stock_minute_data(stock_code, trading_day)
    open_price = stock_df.open.values[0]
    close_price = stock_df.close.values[-1]
    return open_price, close_price


def get_stock_period_yield_minute(stock_code, trading_day, begin_time, end_time):
    """
    从钱哥的分钟数据中读取某一段时间的收益率
    :param stock_code:
    :param trading_day: '2018-03-26'
    :param begin_time: '9:30'(str)
    :param end_time:'10:30' (str)
    :return:
    """
    stock_df = read_stock_minute_data(stock_code, trading_day)
    begin_period = trading_day + ' ' + begin_time
    end_period = trading_day + ' ' + end_time
    select_df = stock_df[stock_df.time >= begin_period]
    select_df = select_df[select_df.time <= end_period]
    begin_price = select_df.close.values[0]
    end_price = select_df.close.values[-1]
    period_yield = float(end_price) / float(begin_price) - 1
    return period_yield


def resample_minute_data(stock_code, trading_day, frequency):
    """
    读取分钟数据，并将分钟数据转化成为想要的频率
    :param stock_code:'600300.SZ'
    :param trading_day:"2018-04-13"
    :param frequency:'5min'
    :return:
    """
    resample_data = DataFrame()
    minute_df = read_stock_minute_data(stock_code, trading_day)
    if len(minute_df) > 0:
        time_index_list = get_time_index_stock(minute_df)
        minute_df.index = time_index_list
        resample_data = minute_df.resample(frequency).first()
        resample_data = resample_data.dropna(how='all')
    return resample_data


def get_time_index_stock(minute_df):
    """
    根据读取的minute_df，生成datetime格式的时间序列的index
    :param minute_df:
    :return:
    """
    time_index_list = []
    for time_index in minute_df.index:
        stamp = datetime.strptime(time_index, '%Y-%m-%d %H:%M')
        time_index_list.append(stamp)
    return time_index_list





if __name__ == '__main__':
    stock_code = '000830.SZ'
    trading_day = '2018-04-13'
    frequency = '5min'
