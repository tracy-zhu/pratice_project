# -*- coding: utf-8 -*-
"""

# 根据前面得到涨停板相关性最高的几只股票，输出标的股票，将相关的股票筛选出来


Mon 2018/4/16

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math
from collections import Counter

# 导入用户库：
sys.path.append("..")
from stock_base.stock_file_api import *

key_stock = '603711.SH'


out_file_name = '..\\stock_tool\\result\\up_limit_correlation.txt'
f = open(out_file_name, 'r')
str_lines = f.readlines()


for str_line in str_lines:
    first_stock_code = str_line.split(',')[0]
    if first_stock_code == key_stock:
        print str_line
        break

