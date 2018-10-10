# -*- coding: utf-8 -*-
# """ This script is used for get contract of different instruments get close price by day Created on Mon Jun 27 09:02:46 2016 @author: Tracy Zhu """

import logging
import xml.dom.minidom

import matplotlib.pyplot as plt

from python_base.constant import *
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
# formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# 全局变量
g_tick_qoute_file_root_folder = "\\\\192.168.1.203\\quote_server_bak\\Quote_Data\\Tick_Quote"
g_tick_columns = ['Instrument_ID', 'Update_Time', 'Update_Millisec', 'Trading_Day', 'Pre_Settlement_Price',
                  'Pre_Close_Price', 'Pre_Open_Interest', 'Pre_Delta', 'Open_Price', 'Highest_Price', 'Lowest_Price',
                  'Close_Price', 'Upper_Limit_Price', 'Lower_Limit_Price', 'Settlement_Price', 'Curr_Delta',
                  'Life_High', 'Life_Low', 'Last_Price', 'Last_Match_Volume', 'Turnover', 'Total_Match_Volume',
                  'Open_Interest', 'Interest_Change', 'Average_Price', 'Bid_Price1', 'Bid_Volume1', 'Ask_Price1',
                  'Ask_Volume1', 'Exchange_ID']
g_trade_phase_folder = "F:\\python_project_contract_spread\\trade_phase"
trade_phase_file_name = "F:\\python_project_contract_spread\\trade_phase\\20160503-99999999_trade_phase.xml"
g_dom = xml.dom.minidom.parse(trade_phase_file_name)
variety_id = 'RB'
out_file_folder = "F:\\IC_Contract_Spread\\close_spread_array\\"
trading_day_list = get_trading_day_list()


def get_trade_phase(trading_day):
    global g_trade_phase_folder
    for dirpath, dirnames, filenames in os.walk(g_trade_phase_folder):
        for name in filenames:
            if int(name[0:8]) <= trading_day <= int(name[9:17]):
                trade_phase_file = g_trade_phase_folder + "\\" + name
                return trade_phase_file


def get_opentime(variety_id, trade_phase_file):
    dom = xml.dom.minidom.parse(trade_phase_file)
    root = dom.documentElement
    itemlist = root.getElementsByTagName('VarietyPhase')
    for item in itemlist:
        if variety_id[1:-1] == item.getAttribute("varietyid").encode("gbk"):
            open_time = item.getAttribute("opentime").encode("gbk")
            return open_time


# 得到每个合约的价值序列
def get_close_price_list(instrument_id, begin_trading_day):
    close_price_list = []
    close_price_arr = None
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day >= begin_trading_day:
            close_price = get_close_price(instrument_id, trading_day)
            close_price_list.append(close_price)
            close_price_arr = np.array(close_price_list)
    return close_price_arr


def get_tick(variety_id):
    global g_dom
    root = g_dom.documentElement
    itemlist = root.getElementsByTagName('VarietyPhase')
    for item in itemlist:
        if variety_id[1:-1] == item.getAttribute("varietyid").encode("gbk"):
            tick = float(item.getAttribute("tick").encode("gbk"))
            return tick


def get_spread_array_map(main_instrument_id, sub_instrument_id, trading_day):
    main_close_price_arr = get_close_price_list(main_instrument_id, trading_day)
    sub_close_price_arr = get_close_price_list(sub_instrument_id, trading_day)
    close_price_spread_array = main_close_price_arr - sub_close_price_arr
    fig = plt.figure()
    fig.set_size_inches(23.2, 14.0)
    ax = fig.add_subplot(1, 1, 1)
    png_title = 'Contract Spread array of ' + main_instrument_id + ' & ' + sub_instrument_id
    ax.set_title(png_title)
    ax.plot(close_price_spread_array, 'b')
    plt.legend(["close_price_spread"], loc='best')
    out_file_name = out_file_folder + str(trading_day) + '.png'
    plt.savefig(out_file_name)


def main():
    main_instrument_id = 'RB1705'
    sub_instrument_id = 'RB1710'
    begin_day = '20161025'
    get_spread_array_map(main_instrument_id, sub_instrument_id, begin_day)


if __name__ == '__main__':
    main()

