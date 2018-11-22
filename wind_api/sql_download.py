# -*- coding: utf-8 -*-
"""

# 从数据库中导入股票的数据

@author: Tracy Zhu
"""
from WindPy import w

import sys

import MySQLdb

# 导入用户库：
sys.path.append("..")
from wind_api.wind_download import *
trading_day_list = get_trading_day_list()


def connect_data_source():
    conn = MySQLdb.connect(host="192.168.1.205",
                           user="stock",
                           passwd="112233",
                           db="stock_db",
                           port=3308,
                           )
    return conn


def transfer_trading_day_format(raw_format):
    """
    函数将原有的日期格式，Y%m%d%, 转化成Y%-m%-d%
    :param raw_format:
    :return:
    """
    trading_date = raw_format[:4] + "-" + raw_format[4:6] + "-" + raw_format[6:8]
    return trading_date


def get_turnover_rate(conn, trading_day):
    """
    获取指定交易日的所有A股的换手率数据
    获取整个A股的收益率，按照所有A股的中位数取收益率
    单位为%
    :param trading_day:
    :return:
    """
    turnover_rate_list = []
    cur = conn.cursor()
    trading_date = trading_day[:4] + "-" + trading_day[4:6] + "-" + trading_day[6:8]
    sql_sentence = "select FREE_TURN from daily_price_tb where time=\"{trading_day}\"".format(trading_day=trading_date)
    cur.execute(sql_sentence)
    data = cur.fetchall()
    for turnover_rate in data:
        rate_value = turnover_rate[0]
        if rate_value > 0:
            turnover_rate_list.append(rate_value)
    turnover_rate_series = Series(turnover_rate_list)
    median_turnover_rate = turnover_rate_series.median()
    return median_turnover_rate


def turnover_rate_and_total_match_volume(conn, start_date, end_date, out_file_folder):
    """
    该函数从wind上下载A股的日总成交量序列（亿股）
    从数据库中取每天的换手率中位数序列（%）
    然后绘成许总要求的图
    :param conn:
    :param start_date: Y%m%d%
    :param end_date: Y%m%d%
    :return:
    """
    start_day = transfer_trading_day_format(start_date)
    end_day = transfer_trading_day_format(end_date)
    total_match_volume = total_match_volume_a_share_market(start_day, end_day)
    turnover_rate_a_share_list = []
    for trade_day in total_match_volume.index:
        trading_day = trade_day.strftime("%Y%m%d")
        print (trading_day)
        turnover_rate = get_turnover_rate(conn, trading_day)
        turnover_rate_a_share_list.append(turnover_rate)
    turnover_rate_series = Series(turnover_rate_a_share_list, index=total_match_volume.index)
    fig, ax = plt.subplots()
    ax.plot(total_match_volume, color='r', label="total match volume a share market")
    # ax.plot(raw_df[var_list[1]], color='c', label="Italy 10Y bond")
    ax1 = ax.twinx()
    ax1.plot(turnover_rate_series, color="b", label="turnover rate a share market")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "total match volume and turnover_rate in A share market"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def Italy_CDS_and_10y_bond(start_date, end_date):
    """
    从wind中下载意大利10年期国债
    从数据库中下载意大利5年CDS指数数据
    :param start_date:
    :param end_date:
    :param con:
    :return:
    """
    conn = MySQLdb.connect(host="192.168.1.205",
                           user="stock",
                           passwd="112233",
                           db="macro_db",
                           port=3308,
                           )
    italy_bond = download_data_wind(start_date, end_date, "G1700020")
    sql_sentence = "select time, ITALY_CDS_USD_SR_5Y_D14_Corp from bl_tb"
    cur = conn.cursor()
    cur.execute(sql_sentence)
    data = cur.fetchall()
    cds_list = []
    date_time_list = []
    for select_value in data:
        date_time = select_value[0]
        trading_day = date_time.strftime("%Y%m%d")
        if trading_day >= start_date and select_value[1] > 0:
            cds_list.append(select_value[1])
            date_time_list.append(date_time)
    cds_series = Series(cds_list, index=date_time_list)
    fig, ax = plt.subplots()
    ax.plot(italy_bond, color='r', label="Italy national bond 10 year")
    # ax.plot(raw_df[var_list[1]], color='c', label="Italy 10Y bond")
    ax1 = ax.twinx()
    ax1.plot(cds_series, color="b", label="CDS index 5 year in Italy")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "Italy national bond 10 year and CDS index 5 year"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def european_financial_condition(start_date, end_date):
    """
    欧洲金融条件：欧元兑美元汇率[G0002331]
    投资级以下企业5年期CDS指数:数据库中没有，由意大利的5年CDS指数代替
    从数据库中下载意大利5年CDS指数数据
    :param start_date:
    :param end_date:
    :return:
    """
    conn = MySQLdb.connect(host="192.168.1.205",
                           user="stock",
                           passwd="112233",
                           db="macro_db",
                           port=3308,
                           )
    eur_usd = download_data_wind(start_date, end_date, "G0002331")
    sql_sentence = "select time, ITALY_CDS_USD_SR_5Y_D14_Corp from bl_tb"
    cur = conn.cursor()
    cur.execute(sql_sentence)
    data = cur.fetchall()
    cds_list = []
    date_time_list = []
    for select_value in data:
        date_time = select_value[0]
        trading_day = date_time.strftime("%Y%m%d")
        if trading_day >= start_date and select_value[1] > 0:
            cds_list.append(select_value[1])
            date_time_list.append(date_time)
    cds_series = Series(cds_list, index=date_time_list)
    fig, ax = plt.subplots()
    ax.plot(eur_usd, color='r', label="EURUSD")
    ax1 = ax.twinx()
    ax1.plot(cds_series, color="b", label="CDS index 5 year in Italy")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "EUR_USD　and CDS index 5 year"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)



if __name__ == '__main__':
    start_date = "20170901"
    end_date = "20180304"
    conn = connect_data_source()
    turnover_rate_and_total_match_volume(conn, start_date, end_date, out_file_folder)
