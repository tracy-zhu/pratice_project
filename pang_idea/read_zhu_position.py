# -*- coding: utf-8 -*-
"""

# 读取中融期货朱总每日的持仓

# 每天总共有三个时间段，早盘，午盘, 夜盘

Tue 2017/07/27

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from python_base.plot_method import *

now = datetime.now()
trading_day = now.strftime('%Y%m%d')

file_name = "E:\\quote_data\\zhu_position\\" + trading_day + "\\position 20170727.csv"
f = open(file_name, 'r')
lines = f.readlines()
for one_line in lines:
    line_list = one_line.split(',')
    trading_day = line_list[0].split(':')[0]
    period_num = line_list[0].split(':')[1]
    instrument_id = line_list[1]
    position_num = line_list[2]
    print trading_day, period_num, instrument_id, position_num

