# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 每天将分钟数据转换出来

@author: Tracy Zhu
"""

import os


TRADING_DAY_LIST_FILE_NAME = ' '
os.chdir("F:\\quot_tools")


def get_trading_day_list():
    trading_day_list_file = open(TRADING_DAY_LIST_FILE_NAME, "r")
    trading_day_list = trading_day_list_file.readlines()
    trading_day_list_file.close()
    return trading_day_list

trading_day_list = get_trading_day_list()

for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    command_line = "quote_tools_minute Z:\\" + trading_day + " E:\\quote_data\\1M_K 1"
    os.system(command_line)
