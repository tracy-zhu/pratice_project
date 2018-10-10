# -*- coding: utf-8 -*-
"""

# 找出间隔很久没有涨停，在早上涨停且后面没有打开的股票

WED 2018/03/14

@author: Tracy Zhu
"""

# 导入系统库
import sys
from WindPy import w


# 导入用户库
sys.path.append("..")
from stock_tool.up_limit_stock_num import *

file_path = "..\\stock_tool\\result\\high_grade_momentum_stock.txt"
out_file_path = "..\\stock_tool\\result\\high_grade_momentum_stock_new.txt"
f = open(file_path, 'r')
f_out = open(out_file_path, 'wb')
str_lines = f.readlines()

for line in str_lines[1:]:
    stock_code = line.split(',')[0]
    momentum_values = line.split(',')[1]
    chi_name = find_stock_chi_name(stock_code)
    print>>f_out, stock_code, ',', chi_name, ',', momentum_values

f.close()
f_out.close()
