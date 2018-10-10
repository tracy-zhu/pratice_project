# -*- coding: utf-8 -*-
"""

# 脚本计算美股跌一定幅度，中国3个指数的
    沪深300， 中证500， 上证50的开盘涨幅，收盘涨幅等因素;

# 美股是道琼斯指数的涨幅

Tue 2018/02/06

@author: Tracy Zhu
"""
# 导入系统库
import sys
from WindPy import w
import datetime as dt
import pandas as pd
from pandas import Series
import matplotlib.pyplot as plt
import MySQLdb

# 导入用户库：
sys.path.append("..")

if w.isconnected() == False:
    w.start()


def connect_data_source():
    conn = MySQLdb.connect(host="192.168.1.205",
                           user="stock",
                           passwd="112233",
                           db="daily_market_ths_db",
                           port=3308,
                           )
    return conn


def find_condition_date_usa(start_date, end_date, condition_num):
    """
    查询指定日期，美股收盘涨跌超过一定幅度的日期数；
    :param start_date:
    :param end_date:
    :param condition_num: 涨跌幅的条件值，一般为涨跌幅度
    :return: 返回的是1个data_frame, index为日期，分别是收盘价和涨跌幅
    """
    start_date = '2002-01-04'
    end_date = '2018-03-26'
    condition_num = 0.028

    us_idx = 'SPX.GI'
    # us_idx = 'DJC.GI'
    us_raw = w.wsd(us_idx, "close,pct_chg", start_date, end_date, "TradingCalendar=NYSE")
    us_data = pd.DataFrame(us_raw.Data, index=us_raw.Fields, columns=us_raw.Times).T
    us_data.PCT_CHG /= 100

    doom_data = us_data.loc[us_data.PCT_CHG > condition_num, :].copy()
    return doom_data


def find_condition_data_usa_two(start_date, end_date, condition_num, conn):
    start_date = '2002-01-04'
    end_date = '2018-02-05'
    index_code = "spx_gi_tb"
    cur = conn.cursor()
    sql_sentence = "select time,open,close from {index_code} where time >= \"{pre_trading_day}\" and time <= \"{next_trading_day}\"". \
        format(index_code=index_code,pre_trading_day=start_date,next_trading_day=end_date)
    cur.execute(sql_sentence)
    data = cur.fetchall()
    select_date_time_list = []
    for market_price in data:
        per_change = float(market_price[2]) / float(market_price[1]) - 1
        if per_change > condition_num:
            select_date_time_list.append(market_price[0])



def trading_day_state_wind(index_code, selected_date):
    """
    从wind上下载数据
    """
    pass


def trading_day_state(index_code, selected_date, conn):
    """
    给定指数和美股条件筛选出的日期，确定出该指数的情况，包括开盘幅度，和收盘相对于开盘涨跌幅度
    :param index_code: 指数代码，沪深300[000300_sh_tb] 中证500[000905_sh_tb] 上证50[000016_sh_tb]
    :param selected_date: 根据美股选出的日期，格式为datetime.date格式
    :return:
    """
    index_code = "000300_sh_tb"
    cur = conn.cursor()
    pre_trading_day = selected_date.strftime("%Y-%m-%d")
    next_10_day = selected_date + dt.timedelta(days=10)
    next_day_str = next_10_day.strftime("%Y-%m-%d")
    sql_sentence = "select time,open,close from {index_code} where time >= \"{pre_trading_day}\" and time <= \"{next_trading_day}\"".\
        format(index_code=index_code,pre_trading_day=pre_trading_day,next_trading_day=next_day_str)
    cur.execute(sql_sentence)
    data = cur.fetchall()
    pre_close_price = data[0][2]
    open_price = data[1][1]
    close_price = data[1][2]
    open_price_change = float(open_price) / float(pre_close_price) - 1
    day_price_change = float(close_price) / float(open_price) - 1
    return open_price_change, day_price_change


def condition_stat(start_date, end_date, index_code, condition_num):
    """
    给定指定日期和美股变化的条件值，index_code为国内股市的指定变化
    """
    conn = connect_data_source()
    doom_data = find_condition_date_usa(start_date, end_date, condition_num)
    select_date_time_list = doom_data.index
    open_price_change_list = []
    day_price_change_list = []
    for selected_date in select_date_time_list:
        open_price_change, day_price_change = trading_day_state(index_code, selected_date, conn)
        open_price_change_list.append(open_price_change)
        day_price_change_list.append(day_price_change)
    open_price_change_series = Series(open_price_change_list)
    day_price_change_series = Series(day_price_change_list)
    open_price_change_series.hist()
    day_price_change_series.hist()
    print open_price_change_series.describe()
    print day_price_change_series.describe()
    print sum(day_price_change_series>0)
    return open_price_change_series, day_price_change_series


if __name__ == '__main__':
    start_date = '2002-01-04'
    end_date = '2018-03-26'
    index_code = "000300_sh_tb"
    condition_num = 0.028
    condition_stat(start_date, end_date, index_code, condition_num)

