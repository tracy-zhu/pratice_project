# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 14:46:11 2016

该脚本用来运行开盘之后价差是否会回归

@author: Tracy Zhu
"""

import os, sys

import pandas as pd
from pandas import DataFrame, Series

import logging

import xml.dom.minidom

import matplotlib.pyplot as plt

from datetime import datetime

os.chdir("F:\\python_project_Bid_Ask\\")
# 导入用户库
sys.path.append("..")
from python_base.common_method import *

# 日志文件
log_file_name = "Contract_Spread_analyse.log"

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    filename=log_file_name,
                    filemode='w')

# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# 全局变量
g_tick_qoute_file_root_folder = "Z:\\"
g_tick_columns = ['Instrument_ID', 'Update_Time', 'Update_Millisec', 'Trading_Day', 'Pre_Settlement_Price',
                  'Pre_Close_Price', 'Pre_Open_Interest', 'Pre_Delta', 'Open_Price', 'Highest_Price', 'Lowest_Price',
                  'Close_Price', 'Upper_Limit_Price', 'Lower_Limit_Price', 'Settlement_Price', 'Curr_Delta',
                  'Life_High', 'Life_Low', 'Last_Price', 'Last_Match_Volume', 'Turnover', 'Total_Match_Volume',
                  'Open_Interest', 'Interest_Change', 'Average_Price', 'Bid_Price1', 'Bid_Volume1', 'Ask_Price1',
                  'Ask_Volume1', 'Exchange_ID']
g_trade_phase_folder = "F:\\python_project_contract_spread\\trade_phase"
trade_phase_file_name = "F:\\python_project_contract_spread\\trade_phase\\20160503-99999999_trade_phase.xml"
g_dom = xml.dom.minidom.parse(trade_phase_file_name)
out_file_folder = "C:\\Users\\Tracy Zhu\\Desktop\\tool\\error_in_rob_order\\picture\\"


def get_spread_array_map(variety_id, trading_day, tick_num):
    instrument_file_list = get_instrument_file_list(str(trading_day))
    instrument_list = instrument_file_list[variety_id]
    main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
    first_file_name = g_tick_qoute_file_root_folder + "\\" + str(trading_day) + "\\" + main_instrument_id + ".csv"
    second_file_name = g_tick_qoute_file_root_folder + "\\" + str(trading_day) + "\\" + sub_instrument_id + ".csv"
    first_instrument = first_file_name.split('\\')[-1].split('.')[0]
    second_instrument = second_file_name.split('\\')[-1].split('.')[0]
    data_first = pd.read_csv(first_file_name, header=0, names=g_tick_columns, index_col=False)
    data_second = pd.read_csv(second_file_name, header=0, names=g_tick_columns, index_col=False)
    df_first = get_dataframe(data_first, g_tick_columns)
    df_second = get_dataframe(data_second, g_tick_columns)
    spread_array_last = df_first.Last_Price - df_second.Last_Price
    spread_array = spread_array_last[spread_array_last.index.hour >= 20].head(tick_num)
    last_spread_array = df_first.Pre_Close_Price - df_second.Pre_Close_Price
    last_spread = last_spread_array[spread_array_last.index.hour >= 20].head(tick_num)
    fig = plt.figure()
    fig.set_size_inches(23.2, 14.0)
    ax = fig.add_subplot(1, 1, 1)
    out_title = 'Contract Spread array of ' + first_instrument + '&' + second_instrument + ' in ' + str(trading_day)
    ax.set_title(out_title)
    ax.plot(spread_array, color='b', label='spread_array', linewidth=2)
    ax.plot(last_spread, color='r', label='last_spread', linewidth=2)
    ax.legend(loc='upper left')
    path_name = out_file_folder + str(trading_day)
    isExists = os.path.exists(path_name)
    if not isExists:
        os.makedirs(path_name)
    out_file_name = path_name + '\\' + first_instrument + '&' + second_instrument + ' in ' + str(
        trading_day) + '60s.png'
    plt.savefig(out_file_name)


def get_spread_array_map_by_instrument(first_instrument, second_instrument, trading_day, tick_num, end_time):
    first_file_name = g_tick_qoute_file_root_folder + "\\" + str(trading_day) + "\\" + first_instrument + ".csv"
    second_file_name = g_tick_qoute_file_root_folder + "\\" + str(trading_day) + "\\" + second_instrument + ".csv"
    data_first = pd.read_csv(first_file_name, header=0, names=g_tick_columns, index_col=False)
    data_second = pd.read_csv(second_file_name, header=0, names=g_tick_columns, index_col=False)
    df_first = get_dataframe(data_first, '1s')
    df_second = get_dataframe(data_second, '1s')
    df_first_filter = get_data_frame_slice(df_first, end_time)
    df_second_filter = get_data_frame_slice(df_second, end_time)
    buy_spread_array_last = df_first_filter.Ask_Price1 - df_second_filter.Bid_Price1
    buy_spread_array = buy_spread_array_last.head(tick_num)
    sell_spread_array_last = df_first.Bid_Price1 - df_second.Ask_Price1
    sell_spread_array = sell_spread_array_last.head(tick_num)

    fig = plt.figure()
    fig.set_size_inches(23.2, 14.0)
    ax = fig.add_subplot(1, 1, 1)
    out_title = 'Contract Spread array of ' + first_instrument + '&' + second_instrument + ' in ' + str(trading_day)
    ax.set_title(out_title)
    ax.plot(buy_spread_array, color='b', label='ask_spread_array', linewidth=2)
    ax.plot(sell_spread_array, color='r', label='bid_spread_array', linewidth=2)
    ax.legend(loc='upper left')
    path_name = out_file_folder + str(trading_day)
    isExists = os.path.exists(path_name)
    if not isExists:
        os.makedirs(path_name)
    out_file_name = path_name + '\\' + first_instrument + '&' + second_instrument + ' in ' + str(
        trading_day) + '60s.png'
    plt.savefig(out_file_name)

# 得到晚上收盘至早上开盘一段时间的dataframe
def get_data_frame_slice(df, end_time):
    end_time_list = end_time.split(":")
    end_hour = int(end_time_list[0])
    end_minute = int(end_time_list[1])
    df_filter_mor = df[df.index >= datetime(1900,1,1,9,0,0)]
    df_filter_end = df[df.index == datetime(1900,1,1, end_hour, end_minute, 0)]
    df_filter = pd.concat([df_filter_end, df_filter_mor])
    return df_filter

def main():
    first_instrument = 'RB1710'
    second_instrument = 'RB1705'
    end_time = '23:00:00'
    trading_day = 20170327
    tick_num = 60
    get_spread_array_map_by_instrument(first_instrument, second_instrument, trading_day, tick_num, end_time)


if __name__ == '__main__':
    main()
