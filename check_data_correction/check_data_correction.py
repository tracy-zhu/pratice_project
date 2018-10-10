#  -*- coding: utf-8 -*-

# 该文件每天检查数据的完备性

# 导入系统库
import sys, string, os, copy, time, types
import numpy as np
import logging
from logging.handlers import RotatingFileHandler

# 导入用户库
sys.path.append("..")
from python_base.common_method import *
from os.path import getsize

# 日志文件
log_file_name = "limit_price_analyse.log"


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s  %(levelname)s %(message)s',
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
# g_tick_quote_file_root_folder = "\\\\192.168.1.203\\quote_server_bak\\Quote_Data\\Tick_Quote"
g_tick_quote_file_root_folder = "Z:\\"
G_VARIETY_LIST = ['RB', 'RM', "J", "IF"]

# 定义 环境变量
now = datetime.now()
trading_day = now.strftime('%Y%m%d')
# trading_day = '20160331'

# 按交易日，和品种，输出有数据缺失的合约
def judge_missing_data_variety(trading_day, variety_id, instrument_list):
    quote_map = {}
    for one_file_name in instrument_list:
        quote_file = open(one_file_name, "r")
        quote_list = quote_file.readlines()
        quote_file.close()
        instrument_id = one_file_name.split("\\")[-1].split(".")[0]
        close_quote = CBest_Market_Data_Field()
        if len(quote_list) > 3:
            if len(quote_list[-1]) > 10:
                close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-2])
            else:
                close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-3])
            quote_map[instrument_id] = close_quote

    # 寻找主力合约
    max_trade_volume = 0
    main_instrument_id = ""
    for (instrument_id, best_quote) in quote_map.items():
        if best_quote.Total_Match_Volume > max_trade_volume:
            max_trade_volume = best_quote.Total_Match_Volume
            main_instrument_id = instrument_id

    quote_data = read_data(main_instrument_id, trading_day)
    trade_phase_file = get_trade_phase(trading_day)
    main_file_name = g_tick_quote_file_root_folder + '\\' + trading_day + '\\' + main_instrument_id + '.csv'
    file_size = getsize(main_file_name) / 1024
    # print file_size
    # logging.debug('find id data missing for %s ', variety_id)
    # if len(quote_data) < 500 or file_size < 1000:
    missing_periods = judge_complete_data(quote_data,variety_id, trade_phase_file)
    if missing_periods > 0:
        print_line = variety_id + " data is missing!"
        print print_line
    else:
        print_line = variety_id + " data is correct ^-^"
        print print_line

# 根据文件名或合约名，获取品种ID
def Get_Variety_ID(instrument_name):
    variety_id = instrument_name[0]
    if "A" <= instrument_name[1] <= "Z":
        variety_id = variety_id + instrument_name[1]
    return variety_id

def judge_complete_data(quote_data, variety_id, trade_phase_file):
    missing_periods = 0
    zip_phase_time = get_phase_time(variety_id, trade_phase_file)
    update_time_list = quote_data.Update_Time
    update_time_array = np.array(update_time_list)
    for phase_time in zip_phase_time:
        begin_time = phase_time[0]
        end_time = phase_time[1]
        begin_array = update_time_array[update_time_array >= begin_time]
        slice_array = begin_array[begin_array <= end_time]
        if len(slice_array) < 500:
            missing_periods += 1
    return missing_periods

def find_missing_data(trading_day):
    global g_tick_quote_file_root_folder
    folder_path = g_tick_quote_file_root_folder + "\\" + trading_day
    if folder_path is None:
        raise Exception("folder_path is None")

    # 获取该交易日的文件列表
    instrument_file_list = {}
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for name in filenames:
            # print name
            if len(name) < 7 + 4:
                variety_id = Get_Variety_ID(name)
                if variety_id in G_VARIETY_LIST:
                    if instrument_file_list.has_key(variety_id):
                        pass
                    else:
                        instrument_file_list[variety_id] = []
                    instrument_file_list[variety_id].append(dirpath + '\\' + name)

    for (variety_id, instrument_list) in instrument_file_list.items():
        judge_missing_data_variety(trading_day, variety_id, instrument_list)


def main():
    find_missing_data(trading_day)

if __name__ == '__main__':
    main()
